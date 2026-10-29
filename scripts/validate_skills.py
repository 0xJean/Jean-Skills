#!/usr/bin/env python3
"""Validate portable skills and local Markdown links without network access.

English checks are heuristics, not a translation or grammar audit. They inspect
rendered prose and YAML string values, excluding code and URLs. Language
classification needs at least eight words and forty letters; short labels and
ambiguous passages can therefore escape detection. Root README files may be
multilingual. HTTP availability is deliberately left to the separate link job.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

from github_slugger import GithubSlugger
from langdetect import DetectorFactory, LangDetectException, detect_langs
from markdown_it import MarkdownIt
from markdown_it.token import Token
import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


DetectorFactory.seed = 0
MARKDOWN = MarkdownIt("commonmark").enable(["table", "strikethrough"])
SKILL_FIELDS = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools"
}
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SCAFFOLD = re.compile(
    r"\[(?:(?:TODO|TBD|FIXME)(?::[^\]]*)?|(?:insert|add|describe|write|replace|your)\b[^\]]*)\]"
    r"|^\s*(?:TODO|TBD|FIXME)(?:\s*:\s*.*)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
WORDS = re.compile(r"[^\W\d_]+", re.UNICODE)
URLS = re.compile(r"(?:[a-z][a-z0-9+.-]*://|www\.)\S+|\b\S+@\S+\.\S+", re.I)
GREEK_SYMBOLS = frozenset("αβγδεζηθικλμνξοπρστυφχψωΓΔΘΛΞΠΣΥΦΨΩ")


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    message: str
    code: str


@dataclass
class Document:
    tokens: list[Token]
    anchors: set[str]
    prose: list[tuple[int, str]]
    links: list[tuple[int, str]]


class UniqueLoader(yaml.SafeLoader):
    """Safe YAML with duplicate fields rejected, including nested mappings."""


def _unique_mapping(loader: UniqueLoader, node: MappingNode, deep: bool = False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as error:
            raise yaml.constructor.ConstructorError(
                "while reading a mapping", node.start_mark,
                "mapping keys must be scalar values", key_node.start_mark,
            ) from error
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while reading a mapping", node.start_mark,
                f"duplicate field {key!r}", key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def _frontmatter(text: str) -> tuple[str, str, int] | None:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1:]), index + 1
    return None


def _inline_text(tokens: list[Token], *, code: bool = False) -> str:
    parts = []
    for token in tokens:
        if token.type == "text" or (code and token.type == "code_inline"):
            parts.append(token.content)
        elif token.type in {"softbreak", "hardbreak"}:
            parts.append("\n")
        elif token.type == "image":
            parts.append(_inline_text(token.children or [], code=code))
    return "".join(parts)


class _HTML(HTMLParser):
    """Read actual HTML tokens, never fenced or inline code examples."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str]] = []
        self.anchors: set[str] = set()
        self.prose: list[tuple[int, str]] = []
        self.code_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"code", "pre", "script", "style"}:
            self.code_depth += 1
        if self.code_depth:
            return
        values = dict(attrs)
        if values.get("id"):
            self.anchors.add(values["id"])
        if tag == "a" and values.get("name"):
            self.anchors.add(values["name"])
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.links.append((self.getpos()[0], values[attribute]))
        if tag == "img" and values.get("alt"):
            self.prose.append((self.getpos()[0], values["alt"]))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in {"code", "pre", "script", "style"} and self.code_depth:
            self.code_depth -= 1

    def handle_data(self, data):
        if not self.code_depth and data.strip():
            self.prose.append((self.getpos()[0], data))


def _parse_markdown(text: str) -> Document:
    tokens = MARKDOWN.parse(text)
    slugger = GithubSlugger()
    anchors: set[str] = set()
    prose: list[tuple[int, str]] = []
    links: list[tuple[int, str]] = []
    for index, token in enumerate(tokens):
        line = (token.map or [0])[0] + 1
        if token.type == "heading_open":
            anchors.add(slugger.slug(_inline_text(tokens[index + 1].children or [], code=True)))
        elif token.type == "inline":
            prose.append((line, _inline_text(token.children or [])))
            current_line = line
            for child in token.children or []:
                if child.type in {"link_open", "image"}:
                    target = child.attrGet("href" if child.type == "link_open" else "src")
                    if target is not None:
                        links.append((current_line, target))
                elif child.type == "html_inline":
                    html = _HTML()
                    html.feed(child.content)
                    anchors.update(html.anchors)
                    links.extend((current_line + n - 1, url) for n, url in html.links)
                if child.type in {"softbreak", "hardbreak"}:
                    current_line += 1
                else:
                    current_line += child.content.count("\n")
        elif token.type == "html_block":
            html = _HTML()
            html.feed(token.content)
            anchors.update(html.anchors)
            prose.extend((line + n - 1, value) for n, value in html.prose)
            links.extend((line + n - 1, url) for n, url in html.links)
    return Document(tokens, anchors, prose, links)


