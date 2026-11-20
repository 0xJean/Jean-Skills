---
name: github-team-workflow
description: Set up and execute structured GitHub team collaboration workflows, including dual-trunk (main + dev + release + hotfix) or single-trunk branching, GitHub Rulesets and Environments, split PR CI gates, release and RC tag promotion, hotfix and back-merge procedures, Issue and PR templates, tiered technical design docs, and repository AGENTS.md/CONTRIBUTING.md onboarding. Use when bootstrapping a repository's collaboration setup or running daily Git/GitHub development, release, or hotfix tasks; exclude generic Git tutorials, product management, or non-GitHub VCS platforms unless explicitly adapted.
---

# GitHub Team Collaboration Workflow

Bootstrap GitHub repository governance and execute daily development, release, hotfix, and technical design workflows consistently. Load only the references and templates needed for the current task. Respond in the user's requested language and follow the repository's documentation language; this skill's English source does not override either.

## Inspect the repository first

- Check existing branches (`main`, `dev`, `release/*`), default branch, tags, `.github/` files, `AGENTS.md`, `CONTRIBUTING.md`, `docs/design/`, and the project's build/test toolchain before generating files or running Git commands.
- Check whether `gh` CLI is installed and authenticated (`gh auth status`) before executing GitHub API operations (labels, Issues, PRs, Releases, Rulesets).
- Preserve established repository conventions when working inside an existing project; apply the defaults below when bootstrapping a new repository or standardizing an existing one.
- Ask only for missing decisions that change repository configuration or remote mutations (such as target topology, product tracker URL format, or confirmation before pushing tags/merging to `main`).

## Workflow topology defaults

| Topology | When to use | Branches | Merge strategy |
| --- | --- | --- | --- |
| **Standard Dual-Trunk** (default) | Multi-developer teams with `dev` / `staging` / `production` environments and controlled releases | `main`, `dev`, `feat/*`, `fix/*`, `chore/*`, `release/vX.Y.Z`, `hotfix/*` | Task -> `dev`: **Squash**; `release/*` or `hotfix/*` -> `main`: **Merge commit**; `main` -> `dev` sync: **Merge commit** |
| **Lite Single-Trunk** (optional) | Small teams (< 10 engineers), libraries, or continuous deployment without a separate `dev` branch | `main`, short-lived `feat/*`, `fix/*`, `chore/*` | Task -> `main`: **Squash**; release via tags or automated release PRs |

Unless the user asks for Lite Single-Trunk or the repository already uses single-trunk, follow **Standard Dual-Trunk**:

```text
feat/* ──PR(Squash)──▶ dev ──cut──▶ release/vX.Y.Z ──PR(Merge)──▶ main ──tag──▶ production
 (task branch)        (dev env)     (rc tag -> staging)           (vX.Y.Z)
                                                                     │
                                              ◀──PR(Merge)───────────┘ (back-merge to dev)

hotfix/* ──from main──▶ staging check ──PR(Merge)──▶ main ──tag vX.Y.Z+1──▶ production ──▶ sync to dev
```

## Non-negotiable guardrails

- **Never squash-merge `main -> dev`:** Back-merging `main` into `dev` must use a **Merge commit** so Git preserves merge ancestry and avoids repeated conflicts. Do not enable `Require linear history` on `dev` in dual-trunk repositories.
- **Exempt sync branches in `pr-dev.yml`:** Allow `main`, `release/*`, and `sync/*` head refs in `dev` branch-name and Issue-link checks so release/hotfix back-merges are never blocked.
- **Treat tags as immutable:** Never delete, move, or re-push published `v*` tags. Fix defects with a new `rc` tag (before release) or a new `PATCH` version (after release).
- **Build once, promote across environments:** Deploy the QA-verified `rc` artifact/image digest to `production` (re-tagging the verified digest to `vX.Y.Z`) rather than rebuilding an untested artifact from the `main` merge commit.
- **Respect GitHub Ruleset and Environment limits:** Ruleset bypasses apply to an entire Ruleset, and `Restrict creations` allows only bypass actors to create matching refs. Layer two `main` Rulesets (a no-bypass baseline enforcing 1 approval + mandatory `pr-main.yml` CI, plus a 2-approval release Ruleset bypassed only by P0 hotfix leads) and two `v*` Tag Rulesets (immutability with no bypass, plus `Restrict creations` bypassed by Maintainers / Release Managers). GitHub Environments' built-in Required Reviewers passes on **any one** approval; enable `Prevent self-review` and use a Custom Deployment Protection Rule if strict multi-person production quorum is required.
- **Respect existing repository templates (never overwrite silently):** During daily execution (Issues, PRs, design docs), always use the target repository's existing templates first and fall back to `assets/` only when missing. During bootstrap or audit, create missing files by default; for any file that already exists (`.github/` templates, workflows, `CODEOWNERS`, `AGENTS.md`, `CONTRIBUTING.md`), report differences and ask before merging incrementally—never silently overwrite repository-specific rules or CI steps.
- **Confirm remote mutations:** Before creating public Releases, pushing release/hotfix tags, merging into `main`, or applying destructive Git operations, confirm scope and target state with the user unless already explicitly authorized.

## Read by task

| Current task | Reference | Assets / scripts |
| --- | --- | --- |
| Bootstrap `.github/`, CI gates, Rulesets, Environments, `AGENTS.md`, or labels | [Repository bootstrap](references/repo-bootstrap.md) | [PR template](assets/pull_request_template.md), [Issue templates](assets/issue-templates/config.yml), [Workflows](assets/workflows/pr-dev.yml), [AGENTS template](assets/AGENTS.md.tmpl), [Label script](scripts/init-labels.sh) |
| Create Issues, cut task branches, write commits, open or review PRs | [Daily development](references/daily-dev.md) | [PR template](assets/pull_request_template.md), [Bug template](assets/issue-templates/bug.yml), [Feature template](assets/issue-templates/feature.yml) |
| Cut `release/*`, push `rc` or formal tags, run P0 hotfix, rollback, or back-merge `main -> dev` | [Release and hotfix](references/release-hotfix.md) | [PR to main workflow](assets/workflows/pr-main.yml), [Sync workflow](assets/workflows/sync-main-to-dev.yml), [Hotfix template](assets/issue-templates/hotfix.yml) |
| Draft or review single-repo or cross-repo technical design documents | [Technical design](references/tech-design.md) | [Design doc template](assets/design-doc-template.md) |

## Execution workflow

1. **Identify mode:** Determine whether the request is a **Bootstrap/Audit** task (configuring templates, workflows, labels, `AGENTS.md`, Rulesets) or an **Execution** task (Issue, branch, commit, PR, design doc, release, hotfix, sync).
2. **Load only the matching reference:** Read the relevant file in `references/` and adapt any template from `assets/` to the repository's actual language, package manager, PRD tracker (e.g., Feishu, Linear, Jira, Notion), and shared governance repository (e.g., `engineering` or `.github`).
3. **Verify locally before pushing:** Validate generated YAML syntax, verify branch base and cleanliness (`git status`, `git log --oneline -n 5`), check Conventional Commit and PR title formats, and run the repository's lint/test/build commands when code changes are involved.
4. **Deliver clear handoff:** Report files created or updated, commands run and their results, and any manual GitHub UI steps that still require repository admin permissions (such as Rulesets, Environments, or Secrets).
