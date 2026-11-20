# Technical Design Workflow

Use this reference when sizing a new feature, deciding where its technical design lives, drafting a design document, or coordinating a cross-repository rollout.

## Separation of concerns

| Layer | Tool | Owns |
| --- | --- | --- |
| Product / feature level | External tracker (e.g. Feishu, Linear, Jira, Notion) | PRD, business goals, milestone schedule |
| Repository level | GitHub Issue | Repository scope, acceptance criteria, owner, engineering progress |
| Architecture / design level | Issue body, `docs/design/`, or shared `engineering/designs/` | Technical approach, contracts, rollout and rollback plan |
| Code level | GitHub PR | Implementation, tests, code review |

**Single source of truth:** Each technical design lives in **one** place. All other Issues or documents link to it rather than duplicating text.

## Design tiers and storage

| Tier | Criteria | Where it lives | Review method |
| --- | --- | --- | --- |
| **Small** | Single module; no API contract or schema changes | A few sentences inside the repo's feature Issue | Issue comments |
| **Medium** | New/modified APIs or spans multiple modules within one repo | Concise one-page plan inside the repo's feature Issue | 1-2 peers review before coding |
| **Large (single repo)** | Database schema changes, new dependencies/tech, or architectural impact | `<repo>/docs/design/NNNN-short-name.md` (linked from Issue) | PR review in the repository |
| **Cross-repo** | Coordinates changes across two or more repositories | Shared governance repo `<engineering>/designs/NNNN-short-name.md` (linked from every affected repo's Issue) | PR review with owners from every affected repository |

Only **Large** and **Cross-repo** features require a standalone design file. When unsure about the tier, escalate to the tech lead before writing code.

## File naming and lifecycle

- **Filename:** `NNNN-short-name.md` with zero-padded sequential numbering (for example, `0012-sms-login.md`).
- **Status progression:** `Draft` -> `In Review` -> `Approved` -> `Implemented` (or `Superseded` / `Rejected`).
- Start from [design-doc-template.md](../assets/design-doc-template.md).

## Required sections for cross-repo designs

In addition to the standard template sections (background/PRD link, goals/non-goals, design, alternatives, impact, rollout/rollback, risks, acceptance criteria), a cross-repo design must include:

1. **Affected repositories matrix:** Every repository involved, high-level responsibility, and link to that repository's tracking Issue.
2. **Interface contracts:** Request/response schemas, event formats, versioning, and backward-compatibility guarantees between repositories.
3. **Deployment order and compatibility:** Which repository deploys first, whether old and new versions can coexist during rollout, and step-by-step rollback order if a later repository fails.

Keep repository-internal implementation details inside each repository's own Issue rather than duplicating them in the shared cross-repo document.

## Cross-repo release coordination

- Follow the deployment order defined in the approved cross-repo design.
- Each repository still runs its own standard release process via its product-line Release Manager.
- When a feature spans multiple product lines, the feature owner coordinates the respective Release Managers to execute releases in the documented order.
