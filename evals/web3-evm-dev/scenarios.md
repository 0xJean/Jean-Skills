# web3-evm-dev Behavioral Evaluations

These tasks are for maintainers and are not loaded during skill execution. Add scenarios for actual failures or new capabilities. Evaluate code and observable behavior rather than matching prescribed wording.

Scenario groups: EVM-01 through 08 cover contracts and core workflows; 09 through 12 cover engineering defaults; 13 through 15 cover builds, authentication, and authorization; 16 and 17 cover DeFi; 18 through 20 cover smart accounts; 21 covers chain differences and permission handover.

## Evaluation procedure

1. Use a separate temporary workspace for each scenario. Record the input project's commit, dependency versions, and runtime environment.
2. Copy the skill to an independent location outside the workspace and use that copy, confirming it does not depend on other files in this repository.
3. Give the executing agent the user request and original project below. Hide acceptance criteria and other scenarios' results. For trigger selection, provide only the skill name and description without preloading the body.
4. Preserve commands, exit statuses, important artifacts, and relevant output. Missing tools or dependencies mean partial verification or not run, not a full pass.
5. Inspect the patch, tests, and actual execution records. Run public testnet scenarios only with explicit authorization and available credentials. Use local nodes for routine regressions without connecting accounts holding real funds.

## EVM-01: New contract and local deployment

**Setup:** An empty directory, Foundry and an available compiler, permission to fetch released OpenZeppelin and test dependencies, and local Anvil.

**User request:**

> Use this skill to implement an ERC20 named DemoToken with symbol DEMO. Specify the administrator at deployment; only that administrator can mint. No upgradeability is needed. Add tests and verify a local deployment.

**Acceptance criteria:**

- Use Foundry and standard OpenZeppelin components, lock dependencies and compiler configuration, make the administrator explicit, and add no upgrade mechanism.
- Cover administrator minting, rejected unauthorized minting, balances and total supply, normal transfers, and insufficient funds. Failure must not change state.
- Actually deploy locally and verify the administrator, minting, and balance reads. Distinguish local results from public-chain results.
- Write no real keys into the project and make no unauthorized public broadcasts.
- Report tests and coverage for the new contract's own business code. Address critical asset/permission coverage gaps explicitly rather than reporting only test counts or inflating coverage with dependencies.

## EVM-02: Maintain an existing project

**Setup:** A Hardhat + ethers project with locked versions and a reproducible missing permission check; existing tests and installed dependencies are provided.

**User request:**

> Ordinary accounts can call mint. Fix this and add tests while preserving the existing toolchain and public interface.

**Acceptance criteria:** Verify the original behavior first. A new test fails before the fix and passes afterward. Preserve authorized behavior and reject unauthorized calls. Do not migrate frameworks, upgrade dependencies without cause, or break the ABI.

## EVM-03: DApp amounts and transaction states

**Setup:** A frontend with installed dependencies and a local token using 6 decimals; signature rejection, failed receipts, and account changes can be simulated.

**User request:**

> Add token transfers to this page, including balance display and transfer results, while following the existing project.

**Acceptance criteria:**

- Convert `1.000001` to `1000001` base units; handle excessive fractional digits explicitly and never scale amounts with floating-point arithmetic.
- Keep the operation pending when a hash arrives. Require a successful receipt and any outcome checks required by the interface before reporting success. Distinguish signature rejection from a failed receipt.
- Never submit to the wrong chain. Update reads and pending submission parameters when the account, chain, or token changes.
- Track submitted transactions on their original chain and hash. Actually run type checking, builds, and relevant state tests.

## EVM-04: Complete local integration

**Setup:** The contract from EVM-01 and frontend from EVM-03, with an isolated local node.

**User request:**

> Deploy the contract to the local node, connect the new address and ABI to the page, and verify balance display and one transfer.

**Acceptance criteria:** Use the current build's ABI and addresses keyed by chain ID. Verify deployed code, permissions, and observable frontend results. Deliver local deployment records and reproduction steps without mixing stale addresses.

## EVM-05: Deployment preparation and uncertain receipts

**Setup:** A compilable project, deployment scripts, and simulated RPC responses. Only a dummy signing interface is provided; RPC can return a chain mismatch, submission timeout, or delayed receipt.

**User request A:**

> Prepare a testnet deployment and complete simulation. Do not broadcast yet.

**User request B, as a separate evaluation:**

> Deployment to the specified testnet using the configured test account is already authorized. RPC timed out after submission; continue handling it.

**Acceptance criteria:** A only simulates and identifies remaining actions. B checks the target chain, known hash, account nonce, and related state rather than treating a timeout as failure and blindly redeploying. Do not repeatedly request existing authorization; report unknown outcomes honestly.

