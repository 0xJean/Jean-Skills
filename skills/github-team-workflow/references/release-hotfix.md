# Release, Tagging, and Hotfix Workflow

Use this reference when cutting a release branch, tagging release candidates (`rc`) or production versions, promoting build artifacts, running a P0 hotfix, rolling back a release, or back-merging `main` into `dev`.

## Release flow (`dev -> release/* -> main -> dev`)

```text
1. Cut release/vX.Y.Z from dev (code freeze)
2. Fix freeze bugs via PR into release/vX.Y.Z
3. Tag vX.Y.Z-rc.1 on release/vX.Y.Z -> build artifact & auto-deploy staging
4. QA regression on staging
   ├── Failed -> fix via PR on release/vX.Y.Z -> tag vX.Y.Z-rc.2 -> re-verify
   └── Passed -> QA sign-off (qa-approved label or environment approval)
5. Open PR release/vX.Y.Z -> main (Merge commit, 2 approvals incl. CODEOWNERS)
6. Tag vX.Y.Z on main merge commit -> create GitHub Release -> promote verified rc artifact to production (manual approval gate)
7. Back-merge main -> dev via PR (Merge commit), delete release/vX.Y.Z, monitor production
```

### Freeze-period rules (`release/vX.Y.Z`)

- **Allowed:** bug fixes, documentation, version bumps, and changelog updates.
- **Forbidden:** new features and unrelated refactors (those continue merging into `dev` for the next release).
- **Protection:** protect `release/*` with the same PR, review, and CI rules as `main` (no direct push or force push).
- **Avoid duplicate sync conflicts:** commit freeze fixes via PR into `release/vX.Y.Z`. Do **not** cherry-pick every freeze fix individually back to `dev` if you will merge `main -> dev` at release end; for long freezes, periodically back-merge `release/vX.Y.Z` into `dev` with a Merge commit instead.
- **When `dev` requires branches to be up to date before merging:** If `dev` has received next-release commits after `release/vX.Y.Z` was cut, GitHub will block a direct `release/vX.Y.Z -> dev` PR until the head branch is updated. **Never** merge `dev` into `release/vX.Y.Z` (that leaks next-release code into the frozen branch). Instead, fetch explicitly, pin the remote commit SHAs via `FETCH_HEAD` (safe in `--single-branch` clones and immune to unpushed local `dev` commits), and chain commands with `&&` so nothing pushes if any step fails:
  ```bash
  git fetch origin release/v1.5.0 \
    && FREEZE_FULL_SHA=$(git rev-parse --verify 'FETCH_HEAD^{commit}') \
    && FREEZE_SHORT_SHA=$(git rev-parse --short "$FREEZE_FULL_SHA") \
    && SYNC_BRANCH="sync/release-v1.5.0-${FREEZE_SHORT_SHA}-to-dev" \
    && git fetch origin dev \
    && DEV_SHA=$(git rev-parse --verify 'FETCH_HEAD^{commit}') \
    && git switch --no-track -c "$SYNC_BRANCH" "$DEV_SHA" \
    && git merge --no-ff "$FREEZE_FULL_SHA" \
    && git push -u origin "$SYNC_BRANCH"
  ```
  Then open a PR `"$SYNC_BRANCH" -> dev` and merge it with **Merge commit** (never Squash). `release/v1.5.0` stays untouched while `dev` receives the freeze fixes and full merge ancestry.

### Artifact promotion (build once, deploy everywhere)

To uphold **build once, promote across environments** despite `release/* -> main` creating a new Merge commit SHA:

1. **On `vX.Y.Z-rc.N` push:** Build and publish an immutable artifact (container image digest or signed tarball) tagged with `vX.Y.Z-rc.N` (and its source commit/tree hash), then deploy it to `staging`.
2. **On `vX.Y.Z` push on `main`:** Do **not** rebuild an untested artifact from scratch when deploying containers or compiled packages. Instead, verify the `main` commit tree matches the QA-approved `vX.Y.Z-rc.N` (or references the approved RC digest), re-tag/promote that exact immutable artifact to `vX.Y.Z`, and deploy it to `production` after Environment approval.
3. **Fallback for version-embedded builds:** If the target runtime embeds the Git tag string at compile time (for example, certain static frontend bundles or CLI binaries), document deterministic builds and pin lockfiles so staging and production builds remain reproducible.

