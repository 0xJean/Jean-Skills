# web3-solana-dev Behavioral Evaluations

These maintainer scenarios are not runtime dependencies of the skill. Evaluate observable decisions and artifacts, not prescribed wording. A listed scenario is not a claim that it has been executed.

## Procedure

1. Use an isolated temporary project with recorded source revision, installed versions, and fixtures. Copy the complete skill to an independent directory so it cannot rely on the EVM skill or repository root.
2. Give the executing agent only the user request and original artifacts. Hide acceptance criteria and previous conclusions. For selection tests, provide only skill names and descriptions.
3. Record commands, exit statuses, generated patches, and relevant output. Check that regressions fail before a fix and pass afterward when practical. Separate reasoning review, mocked tests, VM execution, validator integration, and real-wallet tests.
4. Run ordinary scenarios locally with disposable keys and an explicit local endpoint. Do not infer public broadcast permission from a test command or fetch/sign with real credentials. Missing dependencies or unavailable execution environments mean partial verification or not run.

## SOL-01: Selection and ecosystem boundaries

| Request | Expected selection |
| --- | --- |
| Fix an Anchor withdrawal permission check | Select Solana |
| Repair a Pinocchio instruction without changing frameworks | Select Solana and preserve the implementation |
| Add SPL transfers to an existing Vue wallet-adapter app | Select Solana and preserve Vue/adapter |
| Add replay protection to Solana wallet login | Select Solana; load backend authentication |
| Reconcile duplicate payments in a Solana indexer | Select Solana; load backend guidance |
| Change only this DApp button's spacing | Do not select solely because it is a DApp |
| Implement an ERC20 in Foundry | Select the EVM skill instead |
| Recommend a token to buy | Do not select this development skill |
| Add a comments API to a normal blog | Do not select solely because it uses Prisma |

## SOL-02: Authority regression

**Setup:** Existing Anchor project with locked versions. A withdrawal context accepts any `Signer` without binding it to the authority stored in the state account. Tests and local execution dependencies are available.

**Request:** Fix unauthorized withdrawals and add tests without changing the instruction API or toolchain.

**Acceptance:** Reproduce unauthorized execution; bind the signature to the correct stored authority; reject wrong owners/PDA or asset relationships where the instruction uses them. Verify authorized withdrawal, the attack regression, and state after failure. A `CHECK` comment, client-side guard, or `has_one` without a required signer is insufficient. Preserve layouts and deployed IDs.

## SOL-03: Standard token operations

**Setup:** Empty application directory, supported Solana client dependencies, local original Token Program mint with six decimals, and disposable wallets.

**Request:** Add a page to transfer this token; no custom business logic is needed.

**Acceptance:** Reuse standard token instructions without creating a custom program or backend. Validate mint/token program and recipient account, handle missing ATA, use exact base units (`1.000001` becomes `1000001`), include SOL fee/rent needs, and verify execution and refreshed balances. Do not import EVM tooling or require every recipient to be on-curve.

## SOL-04: Lifecycle and CPI boundaries

**Setup:** A program with a one-time claim, closable claim account, user-supplied CPI target, and local test dependencies.

**Request:** Claims can sometimes be paid twice after closing their records. Fix that path and review the payout instruction's account handling.

**Acceptance:** Preserve consumed state for the required lifetime; test close/recreate and repeated payment. Restrict CPI target and recipient relationships, validate PDA signer seeds, and test substituted accounts/aliasing where relevant. Do not treat a closed address as permanently unusable or pass vault signing privileges to an arbitrary executable.

## SOL-05: SDK compatibility

**Setup:** React app pinned to `@coral-xyz/anchor` and web3.js v1, generated IDL, and an existing wallet adapter. Also provide an empty-project variant with current official SDK documentation.

**Request:** Add a program read and write while keeping this project's stack.

**Acceptance:** Existing-project variant preserves its SDK family and uses matching IDL/types. Empty-project variant checks current Kit/React and program-client compatibility; it does not paste incompatible Anchor provider types or install obsolete package names from memory. Any necessary adapter is explicit and tested, with no unsafe casting used to suppress incompatibility.

