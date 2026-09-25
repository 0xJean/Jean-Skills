# Testing strategy and failure diagnosis

Use this reference to validate changed contract behavior, regression fixes, external integrations, or contract-to-DApp flows. Choose test levels that verify business rules; do not add every test type to every task.

## Select the scope

| Change or risk | Preferred validation | Expected evidence |
| --- | --- | --- |
| New or modified entry point | Unit tests | State changes, return values, events, and relevant failure paths |
| Known bug fix | Minimal regression case | Reproduces the bug before the fix and passes afterward |
| Amounts, fees, or boundary calculations | Parameterized or fuzz tests | Business relationships and limits hold across inputs |
| Multiple users and asset operations | Stateful invariant tests | Conservation or permission invariants hold after valid sequences |
| Integration with a deployed protocol | Fork tests at a fixed block | Expected behavior against real code and state |
| Wallet or transaction UI | Frontend state tests and local integration | Displayed state agrees with transaction outcomes |

For documentation, formatting, or changes without business effects, use the relevant checks only. Run the smallest affected test set first, then required related regressions and CI checks. Do not repeatedly expand testing without a new concern.

For [DeFi](defi.md), [smart accounts](smart-accounts.md), or [wallet authentication](authentication.md), select business assertions from the corresponding reference. Do not add those test fixtures to projects that do not use the mechanisms.

## Contract completion criteria

- Each external business operation in a new contract should have traceable tests for expected success, applicable authorization failures, boundaries, and state after failure. For existing contracts, cover affected paths and regressions.
- A single happy-path case is insufficient for critical asset, permission, initialization, or signature-replay branches. Verify each applicable path. Do not duplicate the complete OpenZeppelin test suite for unchanged inherited internals; test your configuration, overrides, and composition.
- For new contracts or substantial logic changes, run `forge coverage --report summary` or the existing framework's equivalent. Inspect function, line, and branch gaps in your business code. Report important gaps, reasons, and remaining checks; test counts or a single coverage percentage do not establish sufficiency.
- Preserve existing repository coverage thresholds. Do not invent a project-wide 100% target when none exists. Add tests for uncovered critical asset or permission behavior, or explicitly mark it as not yet verified.
- Coverage instrumentation may use different compiler settings from the deployment build. Compilation and tests must also pass with the target configuration; do not silently change deployment settings to satisfy coverage tooling.

## Unit tests and regressions

- Derive assertions from requirements rather than repeating the implementation's calculations. Business rules determine balance changes, authorization boundaries, consumption counts, and recipients.
- Cover authorized success and unauthorized failure. When fixing mint permissions, preserve valid minting; test failure after revocation when the project supports revocation.
- Where supported, assert the specific error and its arguments instead of merely expecting some revert. Also verify that relevant state was not changed incorrectly.
- For asset operations, check the relationship between payer, recipient, and protocol accounting. For event-dependent UIs or indexers, check event fields and the emitting contract.
- Select zero, minimum valid values, upper limits and adjacent values, insufficient balance, or insufficient allowance according to the interface contract. Do not assume every zero value is invalid.
- For time or signatures, cover expiry boundaries, invalidation, and reuse. For external calls, use focused mocks or adversarial receivers to exercise failures, callbacks, and reentrancy paths.
- Confirm tests call the intended contract and actual business entry point. Proxy behavior tests should generally call through the proxy rather than only testing the implementation.

## Fuzz tests: explore input space

- Constrain inputs to the business domain while retaining meaningful extremes. Explain why constraints are valid; do not filter away inputs that expose a bug.
- Prefer the framework's range helpers for contiguous valid ranges. When filtering with assumptions, inspect discard rates to ensure useful samples remain.
- Consider both values and address roles, including whether payer, beneficiary, and caller may be the same.
- Preserve reproducible inputs or seeds after finding a counterexample, and add a small, explicit regression where practical. Do not simply increase random runs and try again.

## Invariant tests: explore operation sequences

Introduce these tests when state relationships warrant repeated checks. Define invariants in business terms, then select targets, actors, operations, and input generation.

- Examples include the relationship between summed balances and supply, unauthorized actors never minting, or a consumed claim never paying again. Define the applicable model first for systems with fees, debt, or external balance changes.
- Put complex operation preconditions in a handler where useful. Ensure it actually calls the target contract rather than only updating a test-side ledger.
- Use independent test-side reference state when accumulation is needed, avoiding duplication of the same faulty formula as the implementation.
- Inspect calls, successes, reverts, and discards for each operation type. Confirm that important state transitions occurred.
- Foundry invariant runs may allow reverts; inspect the current `fail_on_revert` setting. Many failed calls do not imply meaningful exploration.
- For handlers whose calls should all be valid, consider failing on revert and separating or explicitly asserting expected failure paths. This is not a universal requirement for every invariant suite.
- Avoid conditional early returns that skip all assertions. If different states need different constraints, assert each state meaningfully or use separate scenarios.
- Random run counts do not validate the test harness. First execute a deterministic valid sequence and confirm that handlers, counters, and assertions observe it.
- Minimize failing sequences and preserve a replay method. Report actual runs, depth, and coverage of effective operations; do not treat these counts as a security rating.

