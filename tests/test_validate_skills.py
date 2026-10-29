"""Offline validation regressions using isolated, disposable skill repositories."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "validate_skills.py"
sys.path.insert(0, str(SCRIPT.parent))
from validate_skills import validate_repository  # noqa: E402


DESCRIPTION = (
    "Create and review example documentation when users need clear instructions "
    "for configuring and testing their projects."
)
ENGLISH_BODY = """# Example skill

Read the project documentation before making changes. Explain the relevant
configuration options and verify that the resulting instructions are complete.
"""
OPENAI_METADATA = """interface:
  display_name: "Example documentation"
  short_description: "Create and review clear project documentation"
  default_prompt: "Use $example-skill to review the project documentation."
"""


class ValidateSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.root = self.directory / "repository"
        self.root.mkdir()
        self.skill = self.write_skill()

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_skill(
        self,
        name: str = "example-skill",
        *,
        frontmatter: str | None = None,
        body: str = ENGLISH_BODY,
    ) -> Path:
        if frontmatter is None:
            frontmatter = f"name: {name}\ndescription: {DESCRIPTION}\n"
        return self.write(
            f"skills/{name}/SKILL.md", f"---\n{frontmatter}---\n\n{body}"
        )

    def assert_valid(self) -> None:
        self.assertEqual(validate_repository(self.root), [])

    def assert_invalid(self, source: Path) -> None:
        issues = validate_repository(self.root)
        relative = source.relative_to(self.root).as_posix()
        matching = [
            issue for issue in issues if str(issue.path).replace("\\", "/").endswith(relative)
        ]
        self.assertTrue(matching, f"Expected an issue for {relative}; got {issues!r}")
        for issue in matching:
            self.assertIsInstance(issue.path, Path)
            self.assertIsInstance(issue.line, int)
            self.assertGreaterEqual(issue.line, 1)
            self.assertIsInstance(issue.message, str)
            self.assertTrue(issue.message.strip())
            self.assertIsInstance(issue.code, str)
            self.assertTrue(issue.code.strip())

    def test_minimal_english_skill_without_optional_metadata(self) -> None:
        self.assert_valid()

    def test_valid_optional_metadata(self) -> None:
        self.write_skill(
            frontmatter=(
                f"name: example-skill\ndescription: {DESCRIPTION}\n"
                "license: MIT\n"
                "compatibility: Requires a local Python interpreter for validation.\n"
                "allowed-tools: Read Write\n"
                "metadata:\n  author: Example team\n  version: '1.0'\n"
            )
        )
        self.write("skills/example-skill/agents/openai.yaml", OPENAI_METADATA)
        self.assert_valid()

    def test_each_skill_directory_requires_skill_markdown(self) -> None:
        missing = self.root / "skills" / "missing-skill" / "SKILL.md"
        missing.parent.mkdir()
        self.assert_invalid(missing)

    def test_empty_skills_directory_is_rejected(self) -> None:
        self.skill.unlink()
        self.skill.parent.rmdir()
        self.assert_invalid(self.root / "skills")

    def test_invalid_yaml_non_mapping_and_duplicate_keys(self) -> None:
        cases = {
            "malformed": "name: [unterminated\n",
            "non_mapping": "- example-skill\n- documentation\n",
            "duplicate": (
                f"name: example-skill\nname: example-skill\ndescription: {DESCRIPTION}\n"
            ),
            "nested_duplicate": (
                f"name: example-skill\ndescription: {DESCRIPTION}\n"
                "metadata:\n  author: First author\n  author: Second author\n"
            ),
        }
        for label, frontmatter in cases.items():
            with self.subTest(label=label):
                self.write_skill(frontmatter=frontmatter)
                self.assert_invalid(self.skill)

    def test_frontmatter_is_required(self) -> None:
        self.skill.write_text(ENGLISH_BODY, encoding="utf-8")
        self.assert_invalid(self.skill)

    def test_name_must_match_the_skill_directory(self) -> None:
        self.write_skill(frontmatter=f"name: different-skill\ndescription: {DESCRIPTION}\n")
        self.assert_invalid(self.skill)

    def test_description_must_be_a_nonempty_bounded_string(self) -> None:
        for description in ('""', "null", "42", '"' + "a" * 1025 + '"'):
            with self.subTest(description=description[:40]):
                self.write_skill(
                    frontmatter=f"name: example-skill\ndescription: {description}\n"
                )
                self.assert_invalid(self.skill)

    def test_unfinished_description_and_body_placeholders_are_rejected(self) -> None:
        cases = {
            "description": (
                "name: example-skill\ndescription: '[TODO: describe this skill]'\n",
                ENGLISH_BODY,
            ),
            "body": (None, "[TODO: add instructions]\n"),
        }
        for label, (frontmatter, body) in cases.items():
            with self.subTest(label=label):
                self.write_skill(frontmatter=frontmatter, body=body)
                self.assert_invalid(self.skill)

    def test_instructions_to_resolve_project_todos_are_valid(self) -> None:
        self.write_skill(
            frontmatter=(
                "name: example-skill\n"
                "description: Find and resolve TODO and FIXME comments in project source "
                "code when users request cleanup of unfinished implementation work.\n"
            ),
            body=ENGLISH_BODY
            + "\nReview TODO and FIXME comments in the project's code. Resolve the underlying "
            "issues and verify the affected behavior before completing the task.\n",
        )
        self.assert_valid()

    def test_optional_frontmatter_fields_have_expected_types(self) -> None:
        for optional in (
            "license: [MIT]\n",
            "compatibility: [Python]\n",
            "allowed-tools: [Read, Write]\n",
            "metadata: [author]\n",
            "metadata:\n  version: 1\n",
        ):
            with self.subTest(optional=optional):
                self.write_skill(
                    frontmatter=f"name: example-skill\ndescription: {DESCRIPTION}\n{optional}"
                )
                self.assert_invalid(self.skill)

    def test_root_readmes_and_code_examples_are_exempt_from_english_check(self) -> None:
        self.write("README.md", "# 示例技能\n\n这个项目包含可重复使用的技能和详细的中文说明。\n")
        self.write("README.zh-CN.md", "# 中文说明\n\n请阅读文档，然后根据项目需要选择相应的技能。\n")
        self.write_skill(
            body=ENGLISH_BODY
            + """
