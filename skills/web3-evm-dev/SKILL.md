---
name: web3-evm-dev
description: Develop, modify, and debug EVM Solidity contracts, DApps, and supporting backends, including DeFi integrations, smart accounts, wallet authentication, testing, and deployment. Use for Ethereum and EVM-compatible chains; exclude styling-only changes, generic backends, market analysis, and Solana development.
---

# EVM Contract and DApp Development

Deliver verifiable code changes for the user's task. Select the relevant contract, frontend, supporting backend, or deployment workflow. Load only the references needed for a focused fix; do not expand it into a complete application or general security audit. Respond in the user's requested language and follow the project's product locales; this skill's English source does not override either.

## Identify the project

- Read project conventions, directories, dependencies and lockfiles, compiler settings, tests, and deployment entry points. Identify existing proxies or live deployments and the ABI, storage, and integration compatibility that must be preserved.
- Determine the target chain, contracts, business rules, administrator roles, amount units, and delivery scope from the request and configuration. Ask only for missing details that change the implementation or onchain actions; otherwise proceed with clearly stated, reasonable assumptions.
- Choose technology in this order: the user's current explicit requirements, existing project constraints, then the new-project defaults below. Do not migrate a Hardhat, ethers, or non-React project merely because this skill is active. Explain compatibility or necessary changes within the task. Existing habits do not relax signing-credential handling or transaction-result checks.
- Before calling an SDK or CLI, check the installed version, type definitions, and `--help`. Consult the matching official documentation when uncertain or adding dependencies. Identify missing dependencies and never report an unexecuted check as passing.

## New-project defaults and completion requirements

| Area | Default technology and convention |
| --- | --- |
| DApp | TypeScript + React; RainbowKit for wallet connection; wagmi Hooks/Actions for contract interaction; viem for underlying clients and precise types |
| User experience | react-toastify for operation lifecycle notifications; pages, RainbowKit, and notifications share theme and locale state; provide switchable languages, defaulting to Simplified Chinese and English when unspecified |
| Onchain reads | Use wagmi's TanStack Query integration for caching and refresh; invalidate affected queries after confirmation and isolate data across account and network changes |
| Supporting backend, when needed | Node.js + TypeScript + Prisma + viem; create it only for persistence, indexing, or controlled APIs; manage services on persistent hosts with PM2 |
| Contracts | Solidity + Foundry; prefer released OpenZeppelin components; test business behavior, permissions, and asset boundaries |
| Developer signing | Use Cast Wallet encrypted keystores for local developer wallets; never store real private keys or seed phrases in plaintext files or `.env`; existing hardware or external signers may be retained |

These are this skill's engineering conventions, not universal EVM standards. Apply defaults to new projects or modules without existing constraints; reuse established integrations when adding to an existing project. Keep migrations within the explicit task. Choose compatible releases and lock versions, especially RainbowKit's wagmi/viem/Query peer dependencies; do not independently install every package's latest version. Choose the React build framework and i18n implementation to fit the project.

## Read by task

| Current work | Reference | Questions to resolve |
| --- | --- | --- |
| Create or modify contracts | [Contract development](references/contracts.md) | Permissions, state changes, asset accounting, external calls, and deployed compatibility |
| Fix failures or verify behavior | [Testing and debugging](references/testing.md) | Regressions, boundaries, fuzzing, state invariants, and fork reproduction |
| Connect wallets or read/write contracts | [DApp integration](references/dapp.md) | RainbowKit, wagmi, themes/locales, notifications, amounts, and cache refresh |
| EVM APIs, storage, indexing, or process operations | [Supporting backends](references/backend.md) | Prisma consistency, viem, event recovery, and the PM2 lifecycle |
| Deployment scripts, deployment, or integration checks | [Deployment verification](references/deployment.md) | Simulation versus broadcast, signing, receipts, artifact synchronization, and result checks |
| Wallet login, server sessions, or signature authentication | [Wallet authentication](references/authentication.md) | SIWE, one-time challenges, contract-wallet verification, and session authorization |
| Swaps, oracles, vaults, or lending | [DeFi development](references/defi.md) | Slippage, assets/shares, price validity, and economic invariants |
| Smart wallets, account abstraction, delegation, or batching | [Smart accounts](references/smart-accounts.md) | ERC-4337, EIP-7702, ERC-1271, EIP-5792, and execution results |

Load only references relevant to the task. Wallet connection does not automatically introduce SIWE or account abstraction, and an ordinary ERC20 does not require a DeFi module. Reference paths are relative to this skill and do not depend on the collection repository or another skill.

## Develop and verify

1. **Define observable behavior.** Translate requirements into inputs, permissions, state changes, events, and failure conditions. For a bug fix, first construct a test that reproduces the issue.
2. **Implement the necessary changes.** Reuse project components and standard contracts. Add upgradeability, extra privileges, or services only when required. Keep onchain data consistent with frontend types, units, and configuration.
3. **Select useful verification.** Test business rules and relevant failure paths for contract changes; report critical-path coverage and gaps for new contracts. Use boundaries or fuzzing for amount calculations, invariants for complex sequences, and fixed-block forks when external integrations need them. Verify frontend notifications, locales, transaction states, and refresh after account/network changes. Verify persistence, retry idempotency, and recovery where backend changes require them. Avoid unrelated expensive checks.
4. **Check the results.** Run the applicable compilation, tests, type checks, or build and record actual commands and results. Confirm invariant tests execute effective operations. Complete deployment and calls when local integration is needed; deploy to public networks only when the task includes that action.

## Onchain execution scope

Writing deployment scripts, simulating them, and broadcasting to a public network are separate actions. Complete reviewable code, tests, and simulation first, then act within the chains, accounts, and operations already authorized. Do not ask again for existing explicit authorization. If broadcast authorization is missing, deliver runnable preparation and request confirmation only for the remaining action.

Use Cast Wallet encrypted keystores with `--account` aliases for local developer signing, or retain existing hardware/external signers. Real private keys and seed phrases must not enter plaintext files, `.env`, code, frontend bundles, command arguments, or output. Do not export decrypted keys to connect scripts. See [deployment verification](references/deployment.md) for import and unlocking. Simulation cannot guarantee a future transaction will succeed; investigate timeouts or missing receipts before resubmitting.

For proxy upgrades, DeFi, smart accounts, and cross-chain integrations, add design and compatibility checks appropriate to the actual mechanism. State the scope verified by this task and preserve existing constraints. Do not describe ordinary development tests as a full audit.

## Deliver the result

Provide what applies to the task:

- Actual changes, important behavior, and necessary assumptions.
- Checks performed and their results; unverified items and specific reasons.
- For contract/frontend integration, the ABI, chain ID, address source, and usage.
- For a new DApp, supported themes and locales, notification states, and refresh strategy. For backend work, database migration, startup/health checks, and recovery instructions.
- For an actual deployment, the target chain, contract addresses, transaction hashes, receipt status, and source-verification status. Label simulation results as simulations.

Generating code, obtaining a transaction hash, or compiling successfully does not by itself complete the task.
