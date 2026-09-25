# Jean Skills

English | [简体中文](README.zh-CN.md)

A collection of Agent Skills for practical development work. Each skill can be installed independently and loads its references as needed. Ecosystems use sibling directories with their own development workflows and evaluation scenarios.

## Skill catalog

| Skill | Purpose | Status |
| --- | --- | --- |
| [web3-evm-dev](skills/web3-evm-dev/SKILL.md) | EVM contracts, React DApps, DeFi, smart accounts, wallet authentication, and supporting backends | Implemented |

A future Solana skill will use `skills/web3-solana-dev/`. Add its directory and catalog entry when it is implemented.

## Repository layout

```text
jean-skills/
├── README.md
├── README.zh-CN.md
├── skills/
│   └── web3-evm-dev/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
│           ├── contracts.md
│           ├── testing.md
│           ├── dapp.md
│           ├── backend.md
│           ├── deployment.md
│           ├── authentication.md
│           ├── defi.md
│           └── smart-accounts.md
└── evals/
    └── web3-evm-dev/
        └── scenarios.md
```

`skills/` contains distributable skills. `evals/` contains evaluation tasks for maintainers. A skill does not depend on the repository root, another skill, or `evals/` at runtime. Add `scripts/` or `assets/` inside a skill only when there is a concrete need.

## EVM engineering conventions

| Layer | New-project default |
| --- | --- |
| DApp | React + TypeScript, RainbowKit for wallet connection, wagmi for contract interaction, viem for underlying capabilities |
| Experience and data | react-toastify notifications; shared themes and multilingual support; TanStack Query for onchain caching and refresh |
| Supporting backend, when needed | Node.js + TypeScript + Prisma + viem; PM2 for processes on persistent hosts |
| Contracts and signing | Foundry + OpenZeppelin; critical business tests; Cast Wallet encrypted keystores, with no developer private keys in `.env` |

The skill turns these conventions into conditional workflows and observable acceptance criteria. Preserve compatibility in existing projects and migrate only when explicitly requested. PM2 manages processes and restarts them after failure; RPC, database, and host failures still require health checks and recovery mechanisms.

Advanced references load by task: [DeFi](skills/web3-evm-dev/references/defi.md) covers swaps, oracles, ERC-4626 vaults, and lending; [smart accounts](skills/web3-evm-dev/references/smart-accounts.md) covers ERC-4337, EIP-7702, ERC-1271, and EIP-5792; [wallet authentication](skills/web3-evm-dev/references/authentication.md) covers SIWE and sessions. Core workflows also cover approve/permit, known compiler bugs, static analysis, integration CI, L2 confirmation policies, and production permission handover. Activating the skill does not automatically add these modules to an ordinary DApp.

## Install in Codex

Place the desired skill directory in a Codex skill discovery location. Run the following from this repository's root to link the EVM skill into your personal skills directory; keep the clone available. First confirm that `~/.agents/skills/web3-evm-dev` does not already exist, including as a symlink:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/skills/web3-evm-dev" "$HOME/.agents/skills/web3-evm-dev"
```

If the destination exists, inspect its source before deciding how to update it. Do not create a duplicate link or overwrite an existing installation. Alternatively, copy the entire `skills/web3-evm-dev/` directory into a target project's `.agents/skills/` directory for project-local use.

Codex supports skill-directory symlinks and personal/project discovery. Restart Codex if the skill does not appear. See the [official Codex skills documentation](https://learn.chatgpt.com/docs/build-skills) for discovery details.

Installing the skill does not require blockchain tooling. During development, use Foundry, Node.js, and the package manager as the project requires; retain established stacks such as Hardhat or ethers.

## Usage examples

Request a concrete task in the target project. You can also invoke the skill explicitly:

```text
Use $web3-evm-dev to implement an ERC20 with controlled minting in this empty
project, add tests, and deploy locally. Do not connect to public networks yet.
```

```text
Use $web3-evm-dev to add ERC20 transfers to the existing page. Handle 6 decimals,
signature rejection, and onchain failure while keeping the current frontend stack.
```

```text
Use $web3-evm-dev to create a React DApp in Chinese and English. Connect wallets
with RainbowKit, unify themes and notifications, and refresh balances after confirmation.
```

```text
Use $web3-evm-dev to fix the permission bug in this Hardhat project. Reproduce it
first, add regression tests, and keep the current toolchain.
```

```text
Use $web3-evm-dev to integrate deposits and withdrawals for an existing ERC-4626
vault. Handle asset/share units, rounding, allowance, and refresh, with boundary tests.
```

```text
Use $web3-evm-dev to add ERC-4337 operations and gas sponsorship to the existing
wallet. Check chain, account SDK, and EntryPoint compatibility, and show failures and fees correctly.
```

## Language policy

- English is the primary repository documentation language. Keep this README and [its Simplified Chinese version](README.zh-CN.md) aligned when changing shared content.
- Skill instructions, references, UI metadata, and maintainer evaluation scenarios are written in English. Keep a single source for each skill instead of maintaining translated skill copies.
- The source language does not force English responses or an English-only product. Follow the user's requested language and the project's locale requirements; new DApps still default to Simplified Chinese and English when unspecified.

## Add and maintain skills

- Name Web3 skills `web3-<ecosystem>-<capability>`, such as `web3-evm-dev` or `web3-solana-dev`. Name other skills for their concrete tasks. Match the directory name to the frontmatter `name`.
- Put triggers, workflow, and completion criteria in `SKILL.md`; keep details in references inside the skill and link them from the entry point.
- Maintain ecosystem differences in sibling skills without depending on each other's private files. Extract repository-level validation tools only when a repeated need appears.
- When adding a skill, update both README catalogs and `evals/<skill-name>/scenarios.md`. Validate realistic tasks before adding scripts or templates.
- Check project versions and official documentation when maintaining SDK/CLI examples. Do not treat the latest version as a permanent constant.

See the EVM [evaluation scenarios](evals/web3-evm-dev/scenarios.md) for inputs, environment requirements, and acceptance criteria. Structural validation does not establish behavioral correctness; execution records must distinguish completed checks, partial verification, and checks not run.