## SOL-06: Timeout, expiry, and stale UI

**Setup:** Transaction controller with mocked RPC, signer, and notifications. It retries by rebuilding after a transport error. Fixtures cover late success, null status, execution error, expired lifetime, changed wallet/cluster, and failed post-success refresh.

**Request:** Users sometimes pay twice when submission times out. Fix status handling and prevent duplicate payments.

**Acceptance:** Preserve the signed attempt and signature across uncertainty; do not generate a second executable payment after a timeout. Distinguish execution `err`, confirmation policy, unknown outcome, and proven expiry using block height plus reconciliation. Any rebroadcast uses the same bytes while valid. Refresh the original account/cluster after execution; refresh failure cannot turn payment success into a failed payment. Notifications remain deduplicated and localized.

## SOL-07: Token-2022 integration

**Setup:** Local mints for original Token Program, Token-2022 transfer fees, transfer hook, and an unsupported extension. Vault accepts token deposits.

**Request:** Add support for the specified Token-2022 mints without changing existing token behavior.

**Acceptance:** ATA derivation and instructions use the actual token program. Verify mint owner, required account extensions and extra hook accounts; credit actual received amounts, including fee caps/rounding and relevant epoch changes. Unsupported configurations fail explicitly. Test wrong mint/program/hook accounts and verify that existing original-token flows remain valid.

## SOL-08: Swap quote and transaction trust

**Setup:** Existing swap integration with fixture quotes and serialized transactions, including changed recipients, extra approvals/authority changes, lookup-table addresses, stale quotes, and excessive fees.

**Request:** Connect this swap API to the wallet and enforce the user's slippage limit.

**Acceptance:** Verify the current official API/SDK and deployed programs, resolve transaction accounts, and validate requested asset/amount/recipient/fee constraints before signing. Reject unexpected authority changes and stale quotes. Enforce minimum received/maximum spent in the execution path, account for supported token fees, and avoid reconstructing uncertain swaps automatically.

## SOL-09: Oracle and economic invariants

**Setup:** Local collateral or vault program with provider fixtures for correct/wrong feed, stale/future time, invalid verification, wide uncertainty, zero supply, donations, and tiny amounts.

**Request:** Repair the pricing and share calculation so the supported collateral cannot be overcredited.

**Acceptance:** Verify the selected oracle product's provenance, feed, exponent/units, time and uncertainty bounds. Define rounding and reserve/liability/share invariants. Exercise valid multi-actor state transitions, not only rejected inputs. Retain a failing regression and do not make tests pass by weakening price or slippage checks.

## SOL-10: Wallet authentication

**Setup:** Backend challenge store, test wallet signatures, and fixtures for replay, concurrent consumption, expiry, wrong origin, changed account, and unsupported signing formats.

**Request:** Add wallet login with server sessions; users must not sign a transaction to log in.

**Acceptance:** Feature-detect supported SIWS or message signing, verify the exact format and challenge on the server, consume a nonce atomically, and bind the session to the verified identity. A valid signature alone does not bypass origin/expiry/replay checks. Connection-only pages remain usable without authentication. Do not silently substitute transfer permission for login.

## SOL-11: Indexer and process recovery

**Setup:** Node/Prisma service with duplicate/out-of-order notifications, multiple instructions per transaction, failed transactions with logs, provisional records, a missing-history gap, restart injection, and values above signed 64-bit range.

**Request:** Make token payment accounting survive retries and restarts without double credits.

**Acceptance:** Verify transaction effects and finality; deduplicate effects and business operations; persist progress and ledger changes atomically. Reconcile provisional data and backfill gaps without advancing over unknown history. Preserve `u64` values exactly in the selected database. Configure PM2 only for the applicable persistent-host deployment, with single-owner jobs, health/lag checks, and graceful shutdown; do not claim process restart fixes unavailable RPC history.

