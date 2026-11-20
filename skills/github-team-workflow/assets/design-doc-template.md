# Design Doc: Short Feature Title

- **ID:** `NNNN`
- **Status:** `Draft` (`Draft` | `In Review` | `Approved` | `Implemented`)
- **Author:** `@handle`
- **Reviewers:** `@reviewer-1`, `@reviewer-2`
- **PRD / Product Tracker:** `<prd-url>`
- **Tracking Issues:** `#<issue-id>` (list one per affected repository for cross-repo designs)

## 1. Background and Context

Summarize the problem being solved, relevant user or system context, and link to the product PRD.

## 2. Goals and Non-Goals

### Goals
- Measurable outcome 1
- Measurable outcome 2

### Non-Goals
- Explicitly out-of-scope item 1

## 3. Proposed Design

Describe the architecture, data flow, state transitions, API or event contracts, and schema changes.

## 4. Alternatives Considered

Summarize alternative approaches that were evaluated and why they were not selected.

## 5. Impact Scope

| Repository | Responsibility | Tracking Issue | Schema / API Impact |
| --- | --- | --- | --- |
| `<repo-name>` | `<summary>` | `#<id>` | `<none / additive / breaking>` |

## 6. Rollout and Rollback Plan

1. **Deployment order:** Specify repository/service order and backward-compatibility requirements during mixed-version rollout.
2. **Feature flags and config:** List new flags, defaults, and required environment variables.
3. **Database migrations:** Explain expand/contract steps and whether migrations are safely reversible.
4. **Rollback procedure:** Document exact steps to revert safely if production metrics degrade.

## 7. Risks and Mitigations

| Risk | Likelihood / Impact | Mitigation |
| --- | --- | --- |
| `<risk>` | `<low/med/high>` | `<mitigation>` |

## 8. Acceptance Criteria

- Verifiable functional and non-functional criteria required before closing the feature.