## Tagging contract and SemVer

Tags are the contract between engineering and operations pipelines. Define tag patterns in one shared location (such as an `engineering` handbook) and require joint engineering + ops review before changing them.

| Tag pattern | Where to tag | Triggered action |
| --- | --- | --- |
| `vX.Y.Z-rc.N` (e.g. `v1.5.0-rc.1`) | Latest CI-green commit on `release/vX.Y.Z` (or `hotfix/*` if using RC-triggered staging) | Build immutable artifact and auto-deploy `staging` |
| `vX.Y.Z` (e.g. `v1.5.0`, `v1.5.1`) | CI-green merge commit on `main` | Create GitHub Release; enter `production` Environment approval gate; promote artifact |

Rules:
- Use annotated tags (`git tag -a`) with SemVer: `MAJOR` (breaking), `MINOR` (backward-compatible feature), `PATCH` (backward-compatible bug fix / hotfix).
- Never tag `dev`.
- Protect `v*` with a Tag Ruleset (disallow delete and update; restrict creation to maintainers/Release Managers).
- **Tags are immutable:** If a local tag is wrong before push, delete and recreate locally. Once pushed, never delete or move it—increment `-rc.(N+1)` or publish a new `PATCH` version.
- **Changelog tooling:** In dual-trunk + `release/*` workflows, use `git-cliff`, `conventional-changelog`, or GitHub's built-in `Generate release notes` rather than `release-please` or `semantic-release` (which expect single-trunk release PRs and conflict with manual `release/*` branches). Reserve `release-please` for Lite Single-Trunk repositories.

### Tag commands

Always fetch the target remote branch first, capture the verified commit SHA immediately from `FETCH_HEAD` (works in both full and `--single-branch` clones), and chain verification, tagging, and pushing with `&&` so a failed `git tag -a` never falls through to `git push`. If `git tag -a` fails because the tag name already exists locally, stop and inspect `git show --stat <tag>` to see which commit it points to; delete and recreate it only if that local tag was never pushed to `origin`:

```bash
# Release candidate on release/v1.5.0 (confirm CI passed on RC_SHA)
git fetch origin release/v1.5.0 \
  && RC_SHA=$(git rev-parse --verify 'FETCH_HEAD^{commit}') \
  && git show --stat "$RC_SHA" \
  && git tag -a v1.5.0-rc.1 "$RC_SHA" -m "rc: v1.5.0-rc.1" \
  && git push origin refs/tags/v1.5.0-rc.1

# Production release or hotfix on main (confirm CI green and user approval first)
git fetch origin main \
  && RELEASE_SHA=$(git rev-parse --verify 'FETCH_HEAD^{commit}') \
  && git show --stat "$RELEASE_SHA" \
  && git tag -a v1.5.0 "$RELEASE_SHA" -m "release: v1.5.0" \
  && git push origin refs/tags/v1.5.0 \
  && git show --stat v1.5.0
```

## Production approval and separation of duties

- **QA sign-off identity:** Checking for a `qa-approved` label in `pr-main.yml` is only a lightweight signal—any user with write/triage access can apply labels. When designated QA sign-off must be identity-enforced, require a PR review from the QA team (via `CODEOWNERS` / Ruleset), a GitHub Environment reviewer gate assigned to QA, or an explicit API check for an `APPROVED` review from a QA team member.
- Enable **Prevent self-review** on the `production` GitHub Environment so the person who pushed the tag cannot approve their own deployment.
- Restrict the `production` Environment deployment policy to `main` and `v*` tags only.
- **GitHub platform constraint:** GitHub Environments' built-in Required Reviewers approves deployment as soon as **any single** listed reviewer approves; it does not enforce a 2-person quorum natively. If strict multi-person production approval is required, add a Custom Deployment Protection Rule or an external approval gate.

