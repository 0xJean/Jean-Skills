# Repository Bootstrap and Governance

Use this reference when bootstrapping a new repository, auditing an existing repository's GitHub collaboration setup, generating `.github/` files, configuring Rulesets and Environments, or authoring `AGENTS.md` and `CONTRIBUTING.md`.

## Repository file layout

```text
.github/
  pull_request_template.md
  CODEOWNERS
  dependabot.yml
  ISSUE_TEMPLATE/
    bug.yml
    feature.yml
    hotfix.yml
    config.yml
  workflows/
    pr-dev.yml           # Fast PR gate targeting dev and release/*
    pr-main.yml          # Strict release/hotfix gate targeting main only
    deploy-dev.yml       # Auto-deploy dev on push to dev (calls ops reusable workflow)
    deploy-staging.yml   # Auto-deploy staging on v*-rc.* tag (calls ops reusable workflow)
    release.yml          # Create GitHub Release & promote artifact to production on v* tag
    sync-main-to-dev.yml # Open main -> dev PR (or emit sync/* guide when diverged)
AGENTS.md                # Self-contained agent instructions (<= 200 lines)
CONTRIBUTING.md          # Human quick-start + link to full handbook
docs/design/             # Single-repo large feature design docs (NNNN-short-name.md)
```

## Split PR CI gates (`dev` vs `main`)

Keep `pr-dev.yml` and `pr-main.yml` separate so daily `dev` PRs stay fast (< 10 minutes) while `main` PRs run thorough release verification. Never put `branches: [dev, main]` on a single heavy workflow.

