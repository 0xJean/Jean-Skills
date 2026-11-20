# Daily Development Workflow

Use this reference when creating Issues, cutting task branches, writing commits, opening or reviewing pull requests, or managing project boards.

## Branching rules

| Branch | Naming pattern | Cut from | PR target | Merge method | Lifecycle |
| --- | --- | --- | --- | --- | --- |
| Production trunk | `main` | Long-lived | None | None | Accepts only `release/*` and `hotfix/*` (or task branches via Squash in Lite mode); no direct push or force push |
| Integration trunk | `dev` | Long-lived (Dual-Trunk only) | None | None | Accepts task branches (Squash) and `main`/`release/*`/`sync/*` back-merges (Merge commit); no force push |
| Task branch | `feat/<id>-<slug>`, `fix/<id>-<slug>`, `chore/<slug>`, `refactor/<slug>`, `docs/<slug>` | Remote `dev` (or `main` in Lite mode) | `dev` (or `main` in Lite mode) | **Squash** | Short-lived (a few days); rebase onto target regularly; `--force-with-lease` allowed; auto-delete on merge |
| Back-merge sync | `main`, `release/*`, or `sync/<slug>` | `main` / `release/*` (when not diverged) or remote `dev` (for `sync/*`) | `dev` | **Merge commit** | Opened after every `release/*` or `hotfix/*` merges into `main`, or periodically during long freezes |

Rules:
- Only `main` and `dev` are long-lived branches; do not create personal long-lived branches.
- Include the Issue number on feature and bug branches (`feat/123-sms-login`, `fix/456-null-guard`). Omit the number only for tiny chores/typos that do not require an Issue.
- Keep the integration trunk (`dev`, or `main` in Lite mode) always buildable and runnable. Hide unfinished features behind a **Feature Flag**. If a merged PR breaks the trunk, **revert** it first rather than patching forward.

## Issue workflow and triage

Issues are the entry point for tracked work inside a repository. External product tools (such as Feishu, Linear, Jira, or Notion) own product-level PRDs and schedules; GitHub Issues own repository-level scope, technical approach, and engineering progress.

| Work type | Issue required? | Template & labels | Branch & PR link |
| --- | --- | --- | --- |
| Bug | Yes | Bug form (`type:bug`) | `fix/<id>-<slug>`, PR body `Fixes #<id>` |
| Production incident | Yes (P0) | Hotfix form (`type:hotfix`, `priority:p0`) | `hotfix/<id>-<slug>`, follow [release-hotfix.md](release-hotfix.md) |
| Feature | Yes (one per affected repo) | Feature form (`type:feature`) | `feat/<id>-<slug>`, PR body `Closes #<id>` (or `Refs #<id>` for intermediate PRs) |
| Tiny tweak, typo, small refactor, docs | No (within team threshold) | Direct PR | `chore/*`, `refactor/*`, `docs/*` |

### Standard label taxonomy

| Dimension | Labels | Meaning |
| --- | --- | --- |
| Type | `type:bug`, `type:feature`, `type:hotfix` | Applied automatically by Issue forms |
| Priority | `priority:p0`, `priority:p1`, `priority:p2`, `priority:p3` | P0: outage/data risk (immediate hotfix); P1: core flow, current cycle; P2: normal backlog; P3: nice-to-have |
| Area | `area:frontend`, `area:backend`, `area:infra` (adapt to repo) | Maps to `CODEOWNERS` |
| Status | `needs-info`, `blocked` | Missing reproduction/spec; waiting on external dependency |
| Resolution / Meta | `duplicate`, `wontfix`, `good first issue`, `qa-approved` | Closure metadata and QA sign-off |

### Issue lifecycle and closing semantics

Recommended GitHub Projects board columns:
`Backlog` -> `Todo` -> `In Progress` -> `In Review` -> `Merged to dev` -> `Released`.

Because GitHub auto-closes `Closes #123` / `Fixes #123` **only when the PR merges into the repository's default branch**, choose one convention per repository:

- **Multi-PR features (`Refs #` vs `Closes #`):** When a repository's `type:feature` Issue is split into multiple small PRs (`<= 400` lines each), link intermediate PRs with `Refs #<id>` (so they stay traceable without prematurely closing the Issue) and use `Closes #<id>` only on the final PR that completes the acceptance criteria.

| Option | Configuration | Trade-off |
| --- | --- | --- |
| **Default branch = `dev`** (simpler for small/medium teams) | Set `dev` as default branch while keeping `main` protected | `Closes #123` closes automatically on merge to `dev`; reopen or file a bug if QA rejects it. Verify Dependabot and scheduled workflows target the intended branch. |
| **Default branch = `main`** (strict release tracking) | Keep `main` as default branch; use a GitHub Action to move board status to `Merged to dev` on merge to `dev` | Issue stays open until the release merges into `main`; requires extra board automation. |

## Daily development steps

1. **Create or claim the Issue:** Confirm acceptance criteria (or bug reproduction steps) and technical design tier (see [tech-design.md](tech-design.md)).
2. **Cut a fresh task branch from the remote base trunk:**
   - **Standard Dual-Trunk** (from remote `dev`):
     ```bash
     git fetch origin dev \
       && git switch --no-track -c feat/123-sms-login "$(git rev-parse --verify 'FETCH_HEAD^{commit}')"
     ```
   - **Lite Single-Trunk** (repositories with `main` only, no `dev` branch):
     ```bash
     git fetch origin main \
       && git switch --no-track -c feat/123-sms-login "$(git rev-parse --verify 'FETCH_HEAD^{commit}')"
     ```
3. **Commit with Conventional Commits:**
   - Format: `<type>(<scope>): <concise summary>` (types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`, `perf`).
   - Add `!` after type/scope or a `BREAKING CHANGE:` footer for breaking changes.
4. **Keep the PR small and focused:**
   - One logical change per PR; target `<= 400` changed lines where practical.
   - Use Draft PRs for early feedback.
   - Self-review the diff, verify tests locally, and fill out `.github/pull_request_template.md` (summary, linked Issue, design doc link for medium/large features, test verification, UI screenshots if applicable, self-check list).
5. **Review and merge:**
   - `CODEOWNERS` auto-assigns reviewers; aim for a 24-hour review SLA.
   - Focus human review on correctness, maintainability, edge cases, and security; leave formatting to linters.
   - After addressing review comments, click **Re-request review**.
   - **Standard Dual-Trunk:** Merge into `dev` via **Squash merge** once CI checks pass, conversations are resolved, and required approval (1 reviewer) is granted.
   - **Lite Single-Trunk:** Merge into `main` via **Squash merge** once CI checks pass, conversations are resolved, and required approvals (`1-2` reviewers) are granted.
6. **Verify after merge:**
   - **Standard Dual-Trunk:** Merging to `dev` deploys the `dev` environment automatically for developer self-verification.
   - **Lite Single-Trunk:** Verify through the repository's `main` CI/CD checks or preview/staging deployment flow, then cut releases via tags or automated release PRs.