## Fork tests: verify external dependencies

- Use forks only when real protocol code or chain state is needed. Local unit tests should run independently.
- Pin the chain ID and block number, and record dependency addresses. To reproduce historical behavior, check the implementation version and available state at that block.
- Read endpoints from existing project RPC configuration. Do not expose credential-bearing URLs in output or reports; confirm that the RPC supports the required historical state.
- Distinguish local impersonation, balance changes, and time manipulation from real-chain behavior. Modified test state does not prove possession of production permissions or assets.
- Assert business boundaries such as received amounts, fees, or state changes. A call that does not revert is usually insufficient evidence of correctness.
- RPC rate limits or unavailable archive data are environment failures. Preserve the cause, do not mark skipped fork tests as passing, and do not send real transactions as a workaround.

## Static analysis for contract changes or releases

- Run existing project checks first. For new contracts, substantial asset or permission changes, or release preparation without an existing analyzer, prefer a compatible Slither version. Record the tool version, analysis scope, and build configuration.
- Assess each finding's reachable paths and business impact, fixing applicable issues. Document the basis for false positives or accepted constraints. Do not disable checks globally to make CI pass; unrelated historical findings may use an explicit baseline.
- Results must correspond to the actual source and deployment compiler configuration. Missing tools, compilation failure, or unsupported features mean analysis is incomplete, not that no issues were found. Analysis does not replace business tests or an audit conclusion.

## CI and integration across layers, when relevant

- Reuse existing CI. For a new pipeline, pin toolchains and dependencies and use the project's formatting, compilation, testing, and type-checking commands. Integrate static analysis as above. State RPC requirements for fork jobs and distinguish them from tests that can run offline.
- When changing contract-to-DApp integration or building its CI, provide a repeatable critical path: start isolated Anvil, deploy the current source, export the current ABI and addresses, perform the target reads and writes, then verify receipts, notifications, and targeted refreshes. Use local test accounts and clean up nodes created for the run.
- Select relevant failure cases, such as missing addresses, stale ABIs, transaction reverts, or account switches. Component tests and script calls are not real-wallet end-to-end tests; record the actual evidence at each layer.
- CI must not contain real developer keys or broadcast to public networks by default. If an external RPC is unavailable, report the job as not run or failed rather than silently skipping it and claiming a full pass.

## Execution and diagnosis

Use repository scripts and installed tool versions. First inspect test configuration for implicit RPC access, FFI, external scripts, or other side effects. Do not automatically change the global toolchain to run a check.

Foundry projects can use these verified basic commands. Replace the example path with a real test file and confirm how many tests the filter actually selected:

```bash
forge test --match-path 'test/MyContract.t.sol' -vvv
forge test
```

On failure, inspect the first relevant revert, caller, arguments, and preconditions before classifying it as a contract bug, harness issue, or environment problem. Do not weaken assertions or increase error tolerances merely to make tests pass.

Compare gas under consistent compiler settings when the task concerns gas optimization. Coverage helps locate untested paths but cannot replace business assertions. See [DApp interaction](dapp.md) for wallet switching, themes and languages, notification deduplication, precision, and targeted refresh after confirmation; see [backend development](backend.md) for APIs, Prisma migrations, indexer idempotency, and PM2 recovery.

Report the commands actually run, their scope, outcomes, and unverified items. Compilation, unit tests, fork tests, and real deployment verification provide different evidence and cannot substitute for one another.

## Official references, matched to the installed version

- [Foundry Tests](https://getfoundry.sh/forge/tests): test discovery, filtering, and failure traces; check local help before using commands.
- [Foundry Invariant Testing](https://getfoundry.sh/forge/invariant-testing?highlight=invariant): targets, handlers, depth, and how reverts affect meaningful exploration.
- [Foundry Fork Testing](https://www.getfoundry.sh/guides/fork-testing): fixed blocks, impersonation, and fork environments.
- [Slither](https://github.com/crytic/slither) / [Slither Action](https://github.com/crytic/slither-action): static analysis and CI integration; match options to the installed version.
- [Foundry Toolchain Action](https://github.com/foundry-rs/foundry-toolchain): pinning CI toolchains. The integration workflow above is this skill's engineering convention; adapt it to the project.
