# Tokens and DeFi integrations

Use only when the task involves token issuance/transfers, swaps, oracles, vaults, lending, or related asset accounting. A wallet connection or SOL balance page does not require a DeFi module. Reuse established protocol programs and SDKs where they meet the requirement; prefer standard SPL behavior over a custom token program.

## Identify assets and authorities

- Identify an asset by cluster, mint, and governing token program. Names, logos, symbols, decimals, and UI metadata are not authenticity checks. Fetch the mint and verify its program owner before selecting an SDK or decoding layout.
- Decide explicitly whether the integration supports the original Token Program, Token-2022, or selected subsets of both. Use the correct program ID for instructions, validation, and address derivation. Anchor's compatible token interfaces can share basic operations, but accepting both program IDs does not establish support for every extension.
- Derive an associated token account from wallet/authority, token program ID, and mint. It is a token account owned by the selected token program, not by the Associated Token Program. Use idempotent creation when supported and appropriate; validate an existing account rather than assuming its address proves every business property.
- A wallet can have multiple token accounts for a mint. Distinguish a required ATA convention from an API that accepts any properly validated token account. For PDA-owned vaults, use derivation helpers that support an off-curve authority.
- Specify mint, freeze, token-account, delegate, close, and extension authorities independently. Explain retained powers and irreversible revocations before a requested handover. Do not revoke authorities as an incidental default.
- Use integer base units and checked transfers with a verified mint/decimals where appropriate. A token delegate is an explicit allowance mechanism; do not translate ERC20 allowance assumptions to every Solana transfer.

## Define Token-2022 support

Inspect mint and account extensions before accepting deposits, producing quotes, or building transfers. Use the installed SDK's extension-aware decoding and allocation helpers, including required account extensions and initialization ordering. Do not assume the base token-account size is sufficient.

| Extension or behavior | Required integration decision |
| --- | --- |
| Transfer fees | Account for the amount credited, withheld fees, rounding/caps, epoch changes, and withdrawal authority |
| Transfer hook | Validate the hook program and required extra accounts; support resolution and failures without granting unrelated privileges |
| Permanent delegate | Decide whether a third party's transfer/burn power is compatible with collateral or custody guarantees |
| Frozen/default state, pausable or non-transferable behavior | Define rejection and recovery behavior rather than assuming every mint is transferable |
| CPI guard or required transfer memo | Build compatible flows or reject the unsupported account configuration explicitly |
| Interest-bearing or scaled UI amounts | Separate displayed amounts from raw token accounting; do not assume display growth means extra spendable tokens |
| Confidential or unknown extensions | Support the exact documented flow or reject it before promising compatibility |

For supported fee-bearing tokens, credit actual received amounts and enforce minimum output after the relevant deductions. A successful `transfer_checked` does not prove the requested amount equals the net economic receipt. Do not silently ignore extensions or claim universal Token-2022 support from a successful basic transfer.

## SOL and wrapped SOL

Treat native lamports, fee-payer funds, rent reserves, and wrapped SOL token amounts as different balances. Use the native mint corresponding to the selected token program. After transferring lamports into a wrapped SOL account, use the compatible `SyncNative` flow before relying on its token amount.

Constrain wrapping/unwrapping and account-close recipients to the user-approved flow. Avoid closing an existing shared wrapped SOL account as cleanup; close only an account that the operation is authorized to close. Include transaction fees, priority fees, and account creation costs in available-balance checks.

## Swaps and aggregator responses

- Read the current protocol's official SDK/API documentation and deployed program IDs for the intended cluster. Preserve a supported existing integration; API generations, router modes, endpoint schemas, and transaction modification rules can differ.
- Bind each quote to input/output mints, input or output amount, user, recipient, slippage bounds, fees, and freshness. Distinguish exact-input minimum received from exact-output maximum spent. Reject expired or changed quotes and request a fresh decision when price constraints materially change.
- Inspect returned instructions or deserialized transaction messages before requesting signatures. Resolve address lookup tables to validate program IDs, accounts, recipients, token movements, fee payer, signers, delegate/authority changes, and setup/cleanup instructions against the intended action. An API response or successful simulation is not user authorization.
- Use simulation to detect failures and estimate compute, then apply bounded priority fees. Preserve provider constraints for preassembled or partially signed transactions; changing a message can invalidate existing signatures. Use a documented build path when custom instructions are needed.
- For onchain composition, validate CPI programs and permitted accounts, and enforce the authorized minimum/maximum amounts in the execution path. Check post-CPI balances where needed after reloading accounts. A frontend-only slippage setting is insufficient for a custom program's protection.
- Distinguish quote generation, user signature, submission, and successful onchain execution. Follow the transaction lifecycle in [DApp development](dapp.md); never retry an uncertain trade by rebuilding and resigning automatically.

## Oracles and financial accounting

- Bind oracle updates to a configured provider/program and feed identity, with the correct asset pair, exponent, and units. Verify provenance with the provider's supported onchain SDK and required accounts/instructions; a parsed payload alone is not a verified price.
- Enforce application-appropriate maximum age, timestamp validity, confidence/uncertainty bounds, and valid price domain. For feeds that carry forward old values, measure the underlying price's freshness. Choose behavior for closed markets, absent data, and provider outages instead of treating a cached or zero price as usable.
- Match the specific oracle product and SDK generation. For example, Pyth Core and Pro have different integration paths; verify required signature/update instructions and fee funding for the selected path. Do not blindly reuse one product's account layout or feed ID format with another.
- Do not value collateral from an easily manipulated pool spot price or an unsigned client quote. Use an oracle model appropriate to the asset and risk, and test stale, wrong-feed, future-dated, and extreme-confidence updates.
- Define share/debt precision, rounding beneficiaries, zero-supply behavior, fee accounting, and reserve/liability invariants before implementing vaults or lending. Consider donation/inflation effects, loss recognition, withdrawal limits, collateral changes, and liquidation boundaries only where the product uses them.
- Keep business authorization onchain. A database balance or successful API response does not establish collateral ownership, available liquidity, or settlement. Test the relevant model using [program tests and invariants](testing.md).

## Official references

- [Solana token accounts and ATAs](https://solana.com/docs/tokens/basics/create-token-account): ownership, authority, and program-aware derivation.
- [Anchor token transfers](https://www.anchor-lang.com/docs/tokens/basics/transfer-tokens): token interfaces and checked CPI transfers.
- [Solana token extensions](https://solana.com/docs/tokens/extensions): extension capabilities and compatibility requirements.
- [Transfer hook integration](https://solana.com/docs/tokens/extensions/transfer-hook-integration): extra account resolution and hook execution.
- [Wrapped SOL and SyncNative](https://solana.com/docs/tokens/basics/sync-native): reserves and token balance synchronization.
- [Jupiter Swap API](https://developers.jup.ag/docs/swap): current routing, transaction construction, and execution interfaces.
- [Pyth on Solana](https://docs.pyth.network/pro/use-prices-on-blockchain/solana): supported products and onchain verification.
- [Pyth price semantics](https://docs.pyth.network/pro/understanding-price-data): uncertainty and freshness of carried-forward prices.
