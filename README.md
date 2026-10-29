# Jean Skills

English | [简体中文](README.zh-CN.md)

A collection of portable Agent Skills for practical development with Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, and OpenCode. Each skill can be installed independently and loads its references as needed. Ecosystems use sibling directories with their own development workflows and evaluation scenarios.

## Skill catalog

| Skill | Purpose | Status |
| --- | --- | --- |
| [web3-evm-dev](skills/web3-evm-dev/SKILL.md) | EVM contracts, React DApps, DeFi, smart accounts, wallet authentication, and supporting backends | Implemented |
| [web3-solana-dev](skills/web3-solana-dev/SKILL.md) | Solana programs, React DApps, SPL tokens, DeFi integrations, wallet authentication, and supporting backends | Implemented |

Choose the skill for the target ecosystem. Both are self-contained and can be installed separately or together.

## Installation

### Ask your agent to install it

Copy this message into your coding agent with terminal and filesystem access. No manual clone is needed:

```text
Install the web3-evm-dev skill from https://github.com/0xJean/Jean-Skills
for the coding agent I am currently using, at user scope.
Read the repository's installation instructions and use a supported installer
or copy the complete skills/web3-evm-dev directory, including references,
into this agent's documented skill directory. Check any existing installation
before replacing it. Verify the installed files and, where possible, skill
discovery. Tell me the destination and any reload step still needed.
```

For Solana, send this message instead:

```text
Install the web3-solana-dev skill from https://github.com/0xJean/Jean-Skills
for the coding agent I am currently using, at user scope.
Read the repository's installation instructions and use a supported installer
or copy the complete skills/web3-solana-dev directory, including references,
into this agent's documented skill directory. Check any existing installation
before replacing it. Verify the installed files and, where possible, skill
discovery. Tell me the destination and any reload step still needed.
```

For a shared repository installation, replace **“at user scope”** with **“at project scope in this repository”**. An agent that can only chat or browse cannot install local files; use its coding mode or one of the methods below.

### Install with the Skills CLI