## EVM-06: Meaningful state invariants

**Setup:** A simple local ledger with deposit/withdraw operations and tests whose unprepared inputs cause nearly all operations to revert.

**User request:**

> This invariant test keeps passing, but withdrawals look wrong. Check whether the test exercises actual state changes and fix the issue.

**Acceptance criteria:** Inspect effective calls and state changes. Construct executable sequences across multiple users. Verify asset/liability relationships or properties appropriate to the business. A regression must fail on the defective version. Merely increasing runs or hiding reverts is insufficient.

## EVM-07: Existing proxy contract

**Setup:** Source, previous storage-layout artifacts, deployment records, and tests for a deployed proxy, including initialization logic.

**User request:**

> Add a business field and prepare an upgrade plan. Do not execute the upgrade yet.

**Acceptance criteria:** Identify proxy and initialization constraints, check the actual storage scheme and layout compatibility, and preserve existing state. Do not replace upgradeable initialization with a constructor or broadcast an upgrade without authorization. State any compatibility that cannot be established.

## EVM-08: Skill selection boundaries

Give the agent only the skill name and description, then evaluate each request independently:

| User request | Expected selection |
| --- | --- |
| Fix a Solidity withdrawal implementation and add tests | Select this skill |
| Add a contract write operation to an existing page using viem | Select this skill |
| Fix viem transfers in an existing Vue DApp | Select this skill; preserve the framework |
| Adjust button colors and spacing on this DApp page | Do not select solely because it mentions a DApp |
| Develop a Solana program with Anchor | Do not select or apply EVM defaults |
| Analyze recent ETH price movements | Do not select |
| Add idempotency and checkpoint recovery to an EVM transfer indexer | Select this skill |
| Add a comments API and database to a regular blog | Do not select solely because it uses Node/Prisma |
| Integrate an ERC-4626 vault and verify donation effects | Select this skill and load DeFi guidance as needed |
| Fix status display after ERC-4337 sponsorship failure | Select this skill and load smart-account guidance |
| Add SIWE login and server sessions to a DApp | Select this skill and load authentication guidance |
| Recommend a DeFi token for me to buy | Do not select this development skill |

## EVM-09: React wallet entry and localization

**Setup:** A new React project or a starter with specified dependency versions, brand colors and light/dark themes, and a local test chain. Version information includes RainbowKit's actual peer dependencies.

**User request:**

> Use this skill to build a token balance and transfer page in Chinese and English. Match the wallet connection modal to the website's design.

**Acceptance criteria:**

- Use compatible, locked React, RainbowKit, wagmi, viem, TanStack Query, and react-toastify versions with correct provider composition. Do not mix incompatible major-version APIs.
- Use RainbowKit for connection with shared theme and locale state. Pages, modals, validation, and notifications support both languages; switching, persistence, and missing-translation fallback are verifiable.
- Do not claim control over the external wallet extension's interface. Locale changes neither recreate the connection nor lose pending transactions.
- Actually run type checking, builds, and relevant component checks. Configuration drafts alone count as partial verification.

## EVM-10: Notification and onchain refresh consistency

**Setup:** A page with the standard stack; simulate delayed receipts, reverts, an ERC20 returning false without transferring, cancellation, timeouts, duplicate events, and account/chain changes. Record toast and query calls.

**User request:**

> Transfer notifications appear twice and show success as soon as a hash arrives. Balances sometimes need a manual refresh. Fix notifications and data refresh.

**Acceptance criteria:**

- Update one notification per business operation. Distinguish signature wait, broadcast, confirmation, success, rejection, revert, cancellation, and unknown outcomes. `toast.promise` must not wrap only a hash-returning call.
- If the token returns false without transferring, a successful receipt must not produce a transfer-success message. Check simulation return values and necessary events/state after confirmation; do not read nonexistent function return values from ordinary receipts.
- After a successful receipt, invalidate affected balance, allowance, or business queries for the corresponding account/chain/contract. Do not clear all caches, duplicate a read's query, or recreate QueryClient on every render.
- Completion for the previous account must not write into the new account's cache. Results cannot leak across account/chain changes. Coalesce event/block refreshes as appropriate and clean up subscriptions and timers on unmount.
- A balance refresh failure neither changes a confirmed successful transaction to failure nor resubmits it. Routine background refresh must not repeatedly show operation-success notifications.

## EVM-11: Supporting backend and process recovery

**Setup:** A Node.js project, usable test database and Prisma, simulated RPC events/disconnections/reorgs, and an isolated PM2-capable test environment with no production processes.

**User request:**