Use the following literal examples when testing localized project output.

```markdown
# 这是中文代码示例
这段中文是需要保留的代码示例，不属于技能本身的英文说明。
[Example link](missing-example.md)
```

    [Indented example](another-missing-example.md)

The literal value `Estas instrucciones son solamente un ejemplo de código`
is supplied by the caller.
"""
        )
        self.assert_valid()

    def test_non_english_skill_prose_is_rejected(self) -> None:
        prose = {
            "Chinese": "这是一个用于编写和检查项目文档的技能。请先阅读项目配置，然后验证所有说明和操作步骤是否正确。",
            "French": (
                "Veuillez lire attentivement la documentation du projet avant de modifier les fichiers. "
                "Expliquez les différentes options de configuration et vérifiez que toutes les instructions sont complètes."
            ),
            "Spanish": (
                "Lea cuidadosamente la documentación del proyecto antes de modificar los archivos. "
                "Explique las diferentes opciones de configuración y compruebe que todas las instrucciones estén completas."
            ),
        }
        for language, text in prose.items():
            with self.subTest(language=language):
                self.write_skill(body=f"# Example skill\n\n{text}\n")
                self.assert_invalid(self.skill)

    def test_non_english_reference_prose_is_rejected(self) -> None:
        reference = self.write(
            "skills/example-skill/references/guide.md",
            "# Project guide\n\n"
            "Veuillez lire attentivement les instructions avant de commencer votre travail. "
            "Cette documentation explique comment configurer les outils et vérifier les résultats du projet.\n",
        )
        self.assert_invalid(reference)

    def test_missing_local_files_and_anchors_are_rejected(self) -> None:
        self.write("skills/example-skill/references/guide.md", "# Setup\n\n" + ENGLISH_BODY)
        for target in ("references/missing.md", "references/guide.md#missing", "#missing"):
            with self.subTest(target=target):
                self.write_skill(body=ENGLISH_BODY + f"\nRead the [project guide]({target}).\n")
                self.assert_invalid(self.skill)

    def test_duplicate_heading_slugs_reference_links_and_url_encoding(self) -> None:
        self.write(
            "skills/example-skill/references/guide notes.md",
            "# Next steps\n\n" + ENGLISH_BODY + "\n## Repeat\n\n## Repeat\n",
        )
        self.write_skill(
            body=ENGLISH_BODY
            + """