The [Vercel Skills CLI](https://github.com/vercel-labs/skills#readme) is an optional cross-agent installer. It downloads this repository and installs the selected skill; it is not a built-in command of every agent. Requires Git and Node.js/npm. The verified CLI version, `skills@1.7.0`, requires Node.js **22.20.0 or newer**.

Preview the available skills without installing:

```bash
npx skills add 0xJean/Jean-Skills --list
```

Install for one agent at user scope. This example uses Claude Code; replace `claude-code` with an agent ID from the table below:

```bash
npx skills add 0xJean/Jean-Skills --skill web3-evm-dev --agent claude-code --global --copy
```

To install the Solana skill:

```bash
npx skills add 0xJean/Jean-Skills --skill web3-solana-dev --agent claude-code --global --copy
```

For project scope, run inside the target project and omit `--global`. Multiple IDs target several agents:

```bash
npx skills add 0xJean/Jean-Skills --skill web3-evm-dev --agent codex cursor --copy
```

`--copy` installs complete files without depending on symlink support. Use `--yes` for unattended execution after choosing the scope and agents and checking existing installations. The CLI manages its own destination mapping; it may use shared or compatibility directories rather than each agent's native directory below. Shared directories can be discovered by more than one agent.

### Supported agents and manual installation

The skill uses the open [Agent Skills format](https://agentskills.io/specification): `SKILL.md` plus local references. These destinations are documented by the corresponding products; use a current release with Agent Skills support. The table lists native manual-install locations, not an exhaustive list of compatibility paths.

| Agent and official documentation | CLI `--agent` ID | Project skill directory | User skill directory |
| --- | --- | --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `codex` | `.agents/skills/` | `~/.agents/skills/` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| [Cursor](https://cursor.com/docs/skills) | `cursor` | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot: [CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) / [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills) | `github-copilot` | `.github/skills/` | `~/.copilot/skills/` |
| [Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/) | `gemini-cli` | `.gemini/skills/` | `~/.gemini/skills/` |
| [OpenCode](https://opencode.ai/docs/skills/) | `opencode` | `.opencode/skills/` | `~/.config/opencode/skills/` |

For manual installation, clone/download [this repository](https://github.com/0xJean/Jean-Skills), then copy **the entire `skills/web3-evm-dev/` or `skills/web3-solana-dev/` folder** into the chosen directory. The result must be `<skill-directory>/<skill-name>/SKILL.md` with its sibling `references/` intact. Downloading only `SKILL.md` breaks the supporting references. Inspect an existing destination before updating it, and avoid duplicate installations in multiple directories read by the same agent.

`agents/openai.yaml` supplies optional Codex/OpenAI UI metadata; the shared instructions do not depend on it. Keep it with the folder, without expecting other agents to use its appearance or invocation settings. This repository distributes standalone skills, not a Claude or Cursor plugin marketplace; their native marketplace import flows require additional packaging.

These paths concern local agents. A cloud agent cannot automatically read your machine's user directory; use a supported project-level or remote installation for that environment. Installing these instruction files does not require Foundry, Solana/Anchor tools, or blockchain credentials. Development tools are needed only when a task uses them.

### Verify and use the skill

Confirm that `SKILL.md` and all of the selected skill's references exist at the destination: eight references for EVM, six for Solana. The examples below use `web3-evm-dev`; substitute `web3-solana-dev` when checking or invoking the Solana skill:

- **Codex:** use the skill selector or `/skills` in CLI/IDE, then mention `$web3-evm-dev`. Restart if a newly installed skill does not appear.
- **Claude Code / Cursor:** invoke `/web3-evm-dev`; Cursor also offers skill selection with `@`.
- **Copilot CLI:** run `/skills reload`, then `/skills info web3-evm-dev`. In **VS Code**, use `/skills` or `/web3-evm-dev` instead of assuming CLI management commands apply.
- **Gemini CLI:** run `/skills reload` and `/skills list`, then request the skill in natural language. Project skills require a trusted workspace. Follow its native activation confirmation when prompted.
- **OpenCode:** start a new session if needed and ask it to load `web3-evm-dev`; check skill permissions if it is unavailable.

Agent installation documentation checked on **2026-09-26**. A temporary EVM project installation using `skills@1.7.0` with all six agent IDs preserved all 10 EVM skill files byte-for-byte. This verifies installer output, not end-to-end execution inside every agent. The CLI version is a validation record, not a permanent version requirement; use `npx skills@1.7.0` to reproduce that installer version.

On **2026-10-29**, the same CLI installed `web3-solana-dev` from the local checkout into a temporary project with all six agent IDs. All eight Solana skill files matched the source by SHA-256. This checks local packaging and installer output; it does not verify a published GitHub version or execution inside every agent.

## Repository layout

```text
jean-skills/
├── README.md
├── README.zh-CN.md
├── skills/
│   ├── web3-evm-dev/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   └── references/        # Contracts, DApp, backend, deployment, and advanced flows
│   └── web3-solana-dev/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
│           ├── programs.md
│           ├── testing.md
│           ├── dapp.md
│           ├── backend.md
│           ├── tokens-defi.md
│           └── deployment.md
└── evals/
    ├── web3-evm-dev/scenarios.md
    └── web3-solana-dev/scenarios.md
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

## Solana engineering conventions

| Layer | New-project default |
| --- | --- |
| Programs | Rust + Anchor; reuse System/SPL programs when sufficient; validate account relationships, PDAs, signers, and CPI targets |
| DApp | React + TypeScript, Wallet Standard, compatible Solana Kit clients and React bindings; preserve existing Anchor/web3.js client constraints |
| Experience and data | react-toastify; shared themes and `zh-CN`/`en-US` locales; TanStack Query caching and refresh after verified execution |
| Supporting backend, when needed | Node.js + TypeScript + Prisma + compatible Solana SDK; PM2 on persistent hosts |
| Testing | Program and adversarial-account tests, numeric boundaries and invariants; LiteSVM/Mollusk where suitable, plus local validator integration |
| Deployment and signing | Hardware/external signing or approved encrypted custody for real credentials; verify cluster, program/IDL identity, execution, and authorities |

Solana SDK guidance was checked against official documentation on **2026-10-29**. New clients may use [Solana Kit and React bindings](https://solana.com/docs/frontend); the selected [Anchor TypeScript client](https://www.anchor-lang.com/docs/clients/typescript) may require legacy web3.js types. The skill checks versions and preserves that boundary instead of forcing a migration. A Solana JSON keypair is plaintext, including when a seed recovery passphrase was used; it is not a substitute for an encrypted keystore.

Task-specific references cover [SPL Token/Token-2022 and DeFi](skills/web3-solana-dev/references/tokens-defi.md), [wallet authentication and indexing](skills/web3-solana-dev/references/backend.md), and [deployment and authority management](skills/web3-solana-dev/references/deployment.md). Recent-blockhash expiry, ambiguous submission outcomes, token extensions, and deployed account-layout compatibility have explicit checks. Authentication, multisig, and a custom program are introduced only when the task needs them.

## Usage examples

Request a concrete task in the target project. These prompts use the skill name in plain language; use your agent's selector or invocation syntax above to attach it explicitly:

```text
Use the web3-evm-dev skill to implement an ERC20 with controlled minting in this empty
project, add tests, and deploy locally. Do not connect to public networks yet.
```

```text
Use the web3-evm-dev skill to add ERC20 transfers to the existing page. Handle 6 decimals,
signature rejection, and onchain failure while keeping the current frontend stack.
```

```text
Use the web3-evm-dev skill to create a React DApp in Chinese and English. Connect wallets
with RainbowKit, unify themes and notifications, and refresh balances after confirmation.
```

```text
Use the web3-evm-dev skill to fix the permission bug in this Hardhat project. Reproduce it
first, add regression tests, and keep the current toolchain.
```

```text
Use the web3-evm-dev skill to integrate deposits and withdrawals for an existing ERC-4626
vault. Handle asset/share units, rounding, allowance, and refresh, with boundary tests.
```

```text
Use the web3-evm-dev skill to add ERC-4337 operations and gas sponsorship to the existing
wallet. Check chain, account SDK, and EntryPoint compatibility, and show failures and fees correctly.
```

```text
Use the web3-solana-dev skill to implement an Anchor escrow program with deposits,
authorized release, and cancellation. Add adversarial-account tests and verify locally.
```

```text
Use the web3-solana-dev skill to build a bilingual React token-transfer page.
Use Wallet Standard, verify Token-2022 support, and handle rejection, expiry, and refresh.
```

```text
Use the web3-solana-dev skill to fix this existing Anchor/web3.js integration without
migrating SDKs. The RPC times out after submission and users sometimes pay twice.
```

```text
Use the web3-solana-dev skill to prepare an upgrade for this deployed program.
Check account-layout compatibility, IDL/client consistency, and authorities; do not broadcast yet.
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

See the [EVM evaluation scenarios](evals/web3-evm-dev/scenarios.md) and [Solana evaluation scenarios](evals/web3-solana-dev/scenarios.md) for inputs, environment requirements, and acceptance criteria. Structural validation does not establish behavioral correctness; execution records must distinguish completed checks, partial verification, and checks not run.