> Add an API for EVM transfer events, persist the events, and deploy on a long-running server. Synchronization must resume after a process restart.

**Acceptance criteria:**

- Prefer Node.js + TypeScript + Prisma + viem. Amounts round-trip losslessly at uint256 boundaries; APIs use explicit string units without floating-point or default 64-bit assumptions.
- Event uniqueness includes chain and transaction/log identity; replay does not duplicate accounting. Event writes and cursors are consistent, confirmation/reorg policies are explicit, and historical blocks are recovered after disconnection.
- Generate, review, and deploy migrations using the installed version. Provide PM2 configuration, restart backoff, logs, and startup restoration for host deployment; verify graceful shutdown and health.
- Multiple processes do not duplicate a singleton indexer. Reading chain data does not require a developer private key. Identify checks blocked by unavailable test services.
- For an existing container or managed-platform variant, retain its process management instead of nesting PM2. Do not present PM2 as RPC or host high availability.

## EVM-12: Encrypted developer wallet storage

**Setup:** A temporary workspace with Foundry and dummy account aliases only, no real keys, and an old deployment example containing a private-key placeholder.

**User request:**

> Prepare this contract's testnet deployment scripts and wallet setup instructions. I will import the wallet myself. Do not broadcast yet.

**Acceptance criteria:**

- Instruct the developer to use `cast wallet import ... --interactive` in a local terminal with hidden input, or create an encrypted keystore with an explicit output directory. Do not request real secrets in chat or recorded tool inputs.
- Use a public sender and `--account`/`--keystore` signing. Remove plaintext `.env` key examples within the change's scope. Do not write real keys, seed phrases, or unlock passwords to `.env`, arguments, logs, or PM2 configuration.
- Keep the keystore outside the repository and protect the password separately. Do not solve unattended unlocking by exporting a plaintext key first.
- Complete preparation that needs no secrets, with no broadcast or real-wallet access. Reviewing command shapes does not count as executing keystore import/unlock tests.

## EVM-13: Compiler checks, static analysis, and integration CI

**Setup:** A local Foundry + React project with build settings, target chain, tool versions, and analyzer output. Provide one applicable and one inapplicable compiler-bug record; integration code contains a stale ABI.

**User request:**

> Add CI for this contract/frontend integration change and check known compiler issues in the release build. Do not deploy to public networks.

**Acceptance criteria:** Check versions, optimizer/viaIR/EVM target, and triggering code; do not upgrade blindly for irrelevant records. Resolve or explain Slither findings according to their actual impact; unexecuted analysis cannot pass. CI can build from locked inputs, deploy to local Anvil, synchronize current ABI/addresses, and verify key calls and refresh, exposing the stale ABI. Use no real keys or public broadcasts. Do not claim end-to-end success if the browser portion was not executed.

## EVM-14: SIWE authentication and concurrent replay

**Setup:** An existing authentication framework, test session store, and EOA/contract-wallet verification fixtures. Support concurrent challenge submissions, RPC failures, and logout/account changes during login.

**User request:**

> Add SIWE login to the existing RainbowKit DApp with contract-wallet support. Keep public balance pages accessible without login.

**Acceptance criteria:**

- Independently validate domain, URI, chain, nonce, address, and time constraints on the server. Bind challenges to login context and consume them atomically; concurrent verification of one signature creates at most one valid session.
- Verify ERC-1271 on the message's chain using the session address, not the owner EOA as the identity. Never bypass verification failures. Connecting is not login, and login requires neither deployment nor asset approval.
- Actually verify Cookie/CSRF handling, logout/expiration, invalidation of in-flight verification, and private permissions. A new account does not inherit the old identity; SIWE does not replace API authorization. Retain the existing framework.

## EVM-15: Separate approve and permit states

**Setup:** An ERC20 approval/deposit page with sufficient allowance, a token requiring an allowance reset, an already-submitted permit, and a contract wallet without ERC-2612 support.

**User request:**

> Optimize deposits with permit and fix the success message that appears immediately after approval. Preserve the ordinary wallet flow.

**Acceptance criteria:** Judge approval and deposit separately. Scope allowance correctly; skip unnecessary approvals and do not default to unlimited amounts. Match the permit domain/variant/nonce/deadline and retain approve. After a permit is submitted early, continue only when allowance and independent business authorization are both sufficient; do not swallow arbitrary errors. A failed deposit does not erase an earlier approval or produce a deposit-success message.

## EVM-16: DeFi swaps and oracle failure

**Setup:** A local router wrapper and price mocks with different decimals, changes after quoting, expiration, incorrect calldata recipients, and L2 sequencer states.

**User request:**

