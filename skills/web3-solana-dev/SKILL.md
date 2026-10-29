---
name: web3-solana-dev
description: Build, modify, test, and debug Solana programs, DApps, and supporting backends. Use for Anchor or native Rust programs, SPL tokens, DeFi integration, wallet transactions, and deployment; exclude EVM development, trading advice, generic APIs, and styling-only changes.
---

# Solana Program and DApp Development

Deliver verified changes for the requested Solana task. Choose the program, frontend, backend, or deployment workflow needed; a focused fix does not require a new application or a general audit. Respond in the user's language and preserve the project's product locales.

## Identify the project

- Inspect repository instructions, Cargo and JavaScript manifests/lockfiles, Anchor configuration, IDLs, generated clients, tests, and deployment records. Determine the cluster, program IDs, deployed account layouts, authorities, and supported token programs before changing an integration.
- Choose technology in this order: explicit user requirements, existing project constraints, then the defaults below. Preserve native Rust, Pinocchio, existing Anchor versions, wallet-adapter, web3.js, or non-React frontends when maintaining them. Do not turn a small fix into a migration.
- Check installed versions, types, and CLI help before choosing APIs. Solana SDKs, Anchor's Rust/CLI/IDL/client packages, and local execution environments have compatibility boundaries. Consult the matching official documentation when adding dependencies or resolving uncertainty; lock compatible versions rather than installing each latest package independently.
- Infer scope from the task and project. Ask only for missing decisions that change behavior, asset handling, or authorized public actions. Do not create a custom program when existing System or SPL Token instructions meet the requirement.

## New-project defaults

| Area | Convention |
| --- | --- |
| Programs | Rust + Anchor for custom business logic; reuse maintained SPL programs and compatible Anchor libraries; preserve explicit native-program choices |
| Frontend | React + TypeScript; Wallet Standard wallet discovery/connection; prefer compatible Solana Kit clients and React bindings for new integrations |
| SDK compatibility | Check the selected Anchor client before choosing a JS stack; isolate legacy web3.js types or generate a compatible client from the matching IDL |
| Experience | react-toastify lifecycle notifications; shared app/wallet-entry themes and locales; default to switchable `zh-CN` and `en-US` when unspecified |
| Onchain data | TanStack Query for cached reads and targeted refresh, reusing the chosen SDK's Query integration when available |
| Optional backend | Node.js + TypeScript + Prisma + compatible Solana SDK; PM2 on persistent hosts; create a service only for required persistence, indexing, or controlled APIs |
| Verification | Program behavior and negative authorization tests, numeric boundaries and applicable invariants, plus local integration for RPC/wallet/client behavior |
| Real signing credentials | Hardware or external signing with verified tool support, or an approved encrypted custody workflow that does not export plaintext keys; no plaintext keypair files or real secrets in `.env`, source, or output |

These are collection conventions, not universal Solana requirements. Choose the React framework, i18n library, test harness, and signer integration to fit the task. Solana's usual JSON keypair file is plaintext; a seed recovery passphrase does not encrypt that file. Disposable local-test keys have a separate, limited role described in [deployment](references/deployment.md).

## Read by task

| Work | Reference | Decisions it supports |
| --- | --- | --- |
| Create, modify, or review program logic | [Programs](references/programs.md) | Accounts, ownership, signers, PDAs, CPI, state compatibility, and compute limits |
| Reproduce bugs or verify behavior | [Testing](references/testing.md) | Local harness choice, adversarial accounts, economic invariants, and integration checks |
| Connect wallets or read/write accounts | [DApp](references/dapp.md) | SDK compatibility, precise amounts, transaction states, localization, and refresh |
| APIs, indexing, sessions, or service operations | [Backend](references/backend.md) | Persistence, replay/recovery, Sign In With Solana, and process management |
| Tokens, swaps, vaults, or lending | [Tokens and DeFi](references/tokens-defi.md) | Token program selection, extensions, authority, slippage, and oracle/accounting checks |
| Deploy, upgrade, or change authorities | [Deployment](references/deployment.md) | Signers, cluster and artifact identity, verified builds, and actual execution results |

Load only relevant references. Wallet connection does not imply authentication, token transfers do not imply a custom program, and ordinary DApps do not require multisig or DeFi infrastructure. All reference paths are local to this skill; it can be installed independently of the collection and EVM skill.

## Implement and verify

1. Define the observable change: instructions, account relationships, authority, asset units, state transitions, and failure behavior. For a bug, reproduce the failure before fixing it.
2. Implement within existing interfaces. Solana callers supply accounts: validate their identity and relationships, not only their serialized shape. Preserve deployed layouts, PDA derivation, program IDs, and client compatibility unless a migration is in scope. Keep token-program and mint information in both onchain checks and clients.
3. Test affected behavior. Cover unauthorized and substituted accounts as well as valid operations. Use boundaries/property tests for arithmetic and stateful invariants for complex asset flows. A VM test does not establish RPC or wallet integration; run the relevant local integration separately.
4. Run appropriate build, tests, types, or lint checks and inspect their output. A host build alone does not verify the SBF artifact. For frontend changes, exercise wallet rejection, expiry/uncertainty, execution errors, locale changes, and cache isolation as applicable. Report missing tools or unexecuted checks honestly.

## Transactions and public actions

- Simulation, signing, submission, confirmation, and finalization are different states. A returned signature or an RPC timeout does not establish the outcome. Check the transaction's execution error and required commitment, then verify the relevant account or asset result.
- Track cluster, signature, and lifetime with each operation. For recent-blockhash transactions, retain the matching `lastValidBlockHeight`; inspect status before retrying. Rebuilding changes the message and signature and can duplicate a business action. Durable-nonce transactions require nonce-aware handling. See [DApp](references/dapp.md) and [deployment](references/deployment.md).
- Prepare reviewable code and local verification before public deployment. Use the already authorized cluster, accounts, and operations without asking again. If authorization is missing, finish runnable preparation and request only the remaining public action. An upgrade request does not implicitly authorize closing accounts, revoking upgrade authority, or changing unrelated token authorities.
- Keep real keys and seed phrases out of plaintext files, command arguments, logs, and frontend bundles. Do not borrow Cast Wallet or EVM signing assumptions. Confirm that the selected Solana tool can use the actual signer before proposing a runnable deployment.

## Deliver the result

Report the changed behavior, important assumptions, commands actually run, and remaining gaps. Include cluster/program IDs, IDL or client source, token-program/mint/decimal configuration, and compatibility impact when applicable. For DApps, explain transaction outcomes and refresh/localization behavior; for services, migrations, startup/health checks, and recovery. For actual deployments, provide signatures, commitment and execution result, program/authority inspection, and source-verification status separately. Local simulations and development tests are not public deployment results or a full audit.
