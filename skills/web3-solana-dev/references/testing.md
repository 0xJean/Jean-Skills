# Solana testing and debugging

Use for business logic validation, regressions, program integrations, and transaction flows. Select checks for the actual change; documentation or styling work does not require a program test suite.

## Select evidence by layer

| Concern | Suitable test environment | What it does not establish |
| --- | --- | --- |
| Pure accounting or encoding | Rust/TypeScript unit and property tests | Real instruction execution or runtime account checks |
| Instruction behavior and compute | Mollusk with explicit accounts and program artifacts | RPC services, wallet signatures, or validator behavior |
| Stateful transaction sequences and CPI | LiteSVM with deployed artifacts and dependencies | Public-network propagation, RPC subscriptions, or finality |
| Generated clients, RPC, and account subscriptions | Isolated local network using the project's configured backend | Public-cluster congestion or production permissions |
| Wallet UX and confirmation lifecycle | UI state tests plus local integration or a scoped wallet test | A mocked wallet alone is not a real-wallet end-to-end test |
| External protocol compatibility | Pinned program/account fixtures and a suitable local runtime | A fixture is not a full historical Solana fork |

Preserve existing test infrastructure. For new tests, use LiteSVM for fast transaction/state workflows or Mollusk for focused instruction execution as appropriate; do not install both without a need. Match their Solana SDK, feature set, dependencies, sysvars, and compiled program format to the target. Mollusk requires explicit accounts and does not run a validator; carefully validate any simulated signer or transaction-level assumptions through a transaction-capable layer.

## Program coverage requirements

- Cover each new business instruction's intended success, relevant authorization failures, invalid account relationships, amount boundaries, and state after failure. For a focused fix, add a regression and affected-path tests.
- Include applicable substitutions: wrong signer, non-signing authority, wrong owner/type, wrong mint/token program, wrong PDA seeds/bump, unexpected CPI target, duplicated account roles, malformed `remaining_accounts`, and read-only accounts supplied where mutation is needed.
- Test lifecycle boundaries: double initialization, close/recreate, account resizing, authority changes, expired or consumed business operations, and migration from representative old data. Do not add these fixtures to instructions that cannot exercise them.
- Assert intended errors and balance/state effects. A failing transaction must leave business state unchanged, but its fee payer can still pay a transaction fee; do not assert every lamport balance is identical after a submitted failure.
- For CPI, execute the real dependent program when validating integration behavior, and use adversarial programs or fixtures for caller-controlled targets and failure paths. Confirm tests load the intended binary and program ID.
- Preserve existing coverage thresholds. Where the installed toolchain supports source or branch coverage, inspect relevant gaps, but state which target and instrumentation were measured. Host Rust coverage alone does not prove sBPF execution coverage. A test count or a single percentage does not establish meaningful asset/permission coverage.

## Properties and operation sequences

Use property-based or fuzz testing where arithmetic, arbitrary accounts, or repeated operations create useful input space. Retain boundary values and failing seeds; do not filter away failures to make a suite pass.

For stateful programs, define business invariants such as assets covering liabilities, supply matching issued shares, only authorized actors changing config, and a claim paying at most once. Drive actual instructions with multiple actors and track success/failure counts. First run a deterministic valid sequence to confirm the harness reaches the business state. An input generator that always fails account validation provides little evidence of downstream correctness.

For financial programs, test rounding, zero-supply entry, tiny deposits, donation effects, fees, stale or invalid oracle updates, and the supported Token-2022 combinations described in [tokens and DeFi](tokens-defi.md). Bound compute under realistic maximum data/account sizes.

## Local networks and external fixtures

- Inspect `Anchor.toml`, package scripts, environment, and local test configuration before execution. `anchor test` can deploy to its configured cluster; do not assume the command always stays local. Select an isolated local configuration and disposable test signers for routine tests.
- Check installed CLI help for the local backend and flags. Anchor releases may use Surfpool or `solana-test-validator`; an existing validator or a skip flag does not by itself prove the tests will hit the intended endpoint.
- Record cluster, program IDs, capture slot/context, binary hashes, dependency accounts, and fixture provenance for externally sourced state. Ensure related accounts are coherent; independent reads may reflect different slots. Do not present arbitrary account cloning as an exact historical fork.
- Include executable programs and necessary loader/program-data dependencies when the harness needs them. RPC endpoints may not provide historical account snapshots or old program binaries; state missing evidence explicitly.
- Manipulating clock, slot, balances, or signatures in a local harness does not demonstrate production capabilities. Test runtime-dependent features against the intended environment.
- RPC failures and missing dependencies are failed or unexecuted checks, not passing tests. Do not send public transactions to compensate for unavailable local tooling.

## Integration, CI, and diagnosis

- Reuse repository scripts and pin the Rust, Solana/Agave, Anchor, package-manager, and SDK versions used in CI. Commit appropriate lockfiles. Build the actual deployment target as well as host test code.
- Run formatting, applicable Clippy/lint/type checks, compilation, targeted regressions, and required repository checks. Rust dependency checks such as `cargo audit` or `cargo deny` can find dependency issues when configured, but do not replace program-specific validation or establish an audit conclusion.
- Keep public-cluster signing and deployment outside ordinary test jobs. CI signers should be disposable or explicitly provisioned for an authorized deployment job. Never log keys or credential-bearing RPC URLs.
- For program-to-DApp integration, build current source, deploy to an isolated local endpoint, generate matching IDL/clients, perform a read and write, verify onchain results, and confirm notifications plus targeted cache refresh. Include program-ID/cluster mismatch and account-switch cases when affected.
- Inspect the first relevant instruction error, program logs, failing instruction index, account metadata, compute use, and preconditions. Distinguish a program regression from an SDK mismatch, stale binary/IDL, missing fixture, or RPC environment issue. Do not weaken assertions or increase slippage/tolerances simply to pass.
- Report commands actually run, selected tests, outcomes, measured compute/coverage where relevant, and unresolved gaps. Clean up only the local processes created for the test.

## Official references

- [Anchor LiteSVM guide](https://www.anchor-lang.com/docs/testing/litesvm): in-process transaction testing and supported languages.
- [Anchor Mollusk guide](https://www.anchor-lang.com/docs/testing/mollusk): instruction execution, account fixtures, sysvars, and feature sets.
- [Anchor CLI](https://www.anchor-lang.com/docs/references/cli): test/deployment behavior and version-specific tooling.
- [Anchor configuration](https://www.anchor-lang.com/docs/references/anchor-toml): cluster, script, and local network settings.
- [Solana transactions](https://solana.com/docs/core/transactions): atomic execution and transaction fees.
