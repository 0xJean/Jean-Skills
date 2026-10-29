# Solana program development

Use for new programs, instruction changes, account migrations, or program-side debugging. Read [tokens and DeFi](tokens-defi.md) when the change involves token assets or financial integrations; select validation from [testing](testing.md).

## Choose the implementation boundary

- Prefer Rust + Anchor for a new application program. Retain existing native Rust, Pinocchio, or other established implementations when making a focused change. Use the user's requirements and measured constraints to justify a framework change.
- Inspect the installed Anchor CLI and crates, Rust and Solana/Agave toolchains, lockfiles, enabled features, generated IDL, and client dependencies together. Pin compatible versions; framework generations may change APIs, discriminators, account validation, and test defaults.
- Identify the program ID, target cluster, deployed version, account layouts, PDA derivations, instruction encoding, and upgrade authority. A new binary does not migrate existing account data automatically. Preserve published interfaces or provide an explicit migration supported by the task.
- Implement only requested roles, pause controls, fees, and upgrade mechanisms. A simple transfer integration may require no custom onchain program.

## Validate accounts at the instruction boundary

Treat supplied accounts and instruction bytes as untrusted inputs. Account order or a client's generated types do not establish permission.

| Boundary | Establish onchain |
| --- | --- |
| Acting authority | Required signature plus its relationship to the stored authority, owner, position, or role |
| Program state | Expected program owner, account type/discriminator, initialization state, and business identifier |
| PDA | Expected program ID, unambiguous seeds, and validated bump |
| Asset account | Expected token program, mint, token authority, and applicable delegate or close authority |
| External program | Expected executable program ID and permitted instruction/account relationship |
| Dynamic accounts | Explicit length, ordering, ownership, types, relationships, and writable/signer requirements |

Use Anchor's typed accounts and constraints where they express the requirement. `Signer` proves a signature; it does not prove that the signer is the business administrator. `has_one` binds a stored key; it does not replace the signer requirement. Distinguish a Solana account's program owner from the authority stored inside its data, especially token accounts.

Document and perform checks for `UncheckedAccount`, raw `AccountInfo`, and `remaining_accounts`. A `CHECK` comment is an explanation, not an executed validation. For native programs, implement the equivalent checks explicitly. Reject account aliasing when two roles must differ; inspect the installed Anchor version and account types rather than assuming duplicate mutable accounts are always rejected.

## PDAs, initialization, and state lifetime

- Use domain-separated seed prefixes and fixed or explicitly encoded components; avoid ambiguous concatenation of variable-length inputs. Derive the canonical bump when initializing a unique PDA, then validate any stored bump against the expected derivation. Do not accept an arbitrary user-provided bump as evidence of uniqueness.
- A PDA has no private key. Its deriving program can authorize CPI operations with its seeds; this does not mean every account at a PDA is data-owned by that program. Token vault accounts remain owned by their token program.
- Bind initialization to the intended authority and instance. Use `init_if_needed` only when repeated calls preserve all initialized permissions and state; test reinitialization attempts and existing accounts supplied with the wrong identity.
- Allocate serialized space, including the actual discriminator and length prefixes, using the project's layout conventions. Bound variable-length data; string limits must account for bytes. Use layout-aware sizing for zero-copy accounts rather than applying ordinary serialization formulas.
- For `realloc`, constrain the new size, payer/refund recipient, rent funding, and zeroing behavior. Check growth limits and shrink/regrow behavior against the selected runtime and SDK. Preserve a versioned migration path for deployed data.
- Authorize account closure and its rent recipient. Closing an account does not permanently consume its address: if a claim or operation must stay used, preserve that fact in durable state outside the closed account. Test recreation and repeat execution where relevant.

## CPI and asset movement

- Validate CPI target IDs and the accounts passed to them. Never give a caller-selected executable unrestricted access to vault PDA signer privileges. Permit only the signer and writable accounts needed by the intended operation.
- Use typed CPI interfaces where available; pass the exact seeds and bump for the acting PDA. The runtime prevents privilege escalation but does not validate the application's intended recipient or amount.
- Propagate CPI failures and validate expected return data and its producing program. Release outstanding data borrows before incompatible calls. Reload deserialized accounts after a CPI changes data that subsequent logic reads; do not calculate from stale cached state.
- Follow Solana's actual CPI semantics, including direct recursion and restricted indirect reentrancy, rather than assuming EVM callback behavior. Assess the supported call path and shared state for this instruction.
- Keep account lists, iteration, serialization, and CPI depth within measured compute and transaction limits. Use bounded batches or paging for growing collections. Mark accounts writable only when necessary to reduce lock contention.

## Arithmetic and compatibility

- Store lamports and token amounts as integer base units. Check addition, subtraction, multiplication, division by zero, and narrowing conversions; use appropriately wide intermediates. Define rounding direction for fees, shares, debt, and settlement.
- State the balance or conservation invariant before changing accounting. Rent reserves, token balances, available withdrawals, protocol liabilities, and externally transferred funds are distinct quantities.
- Validate instruction data lengths and enum variants; return actionable program errors for expected invalid input. Avoid panics and `unwrap` on user-controlled data in production paths.
- Preserve account field order/types, discriminator assumptions, PDA seeds, and instruction layouts needed by existing clients. Regenerate IDL and client artifacts from the same source/build and test old data against a proposed migration.
- Treat program upgrade authority separately from business admin and token authorities. Prepare authority changes and upgrade verification through [deployment](deployment.md); do not make a program immutable as an incidental cleanup.

## Official references

- [Anchor account constraints](https://www.anchor-lang.com/docs/references/account-constraints): declarative validation; use the installed version's behavior.
- [Anchor account space](https://www.anchor-lang.com/docs/references/space): serialized sizing and zero-copy differences.
- [Anchor security examples](https://github.com/coral-xyz/sealevel-attacks): focused examples of owner, signer, aliasing, CPI, initialization, and closing mistakes.
- [Solana PDA derivation](https://solana.com/docs/core/pda/pda-derivation): seeds, bumps, and signing authority.
- [Solana CPI](https://solana.com/docs/core/cpi): privilege propagation, execution rules, and runtime-dependent limits.
