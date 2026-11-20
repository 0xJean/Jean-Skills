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
| Human approval | 1 reviewer (`CODEOWNERS` optional) | 2 reviewers including `CODEOWNERS` (P0 hotfix uses controlled bypass with 1 review + full CI) |
| Merge method | Squash for task branches; **Merge commit** for `main`/`release/*`/`sync/*` | **Merge commit** |

**Required adaptation before committing:** Both [pr-dev.yml](../assets/workflows/pr-dev.yml) and [pr-main.yml](../assets/workflows/pr-main.yml) include an intentional fail-closed `exit 1` placeholder in their `ci` / `full-verification` jobs so an unconfigured template never appears green. Replace those placeholders with the repository's actual lint, test, and build commands (Node, Python, Go, Rust, Java, etc.) during bootstrap.

**QA sign-off identity:** The `qa-approved` label check in [pr-main.yml](../assets/workflows/pr-main.yml) verifies only label presence, not *who* applied the label. Treat it as a workflow reminder; when designated QA identity enforcement is required, enforce sign-off via QA team PR review (`CODEOWNERS` / Ruleset), a GitHub Environment reviewer gate, or an API check verifying an `APPROVED` review from a QA team member.

### Adapting for Lite Single-Trunk repositories

If the repository uses **Lite Single-Trunk** (no permanent `dev` branch):
- Omit `pr-main.yml` and `sync-main-to-dev.yml`; adapt `pr-dev.yml` as `.github/workflows/pr-ci.yml` targeting `branches: [main]`, and trim `main`, `release/*`, and `sync/*` from `branch-check` (add `release-please--*` if using `release-please`).
- Protect only `main` (1-2 reviewers, Squash merge, linear history optional) and `v*` tags.
- Automated release PR tools such as `release-please` work cleanly in this mode.

## GitHub Rulesets configuration

Configure four Rulesets (or Branch Protection rules if on a plan without Rulesets):

| Rule | `dev` | `main` | `release/*` | `v*` (Tag Ruleset) |
| --- | --- | --- | --- | --- |
| Block direct push / require PR | Yes | Yes | Yes | N/A |
| Required approvals | 1 | 2 | 1 | N/A |
| Require `CODEOWNERS` review | Optional | Yes | Recommended | N/A |
| Require status checks to pass | `pr-dev.yml` jobs | `pr-main.yml` jobs | `pr-dev.yml` jobs | N/A |
| Require branch up-to-date before merge | Yes | Yes | Yes | N/A |
| Require conversation resolution | Yes | Yes | Yes | N/A |
| Require linear history | **No** (breaks `main -> dev` merge commit) | **No** | **No** | N/A |
| Block force push & deletion | Yes | Yes | Yes | Block delete & update |
| Creation restriction | Maintainers | Maintainers | Maintainers / Release Managers | Maintainers / Release Managers |
| Bypass list | Repo admins (emergency) | Narrow Tech Lead / Release Manager team (for P0 hotfix 1-reviewer merge) | Repo admins | None |

Also enable **Settings -> General -> Pull Requests** and check Actions permissions:
- Enable **Allow squash merging** (default for task PRs) and **Allow merge commits** (required for `release/* -> main`, `hotfix/* -> main`, `main -> dev`, `release/* -> dev`, and `sync/* -> dev`).
- Enable **Automatically delete head branches**.
- For [sync-main-to-dev.yml](../assets/workflows/sync-main-to-dev.yml), enable **Allow GitHub Actions to create and approve pull requests**; note that PRs opened with the default `GITHUB_TOKEN` do not trigger `pull_request` workflows (`pr-dev.yml`), so provide a GitHub App token (preferred) or fine-grained PAT if `dev` requires status checks on automated `main -> dev` PRs.

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