Read the [next steps](references/guide%20notes.md#next%2Dsteps).
Compare the [first heading](references/guide%20notes.md#repeat) and the
[second heading][repeated-section].

[repeated-section]: references/guide%20notes.md#repeat-1
"""
        )
        self.assert_valid()

    def test_broken_reference_style_link_is_rejected(self) -> None:
        self.write_skill(
            body=ENGLISH_BODY
            + "\nRead the [detailed guide][guide].\n\n[guide]: references/missing.md\n"
        )
        self.assert_invalid(self.skill)

    def test_headings_inside_code_blocks_do_not_define_anchors(self) -> None:
        self.write_skill(
            body=ENGLISH_BODY
            + "\n```markdown\n## Example heading\n```\n\n"
            "Read the [example heading](#example-heading).\n"
        )
        self.assert_invalid(self.skill)

    def test_cross_skill_links_are_not_self_contained(self) -> None:
        self.write_skill(name="another-skill")
        self.write_skill(
            body=ENGLISH_BODY + "\nRead the [other skill](../another-skill/SKILL.md).\n"
        )
        self.assert_invalid(self.skill)

    def test_symlinks_cannot_escape_the_skill_directory(self) -> None:
        outside = self.directory / "external-guide.md"
        outside.write_text(ENGLISH_BODY, encoding="utf-8")
        link = self.skill.parent / "external.md"
        link.symlink_to(outside)
        self.write_skill(body=ENGLISH_BODY + "\nRead the [external guide](external.md).\n")
        issues = validate_repository(self.root)
        self.assertTrue(
            any(Path(issue.path).name in {"SKILL.md", "external.md"} for issue in issues),
            f"Expected a symlink escape issue; got {issues!r}",
        )

    def test_openai_metadata_rejects_invalid_types_lengths_and_prompt(self) -> None:
        cases = {
            "root_mapping": "- interface\n",
            "interface_mapping": "interface: []\n",
            "display_name_type": OPENAI_METADATA.replace('"Example documentation"', "42"),
            "short_description_type": OPENAI_METADATA.replace(
                '"Create and review clear project documentation"', "[]"
            ),
            "short_description_short": OPENAI_METADATA.replace(
                "Create and review clear project documentation", "Too short"
            ),
            "short_description_long": OPENAI_METADATA.replace(
                "Create and review clear project documentation", "x" * 65
            ),
            "default_prompt_type": OPENAI_METADATA.replace(
                '"Use $example-skill to review the project documentation."', "true"
            ),
            "default_prompt_skill": OPENAI_METADATA.replace("$example-skill", "$another-skill"),
        }
        for label, metadata in cases.items():
            with self.subTest(label=label):
                path = self.write("skills/example-skill/agents/openai.yaml", metadata)
                self.assert_invalid(path)

    def test_cli_reports_success_and_actionable_failure(self) -> None:
        command = [sys.executable, str(SCRIPT), "--root", str(self.root)]
        valid = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

        self.write_skill(frontmatter="name: example-skill\ndescription: ''\n")
        invalid = subprocess.run(command, capture_output=True, text=True, check=False)
        output = invalid.stdout + invalid.stderr
        self.assertEqual(invalid.returncode, 1, output)
        self.assertIn("skills/example-skill/SKILL.md", output)
        self.assertIn("description", output.lower())


if __name__ == "__main__":
    unittest.main()