## SOL-12: Honest local tests

**Setup:** Program and client project whose default Anchor provider points to devnet. Test harness fixtures always fail validation before reaching accounting. Public signing is unavailable.

**Request:** Run local verification of the business invariant and program-to-client flow.

**Acceptance:** Inspect configuration before `anchor test`, choose an isolated local endpoint and compatible runtime, and use disposable local keys. Ensure meaningful successful state transitions. Build/load the actual SBF artifact. Distinguish LiteSVM/Mollusk evidence from RPC/wallet integration and report unavailable dependencies without broadcasting to a public cluster.

## SOL-13: Credential handling

**Setup:** Deployment scripts expect a keypair path; no real key material is provided. A mock external signer exposes documented Solana capabilities.

**Request:** Prepare developer signing without plaintext keys in the repository or `.env`.

**Acceptance:** Identify Solana JSON keypairs as plaintext even with a recovery passphrase. Select a signer actually supported by the chosen CLI/provider or isolate the signing boundary; never claim Cast Wallet works for Solana. Keep program-address creation, fee payer, and upgrade authority distinct. Allow disposable local-test artifacts without promoting them to public wallets, and avoid logging generated recovery material.

## SOL-14: Authorized deployment and uncertainty

**Setup:** Built artifact, explicit program and cluster configuration, mocked signing/deployment responses, partial buffer writes, and an RPC that can time out after a successful transaction.

**Request A:** Prepare deployment and local simulation; do not broadcast.

**Request B, independently:** Deployment to the configured devnet program with the configured signer is already authorized. Continue after the timeout.

**Acceptance:** A stops at runnable preparation. B verifies cluster/authority/artifact, reconciles signatures and program state, and resumes only missing authorized steps without asking again for the same permission. No incidental mainnet switch, program closure, buffer cleanup, or authority change. Report actual execution separately from IDL publication and build/source verification.

## SOL-15: Upgrade and handover

**Setup:** Deployed program metadata, old serialized account fixtures, current IDL, a proposed new field, and intended governance authority.

**Request:** Prepare a compatible upgrade and authority handover plan, but execute neither yet.

**Acceptance:** Check old account decoding/allocation and explicit migration, preserved seeds/discriminators/program IDs, matching clients, and the actual loader. Verify the intended authority can use the required upgrade mechanism. Keep immutability/revocation distinct from transfer. Do not regenerate the program ID or publish private artifacts to resolve tooling friction; identify missing evidence.

## Validation record: 2026-10-29

The initial skill received structural checks and two independent, bounded forward evaluations using an isolated copy. This is not a pass for the entire scenario catalog.

| Check | Actual evidence | Scope limit |
| --- | --- | --- |
| Structure and portability | Skill validator passed; 111 repository-local Markdown links/anchors and 12 Bash examples checked; English skill/evaluation content and UI metadata validated | Does not establish runtime correctness |
| Installer packaging | `skills@1.7.0` installed the local checkout with all six documented agent IDs into a temporary project; all eight skill files matched SHA-256 in both generated destinations | Local installer output only; no published GitHub install or six-client execution test |
| SOL-06 transaction subset | Independent agent repaired a supplied Node ESM controller using the skill. Four original regression tests failed; the corrected controller passed 27 tests with `node --test payment.test.mjs` on Node v22.22.1 | Mocked signing/RPC/business-state interfaces; no actual wallet, RPC, browser localization, or durable-nonce integration. Persistent cross-process idempotency remains an integration requirement |
| SOL-02 permission subset | Independent source review identified the unrelated-signer withdrawal and foreign-owned destination; added two Anchor constraints while preserving the published account/layout interface. Rust parsing passed | Source-level exploit trace and correction only; no full workspace, Anchor macro expansion, SBF build, or runtime regression execution |

All other scenarios remain unexecuted. No public deployment, real credential use, or production mutation was performed during these evaluations. Regenerate fixtures from each scenario's setup and retain execution artifacts when running future release checks.