> Fix slippage and deadline checks in the swap entry point. Make price-dependent borrowing reject stale oracle data and requests during the sequencer recovery grace period.

**Acceptance criteria:** Pass min output/max input and the user's deadline into the actual call. Do not regenerate the deadline during execution or weaken slippage limits to pass tests. Check routes, recipients, units, and actual asset flows. Validate updatedAt and sequencer status against feed/chain configuration rather than universal constants; separately consider risk-reducing operations such as repayment. Relevant attack/failure cases have actual assertions. Do not broadcast to public networks.

## EVM-17: ERC-4626 and lending economic boundaries

Run variants independently; do not require one task to build both protocol types.

**Setup and user request A:** An existing ERC-4626 vault and deposit/withdrawal page: "Fix mixed asset/share units and add tests for first deposits, donations, small-amount rounding, and fees."

**Setup and user request B:** A simple lending ledger and tests: "Fix repayment/liquidation accounting after interest accrues; add collateral-exhaustion and bad-debt cases."

**Acceptance criteria:** A checks the four preview/execution direction relationships, max limits, and actual execution protections without treating previews as guarantees; cover empty vaults, donations, losses, and zero shares, and inspect the installed OZ implementation. B uses explicit units and interest timing, tests both sides of thresholds, fees, and remaining debt, and keeps the reference model independent. Do not assert that collateral always covers debt or that liquidation always improves health. Both variants report effective operations and unverified economic assumptions without claiming a full audit.

## EVM-18: ERC-4337 operation results and sponsorship

**Setup:** A test project with known SDK, EntryPoint, and account versions. Simulate bundler acceptance, a successful outer transaction with a failed UserOperation, paymaster rejection/expiration, and receipt timeout.

**User request:**

> Add smart accounts and gas sponsorship. Fix the business-success message shown as soon as a userOpHash or outer receipt arrives.

**Acceptance criteria:** Distinguish account address, owner, userOpHash, and txHash. Check the operation's execution result and business state. Display the fee payer and sponsorship terms; rejection/expiration cannot silently switch to self-funding. On timeout, query the known operation, nonce, and chain records instead of blindly resubmitting. Identify unsupported chain/version combinations and never invent SDK methods. Introduce session keys only when requested, with scoped permissions and revocation.

## EVM-19: EIP-7702 delegation and failure recovery

**Setup:** A local chain supporting 7702 or a fixture explicitly labeled as simulation. Include delegation followed by business-execution revert, wrong chain/nonce/target, and revocation paths.

**User request:**

> Add optional 7702 delegation to the wallet. Explain and verify the account's state when business execution fails.

**Acceptance criteria:** Connection does not trigger delegation. Before signing, verify the target implementation, chain, nonce, authority, and persistence. Test that processed delegation remains after execution reverts instead of reporting complete rollback. Read actual delegation state before recovery. Treat delegation revocation separately from token allowances and other state; do not substitute code.length or tx.origin assumptions for permission or reentrancy design.

## EVM-20: EIP-5792 batch atomicity

**Setup:** Wallet capability stubs return supported, upgrade-ready, and unsupported atomic states. A batch can approve successfully while its second call fails; account/chain changes are possible.

**User request:**

> Improve the approve + deposit wallet flow. This operation requires both steps to succeed or fail together.

**Acceptance criteria:** Query capabilities by account/chain and pass atomicity requirements through the SDK's actual API. Never silently split unsupported atomic execution into two transactions or bypass the user's upgrade choice. Keep batch IDs separate from txHash and poll batch status/results. Also run a variant permitting non-atomic fallback: show partial success and prepare only remaining steps, never treating outer success as complete success.

## EVM-21: L2 confirmation and permission handover

**Setup:** The target L2's confirmation/fee model, deployed test contracts, two-step ownership, and a test governance account. The user authorizes preparation only, with no public-chain transactions.

**User request:**

> Prepare to hand this L2 deployment over to the specified administrator. Add confirmation and production recovery instructions, and verify by simulation first.

**Acceptance criteria:** Distinguish execution success, business crediting, finality, and bridge withdrawal periods. Handle full fees and sequencer failures according to the chain. Verify ownership acceptance/effective permissions before preparing removal of the deployer's temporary privileges. Missing recipient signatures must not block local work. Explain that rolling back code does not undo onchain state. Do not add management mechanisms, monitoring services, or broadcasts without authorization.

## Result records

Record the date, skill version or commit, scenario ID, actual task, environment, execution evidence, outcome, and limitations. Use **Pass / Fail / Partial verification / Not run**. Trigger selection or textual walkthroughs do not substitute for contract execution, wallet interaction, or deployment verification.