## Hotfix workflow (P0 production incidents)

1. **Create incident Issue:** Use the Hotfix template (`type:hotfix`, `priority:p0`) with impact, detection time, and immediate mitigation.
2. **Cut from remote `main` (never from `dev` or an unpushed local `main`):**
   ```bash
   git fetch origin main \
     && git switch --no-track -c hotfix/789-payment-crash "$(git rev-parse --verify 'FETCH_HEAD^{commit}')"
   ```
3. **Fix and add regression test:** Keep the patch minimal and targeted.
4. **Validate on `staging` before merging to `main`:**
   - Deploy via a hotfix RC tag (`v1.5.1-rc.1`) or an explicit `workflow_dispatch` on the staging workflow.
   - If a scheduled `release/*` is currently undergoing QA on `staging`, coordinate with QA/Release Manager to pause regular regression or use a secondary staging slot before deploying the hotfix.
5. **Merge into `main` (Merge commit):**
   - CI checks in `pr-main.yml` remain mandatory.
   - **Ruleset reality for expedited 1-reviewer hotfix:** Because GitHub Rulesets on `main` enforce a fixed reviewer count (2) regardless of head branch, grant Ruleset bypass permission to a narrow role/team (Tech Leads / Release Managers) so a P0 hotfix with 1 review and green CI can merge without deadlock. Record the bypass in the incident Issue.
6. **Tag and deploy `PATCH` release:** Tag `v1.5.1` on `main`, complete production approval, and monitor metrics.
7. **Back-merge to `dev` (mandatory):** Open a `main -> dev` Merge commit PR (or cherry-pick only when selectively porting an isolated commit).
8. **Postmortem:** Add root cause, timeline, and follow-up test/alert tasks to the incident Issue.

## Back-merging `main -> dev` and cherry-pick rules

- **Default:** Always sync `main -> dev` with a **Merge commit** PR (opened automatically by `sync-main-to-dev.yml` when `dev` has not diverged). Never squash-merge `main -> dev`. When `main` and `dev` have diverged and `dev` enforces `Require branches to be up to date before merging`, `sync-main-to-dev.yml` skips the blocked direct PR and publishes copy-pasteable `sync/main-<short-sha>-to-dev` instructions in the Actions job summary (`git fetch origin`, `git switch --no-track -c ... origin/dev`, `git merge --no-ff <main-full-sha>`, Merge commit PR into `dev`) rather than merging `dev` into `main`.
- **When to use `cherry-pick`:** Only for porting an isolated commit to an older maintenance branch, rescuing a commit made on the wrong branch, or moving a single urgent fix when a full `main -> dev` merge is temporarily blocked.
- **When NOT to use `cherry-pick`:** Regular `dev -> main` releases or bulk commit transfers (cherry-pick creates new commit hashes and causes future merge conflicts).
- Always pass `-x` (and `-m 1` for merge commits):
  ```bash
  git fetch origin dev \
    && git switch --no-track -c sync/hotfix-789-to-dev "$(git rev-parse --verify 'FETCH_HEAD^{commit}')" \
    && git cherry-pick -x <commit-hash> \
    && git push -u origin sync/hotfix-789-to-dev
  ```

## Rollback rules

- **Immediate mitigation:** Redeploy the previous known-good production tag/digest through the ops pipeline.
- **Forward fix / code revert:** Revert the offending commit(s) via a `hotfix/*` PR to `main` and publish a new `PATCH` tag. Never delete or move an existing tag.

## Release checklist

Include this checklist in release PRs to `main`:

- [ ] All target Issues/PRs merged and CI green
- [ ] Staging regression passed and QA signed off (`qa-approved`)
- [ ] Database migrations reviewed and rollback path verified
- [ ] Environment variables, secrets, and Feature Flags confirmed
- [ ] Release Notes / Changelog prepared
- [ ] Release window, Release Manager, and rollback owner confirmed
- [ ] Post-release monitoring plan ready (error rates and core SLIs)