| Aspect | `pr-dev.yml` (`branches: [dev, 'release/*']`) | `pr-main.yml` (`branches: [main]`) |
| --- | --- | --- |
| Allowed head branches | To `dev`: `feat/*`, `fix/*`, `chore/*`, `refactor/*`, `docs/*`, `main`, `release/*`, `sync/*`. To `release/*`: `fix/*`, `docs/*`, `chore/*` only (code freeze). | **Only** `release/*` and `hotfix/*` (fail all others) |
| Required checks | Lint, unit tests + coverage, build, Conventional Commit PR title, branch-name check, `gitleaks` secret scan | All `dev` checks + integration/E2E tests, CodeQL, `dependency-review` (block high/critical), DB migration check, release checklist / `qa-approved` signal |
| Non-blocking helpers | Path labeler, PR size warning (> 400 lines), advisory Issue-link warning on `feat/*`/`fix/*`, AI review comments | Change summary, AI review (advisory only, never counts as approval) |
| Human approval | 1 reviewer (`CODEOWNERS` optional) | 2 reviewers including `CODEOWNERS` (P0 hotfix bypasses Ruleset #3—2nd approval and `CODEOWNERS` unless moved to #2—while baseline #2 keeps >= 1 review + full CI enforced) |
| Merge method | Squash for task branches; **Merge commit** for `main`/`release/*`/`sync/*` | **Merge commit** |

**Required adaptation before committing:** Both [pr-dev.yml](../assets/workflows/pr-dev.yml) and [pr-main.yml](../assets/workflows/pr-main.yml) include an intentional fail-closed `exit 1` placeholder in their `ci` / `full-verification` jobs so an unconfigured template never appears green. Replace those placeholders with the repository's actual lint, test, and build commands (Node, Python, Go, Rust, Java, etc.) during bootstrap.

**QA sign-off timing and identity:** The `qa-gate` job in [pr-main.yml](../assets/workflows/pr-main.yml) runs **before merging into `main`** and requires the `qa-approved` label (verifying label presence only, not *who* applied it). Keep these two checkpoints distinct:
- **Pre-merge (`PR -> main`):** Apply `qa-approved` before merging when using `pr-main.yml` as-is. If designated QA identity must be enforced before merge, replace `qa-gate` with a QA team PR review requirement (`CODEOWNERS` / Ruleset) or a workflow check verifying an `APPROVED` review from a QA team member.
- **Post-merge deployment (`production` Environment):** GitHub Environment Required Reviewers runs **after** the `vX.Y.Z` tag is pushed on `main` (at deployment time) and does not satisfy `pr-main.yml`'s `qa-gate` job; configure it as a separate deployment gate (or remove `qa-gate` if pre-merge label gating is not desired).

### Adapting for Lite Single-Trunk repositories

If the repository uses **Lite Single-Trunk** (no permanent `dev` branch):
- Omit `pr-main.yml` and `sync-main-to-dev.yml`; adapt `pr-dev.yml` as `.github/workflows/pr-ci.yml` targeting `branches: [main]`, and trim `main`, `release/*`, and `sync/*` from `branch-check` (add `release-please--*` if using `release-please`).
- Protect only `main` (1-2 reviewers, Squash merge, linear history optional) and `v*` tags (using the two layered Tag Rulesets below).
- Automated release PR tools such as `release-please` work cleanly in this mode.

## GitHub Rulesets configuration

GitHub Ruleset bypass permissions apply to an **entire Ruleset**, and `Restrict creations` blocks everyone *except* actors in that Ruleset's bypass list. Use **layered Rulesets** so P0 hotfix bypasses cannot skip mandatory CI or the first reviewer, and so Release Managers can create new `v*` tags without being able to update or delete published tags:

| Ruleset | Target | Rules enabled | Bypass list | Purpose |
| --- | --- | --- | --- | --- |
| **1. `dev` Protection** | `dev` | Require PR, **1 approval**, `pr-dev.yml` checks, up-to-date, resolve conversations, block force push & deletion (`Require linear history` = **Off**) | None (or break-glass repo admins only) | Allows Squash for task branches and Merge commit for `main`/`release/*`/`sync/*` back-merges |
| **2. `main` Mandatory Baseline** | `main` | Require PR, **1 approval**, **`pr-main.yml` checks**, up-to-date, resolve conversations, block force push & deletion (`Require linear history` = **Off**) | **None** (never grant hotfix bypass here) | Guarantees even P0 hotfixes always require >= 1 approval and green `pr-main.yml` CI (add `CODEOWNERS` here too if P0 hotfixes must also require Code Owner approval) |
| **3. `main` Standard Release Review** | `main` | **2 approvals**, require `CODEOWNERS` review | Narrow **Tech Lead / Release Manager** team (policy: P0 hotfixes only) | Layers on top of #2: normal releases need 2 approvals + `CODEOWNERS`; bypassing #3 waives both the 2nd approval and `CODEOWNERS` while #2 remains platform-enforced. GitHub does not check whether a PR is truly P0—enforce P0-only usage by policy and audit in the incident Issue |
| **4. `release/*` Protection** | `release/*` | Require PR, **1 approval**, `pr-dev.yml` checks, up-to-date, resolve conversations, block force push (omit `Restrict creations` / `Restrict deletions` here if Release Managers manage branch lifecycle) | None (or break-glass repo admins only) | Enforces freeze-period PR/CI discipline without granting PR/CI bypass. To gate creation and post-release deletion to Maintainers / Release Managers, add a separate `release/*` Lifecycle Ruleset (`Restrict creations` + `Restrict deletions`, bypassed by Maintainers / Release Managers); or keep `Restrict deletions` here with `Bypass: None` and retain `release/*` branches |
| **5. `v*` Tag Immutability** | Tag `v*` | `Restrict updates` + `Restrict deletions` | **None** | Published tags remain immutable—no role can move or delete them |
| **6. `v*` Tag Creation** | Tag `v*` | `Restrict creations` only | **Maintainers / Release Managers** | Allows only Maintainers / Release Managers to push new `v*` tags without granting delete/update bypass on #5 |

Also enable **Settings -> General -> Pull Requests** and check Actions permissions:
- Enable **Allow squash merging** (default for task PRs) and **Allow merge commits** (required for `release/* -> main`, `hotfix/* -> main`, `main -> dev`, `release/* -> dev`, and `sync/* -> dev`).
- Enable **Automatically delete head branches** (applies to unprotected task branches; branches covered by a `Restrict deletions` Ruleset—such as `release/*`—are not auto-deleted and must be deleted manually by a role with deletion bypass, or retained).
- For [sync-main-to-dev.yml](../assets/workflows/sync-main-to-dev.yml), enable **Allow GitHub Actions to create and approve pull requests**; on GitHub.com, `pull_request` (`opened`/`synchronize`/`reopened`) runs created with the default `GITHUB_TOKEN` pause awaiting manual approval from a user with write access—keep `GITHUB_TOKEN` if manual approval is acceptable, or supply a GitHub App token (preferred) or fine-grained PAT for unattended CI runs.

## Environments and operations separation

Keep application rules in each business repository and deployment pipelines/production credentials in a dedicated operations repository (or ops-owned reusable workflows):

- Business repositories invoke ops-maintained reusable workflows pinned to an **immutable tag or commit SHA** (for example, `org/ops-workflows/.github/workflows/deploy.yml@v1.2.0`), never `@main`.
- Configure three GitHub Environments: `dev`, `staging`, `production`.
  - Isolate databases, secrets, domains (`dev.`, `staging.`, `www.`), and third-party sandbox accounts across all three environments.
  - On `production`: enable **Required reviewers**, enable **Prevent self-review**, and restrict deployment branches/tags to `main` and `v*` tags.
  - Remember: GitHub Environments' built-in Required Reviewers passes after **any single** reviewer approves. Use Custom Deployment Protection Rules if compliance mandates 2-person production sign-off.
- Three isolated environments do not require three separate physical servers: small teams can use isolated containers/ports (with production on a dedicated host), Kubernetes namespaces, on-demand staging, or PaaS environments.

## Governance ownership and `AGENTS.md`

| Artifact | Location | Purpose |
| --- | --- | --- |
| Daily rules (branches, commits, PRs, Issues) | Each business repo (`AGENTS.md`, `CONTRIBUTING.md`, `.github/`) | Self-contained so newcomers and AI agents reading only the current repo get complete rules |
| Single-repo large design docs | Each business repo (`docs/design/`) | Versioned alongside code |
| Full handbook, tag contract, cross-repo designs | Shared governance repo (e.g. `engineering/handbook/`, `engineering/designs/`) | Single source of truth; tag contract changes require joint dev + ops approval |
| Default org templates | Org-level `.github` repo | Fallback Issue/PR templates for repos without local overrides |
| Deployment workflows, prod secrets, runbooks | Dedicated ops repo | Separation of duties and least privilege |

### `AGENTS.md` guidelines

- Keep `AGENTS.md` under **200 lines** and include a ruleset version header (e.g. `Workflow spec: v1.0`) so drift across repositories is easy to detect.
- **Include:** branch naming, commit and PR conventions, Issue linking, common local dev/test commands, security rules, and a short summary of design-doc tiers.
- **Omit (link instead):** server topology, full release runbooks, and verbose copies of rules already enforced by GitHub Rulesets.
- Keep `AGENTS.md` as the single local source of truth; point tool-specific files (such as `CLAUDE.md`) to it or symlink them to avoid drift.

## Bootstrap execution checklist

When asked to bootstrap or audit a repository:
1. Inspect existing `.github/`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/design/`, and stack files (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.).
2. **Apply non-destructive precedence rules:**
   - **Missing files:** Create and adapt them from `assets/` to the repository's real toolchain and conventions:
     - `.github/pull_request_template.md`
     - `.github/ISSUE_TEMPLATE/{bug,feature,hotfix,config}.yml`
     - `.github/workflows/{pr-dev,pr-main,sync-main-to-dev}.yml` (adapted to the repo's real lint/test/build commands)
     - `AGENTS.md` (from [AGENTS.md.tmpl](../assets/AGENTS.md.tmpl)) and `CONTRIBUTING.md`
     - `.github/CODEOWNERS` (ask for team/user handles if unknown)
   - **Existing files:** Never silently overwrite existing templates, workflows, `CODEOWNERS`, or `AGENTS.md`. Compare them against the baseline, report missing checks or conflicts (such as a missing `main`/`sync/*` exemption in `pr-dev.yml`), and ask before performing an incremental merge that preserves repository-specific fields and CI jobs.
3. If `gh` is authenticated and the user approves, run [scripts/init-labels.sh](../scripts/init-labels.sh) to sync standard labels (`--force` updates matching standard label colors/descriptions without deleting other custom labels).
4. Report the exact manual GitHub UI steps remaining (Rulesets, Environments, Secrets, default branch choice).