def _clean_prose(text: str) -> str:
    return re.sub(r"\s+", " ", URLS.sub(" ", text)).strip()


def _non_latin(text: str) -> str | None:
    for index, character in enumerate(text):
        if not unicodedata.category(character).startswith("L"):
            continue
        if "LATIN" in unicodedata.name(character, ""):
            continue
        # Isolated Greek variables are useful in English scientific prose.
        if character in GREEK_SYMBOLS:
            neighbors = text[max(0, index - 1):index] + text[index + 1:index + 2]
            if not any("GREEK" in unicodedata.name(c, "") for c in neighbors):
                continue
        return character
    return None


@lru_cache(maxsize=1024)
def _detected_language(text: str) -> str | None:
    words = WORDS.findall(text)
    if len(words) < 8 or sum(map(len, words)) < 40:
        return None
    try:
        languages = detect_langs(text)
    except LangDetectException:
        return None
    best = languages[0]
    return best.lang if best.lang != "en" and best.prob >= 0.90 else None


class _Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.issues: list[Issue] = []
        self.texts: dict[Path, str | None] = {}
        self.documents: dict[Path, Document | None] = {}

    def issue(self, path: Path, line: int, message: str, code: str):
        self.issues.append(Issue(path, max(1, line), message, code))

    def read(self, path: Path) -> str | None:
        if path not in self.texts:
            try:
                self.texts[path] = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as error:
                self.issue(path, 1, f"cannot read UTF-8 text: {error}", "FILE_READ")
                self.texts[path] = None
        return self.texts[path]

    def yaml(self, path: Path, text: str, offset: int = 0):
        loader = UniqueLoader(text)
        try:
            node = loader.get_single_node()
            data = loader.construct_document(node) if node is not None else None
            if not isinstance(data, dict):
                self.issue(path, offset + 1, "YAML must be a mapping", "YAML_MAPPING")
                return None
            return data, node
        except yaml.YAMLError as error:
            mark = getattr(error, "problem_mark", None)
            message = getattr(error, "problem", None) or str(error)
            self.issue(path, offset + (mark.line if mark else 0) + 1, message, "YAML_INVALID")
            return None
        finally:
            loader.dispose()

    @staticmethod
    def field_line(node: MappingNode, name: str, offset: int = 0) -> int:
        for key, _ in node.value:
            if key.value == name:
                return offset + key.start_mark.line + 1
        return offset + 1

    def language(self, path: Path, blocks: list[tuple[int, str]]):
        cleaned = [(line, _clean_prose(value)) for line, value in blocks if value.strip()]
        found = False
        for line, value in cleaned:
            character = _non_latin(value)
            if character:
                self.issue(path, line, f"English prose required; found non-Latin letter {character!r}", "LANGUAGE_SCRIPT")
                found = True
                continue
            language = _detected_language(value)
            if language:
                self.issue(path, line, f"English prose required; detected language {language!r} (heuristic)", "LANGUAGE_PROSE")
                found = True
        if not found and cleaned:
            language = _detected_language("\n".join(value for _, value in cleaned))
            if language:
                self.issue(path, cleaned[0][0], f"English prose required; aggregate detected language {language!r} (heuristic)", "LANGUAGE_PROSE")

    def yaml_language(self, path: Path, node, offset: int = 0):
        blocks = []
        visited = set()

        def visit(item):
            if id(item) in visited:
                return
            visited.add(id(item))
            if isinstance(item, ScalarNode) and item.tag == "tag:yaml.org,2002:str":
                parsed = _parse_markdown(item.value)
                blocks.extend((offset + item.start_mark.line + line, value) for line, value in parsed.prose)
            elif isinstance(item, MappingNode):
                for _, value in item.value:
                    visit(value)
            elif isinstance(item, SequenceNode):
                for value in item.value:
                    visit(value)

        visit(node)
        self.language(path, blocks)

    def skill(self, directory: Path):
        path = directory / "SKILL.md"
        if not path.is_file():
            self.issue(path, 1, "skill directory requires SKILL.md", "SKILL_MISSING")
            return
        text = self.read(path)
        if text is None:
            return
        frontmatter = _frontmatter(text)
        if frontmatter is None:
            self.issue(path, 1, "SKILL.md requires YAML frontmatter enclosed by --- lines", "FRONTMATTER_MISSING")
            return
        header, body, body_offset = frontmatter
        parsed = self.yaml(path, header, 1)
        if parsed:
            data, node = parsed
            for field in data:
                if field not in SKILL_FIELDS:
                    self.issue(path, self.field_line(node, field, 1), f"unknown frontmatter field {field!r}", "FIELD_UNKNOWN")
            name = data.get("name")
            if not isinstance(name, str) or not 1 <= len(name) <= 64 or not NAME.fullmatch(name):
                self.issue(path, self.field_line(node, "name", 1), "name must be 1..64 lowercase ASCII letters/digits with single separating hyphens", "NAME_INVALID")
            elif name != directory.name:
                self.issue(path, self.field_line(node, "name", 1), f"name must match directory {directory.name!r}", "NAME_MISMATCH")
            for field, maximum in (("description", 1024), ("compatibility", 500)):
                if field == "compatibility" and field not in data:
                    continue
                value = data.get(field)
                if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                    self.issue(path, self.field_line(node, field, 1), f"{field} must be a nonempty string of at most {maximum} characters", "FIELD_INVALID")
                elif SCAFFOLD.search(value):
                    self.issue(path, self.field_line(node, field, 1), f"unfinished scaffold marker in {field}", "SCAFFOLD_UNFINISHED")
            for field in ("license", "allowed-tools"):
                if field in data and not isinstance(data[field], str):
                    self.issue(path, self.field_line(node, field, 1), f"{field} must be a string", "FIELD_INVALID")
            if "metadata" in data:
                metadata = data["metadata"]
                if not isinstance(metadata, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()):
                    self.issue(path, self.field_line(node, "metadata", 1), "metadata must map string keys to string values", "FIELD_INVALID")
            self.yaml_language(path, node, 1)
        document = _parse_markdown(body)
        if not any(token.content.strip() for token in document.tokens if token.type in {"inline", "fence", "code_block"}) and not document.prose:
            self.issue(path, body_offset + 1, "SKILL.md must contain a nonempty instruction body", "BODY_EMPTY")
        for line, prose in document.prose:
            if SCAFFOLD.search(prose):
                self.issue(path, body_offset + line, "unfinished scaffold marker in skill instructions", "SCAFFOLD_UNFINISHED")

    def agent(self, path: Path, skill_name: str):
        text = self.read(path)
        if text is None:
            return
        parsed = self.yaml(path, text)
        if not parsed:
            return
        data, node = parsed
        if "interface" in data:
            interface = data["interface"]
            interface_node = next(value for key, value in node.value if key.value == "interface")
            if not isinstance(interface, dict):
                self.issue(path, self.field_line(node, "interface"), "interface must be a mapping", "INTERFACE_INVALID")
            else:
                for field in ("display_name", "short_description", "default_prompt"):
                    if field not in interface:
                        continue
                    value = interface[field]
                    line = self.field_line(interface_node, field)
                    if not isinstance(value, str) or not value.strip():
                        self.issue(path, line, f"interface.{field} must be a nonempty string", "INTERFACE_INVALID")
                    elif field == "short_description" and not 25 <= len(value) <= 64:
                        self.issue(path, line, "interface.short_description must contain 25..64 characters", "INTERFACE_LENGTH")
                    elif field == "default_prompt" and not re.search(r"\$" + re.escape(skill_name) + r"(?![\w-])", value):
                        self.issue(path, line, f"interface.default_prompt must reference ${skill_name}", "INTERFACE_PROMPT")
        self.yaml_language(path, node)

    def document(self, path: Path) -> Document | None:
        if path not in self.documents:
            text = self.read(path)
            if text is None:
                self.documents[path] = None
            else:
                frontmatter = _frontmatter(text) if path.name == "SKILL.md" else None
                if frontmatter:
                    _, body, offset = frontmatter
                    text = "\n" * offset + body
                self.documents[path] = _parse_markdown(text)
        return self.documents[path]

    def skill_boundary(self, path: Path) -> Path | None:
        relative = path.relative_to(self.root)
        if len(relative.parts) > 2 and relative.parts[0] == "skills":
            return self.root / "skills" / relative.parts[1]
        return None

    def link(self, source: Path, line: int, url: str):
        try:
            parsed = urlsplit(url)
        except ValueError as error:
            self.issue(source, line, f"invalid link {url!r}: {error}", "LINK_INVALID")
            return
        if parsed.scheme or parsed.netloc:
            if parsed.scheme.lower() == "file":
                self.issue(source, line, "file: links are not portable; use a relative path", "LINK_ABSOLUTE")
            return
        local_path = unquote(parsed.path)
        fragment = unquote(parsed.fragment)
        if "\x00" in local_path or "\\" in local_path:
            self.issue(source, line, f"invalid portable link path {url!r}", "LINK_INVALID")
            return
        target = (self.root / local_path.lstrip("/")) if local_path.startswith("/") else (source.parent / local_path if local_path else source)
        try:
            resolved = target.resolve()
        except (OSError, RuntimeError) as error:
            self.issue(source, line, f"cannot resolve link {url!r}: {error}", "LINK_INVALID")
            return
        boundary = self.skill_boundary(source)
        if boundary and not resolved.is_relative_to(boundary.resolve()):
            self.issue(source, line, f"local link escapes independently installable skill directory: {url!r}", "LINK_SKILL_ESCAPE")
            return
        if not resolved.is_relative_to(self.root):
            self.issue(source, line, f"local link escapes the repository: {url!r}", "LINK_ROOT_ESCAPE")
            return
        if not target.exists():
            self.issue(source, line, f"local link target does not exist: {url!r}", "LINK_MISSING")
            return
        if not fragment:
            return
        if target.is_dir():
            target = target / "README.md"
        if target.suffix.lower() != ".md":
            return  # Binary/PDF/HTML fragment semantics are outside this check.
        document = self.document(target)
        if document and fragment not in document.anchors:
            self.issue(source, line, f"Markdown heading/anchor does not exist: {url!r}", "LINK_ANCHOR")

    def run(self) -> list[Issue]:
        if not self.root.is_dir():
            self.issue(self.root, 1, "repository root must be an existing directory", "ROOT_INVALID")
            return self.issues
        skills = self.root / "skills"
        if not skills.is_dir():
            self.issue(skills, 1, "repository requires a skills directory", "SKILLS_MISSING")
        else:
            directories = sorted(path for path in skills.iterdir() if path.is_dir())
            if not directories:
                self.issue(skills, 1, "skills directory must contain at least one skill", "SKILLS_EMPTY")
            for directory in directories:
                if directory.is_dir():
                    if directory.is_symlink():
                        self.issue(directory, 1, "skill directories must be real directories, not symlinks", "SKILL_SYMLINK")
                        continue
                    self.skill(directory)
                    agent = directory / "agents" / "openai.yaml"
                    if agent.exists():
                        self.agent(agent, directory.name)
        files = set(self.root.glob("README*.md"))
        for folder in (skills, self.root / "evals"):
            if folder.is_dir():
                files.update(folder.rglob("*.md"))
        for path in sorted(files):
            boundary = self.skill_boundary(path)
            if boundary and not path.resolve().is_relative_to(boundary.resolve()):
                self.issue(path, 1, "Markdown symlink escapes its skill directory", "FILE_SKILL_ESCAPE")
                continue
            document = self.document(path)
            if not document:
                continue
            if path.parent != self.root:
                self.language(path, document.prose)
            for line, url in document.links:
                self.link(path, line, url)
        return sorted(set(self.issues), key=lambda issue: (str(issue.path), issue.line, issue.code, issue.message))


def validate_repository(root: Path) -> list[Issue]:
    """Return all offline validation errors, without modifying the repository."""
    return _Validator(Path(root)).run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (defaults to this script's repository)")
    arguments = parser.parse_args(argv)
    issues = validate_repository(arguments.root)
    for issue in issues:
        print(f"{issue.path}:{issue.line}: {issue.code}: {issue.message}", file=sys.stderr)
    if issues:
        print(f"Validation failed: {len(issues)} error(s).", file=sys.stderr)
        return 1
    print("Offline skill validation passed (structure, English prose, and local Markdown links).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
