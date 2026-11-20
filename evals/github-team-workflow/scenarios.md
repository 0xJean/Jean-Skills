# github-team-workflow Behavioral Evaluations

These maintainer scenarios are not runtime dependencies of the skill. Evaluate observable decisions and artifacts, not prescribed wording. A listed scenario is not a claim that it has been executed.

## Procedure

1. Use an isolated temporary Git repository with recorded initial state. Copy the complete `skills/github-team-workflow/` directory to an independent location so it cannot rely on the collection repository.
2. Give the executing agent only the user request and workspace files. Hide acceptance criteria. For selection tests, provide only skill names and descriptions.
3. Verify generated files, YAML syntax, Git history, and commands without pushing to a real remote unless explicitly tested against a disposable sandbox repository.

## GHW-01: Selection and scope boundaries

| Request | Expected selection |
| --- | --- |
| Bootstrap `.github/` templates, split PR CI gates, and `AGENTS.md` for our dual-trunk repo | Select `github-team-workflow` |
| Cut `release/v1.5.0` from `dev`, tag `rc.1`, and prepare the release checklist | Select `github-team-workflow` |
| Run a P0 production hotfix from `main` and back-merge to `dev` | Select `github-team-workflow` |
| Draft a cross-repo technical design doc for SMS login | Select `github-team-workflow` |
| Explain what `git rebase -i` does in general | Do not select solely for generic Git education |
| Build a Solidity ERC20 staking contract | Do not select; select `web3-evm-dev` instead |

## GHW-02: Repository bootstrap without workflow contradictions

**Setup:** Empty Python repository (`pyproject.toml`, `pytest`, `ruff`) with `main` and `dev` branches and no `.github/` directory.

**Request:** Set up the team's GitHub collaboration templates, split `dev`/`main` PR workflows, and `AGENTS.md`.

**Acceptance:**
- Creates `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/{bug,feature,hotfix,config}.yml`, `.github/workflows/{pr-dev,pr-main,sync-main-to-dev}.yml`, and `AGENTS.md` (under 200 lines).
- Adapts CI commands to Python (`pytest`, `ruff`) instead of leaving unadapted Node or placeholder `exit 1` commands.
- `pr-dev.yml` triggers on `dev` and `release/*` (allowing `main`, `release/*`, and `sync/*` into `dev`, and restricting `release/*` to `fix/*`, `docs/*`, `chore/*`); `pr-main.yml` triggers only on `main` and accepts only `release/*` and `hotfix/*`.
- Documents Ruleset configuration without enabling `Require linear history` on `dev`, and explains Ruleset bypass for P0 hotfixes and Environment single-reviewer approval behavior accurately.

## GHW-03: P0 hotfix and back-merge ancestry preservation

**Setup:** Local Git repository with `main` (at `v1.5.0`) and `dev` (ahead of `main` with feature commits).

**Request:** Prepare a P0 hotfix branch for Issue `#789` (payment crash), outline staging verification and `main` merge, and explain how to sync back to `dev`.

**Acceptance:**
- Cuts `hotfix/789-payment-crash` from `main`, never from `dev`.
- Requires staging verification (and notes coordination if a scheduled `release/*` is using staging) and green `pr-main.yml` CI.
- Merges to `main` with a Merge commit, tags `v1.5.1` as an annotated tag (`git tag -a`) only after confirmation, and back-merges `main -> dev` with a **Merge commit** (never Squash merge).
- Does not suggest deleting or moving `v1.5.0`.

## GHW-04: Artifact promotion and changelog tooling alignment

**Setup:** Team using dual-trunk (`dev` -> `release/*` -> `main`) asks how to wire `release-please` and container builds so `staging` and `production` run the same build.

**Acceptance:**
- Warns that `release-please` expects single-trunk release PRs and conflicts with manual `release/*` branches; recommends `git-cliff`, `conventional-changelog`, or GitHub `Generate release notes` instead (or switching to Lite Single-Trunk if `release-please` is required).
- Explains promoting/re-tagging the QA-verified `rc` image digest to `vX.Y.Z` rather than rebuilding an untested image from the `main` merge commit.
