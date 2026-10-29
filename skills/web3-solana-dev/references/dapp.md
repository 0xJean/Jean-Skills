# Solana DApp Integration

Use this reference for React wallets, program clients, exact amounts, transaction feedback, and chain data refresh. Read [tokens and DeFi](tokens-defi.md) when token extensions, swaps, or vaults affect the flow.

## Choose Compatible Clients

- For new DApps, prefer React + TypeScript, Wallet Standard discovery, a compatible Solana SDK, TanStack Query for application data, and react-toastify. Preserve existing frameworks, wallet adapters, providers, and generated clients unless migration is requested.
- The official frontend documentation reviewed on 2026-10-29 recommends `@solana/kit`, composable `@solana/kit-plugin-*` packages, and `@solana/react`. Its wallet hooks live in `@solana/kit-plugin-wallet/react`. Inspect installed exports and peer dependencies before using these APIs: older Kit, `@solana/react-hooks`, and `@solana/client` examples are not interchangeable with this generation.
- Select the program client before finalizing the application SDK. The reviewed Anchor TypeScript documentation names `@anchor-lang/core` and specifies legacy `@solana/web3.js` v1 compatibility. Existing projects may use `@coral-xyz/anchor`; follow their release, IDL, and lockfile rather than renaming imports in isolation. A newer web3.js major or Kit value is not automatically compatible with an Anchor provider.
- A Kit application can use a compatible generated client from the program's IDL, or isolate a required legacy client behind an explicit adapter. Anchor versions supporting `[clients]` in `Anchor.toml` can run Codama generation after building; inspect the selected renderer and generated dependencies before adopting its output. Keep address, instruction, signer, and transaction conversions at that boundary; do not fix incompatible types with unsafe casts. Do not introduce both SDK families unless the integration requires them.
- Bind program IDs, IDLs/codecs, RPC endpoints, and explorer URLs to the intended cluster. The same public key on another cluster is a different deployment. Validate RPC configuration; never infer the target cluster solely from the connected public key.

## Wallet Entry Point and Localization

- Discover supported wallets through Wallet Standard or the project's established adapter. Check the selected account's chain, signing features, and supported transaction versions; connected read-only accounts may have no signer. Do not assume every wallet supports every signing method.
- Share a stable client/provider and one connection entry point. Preserve disconnected, connecting/reconnecting, rejected, connected, and unsupported-capability states. Account or cluster changes invalidate drafts and simulations built for the previous context.
- Match connection controls, modal, focus behavior, colors, and light/dark mode to site design tokens. Use supported component APIs or an accessible custom entry point; do not patch a library's private DOM.
- Preserve existing languages. New DApps default to `zh-CN` and `en-US`, persisted language selection, and an explicit fallback. Use one locale state for forms, wallet controls, errors, transaction status, and toasts. If a wallet component cannot localize required copy, select a supported alternative or custom UI.
- Store semantic status and translation keys so a locale change updates visible notices without resubmitting a transaction. Wallet extension and hardware-device screens have their own theme and language settings.
- Connecting proves no authenticated session. Implement message-based login only when required, using [backend authentication](backend.md#wallet-authentication-when-needed).
- In SSR projects, keep browser wallet access in client boundaries and avoid cross-user caches on the server. Do not expose RPC secrets or signing material in frontend environment variables.

## Exact Amounts and Account Data

- Keep input as decimal strings and base units as `bigint` or the selected client's exact integer representation, such as Anchor `BN`. Reject negative amounts, excess fractional digits, and out-of-range values before encoding. Never calculate token quantities with floating-point multiplication or `parseFloat`.
- Read decimals from the verified mint and distinguish SOL lamports from SPL token units. Format without losing precision; serialize large integers as canonical decimal strings. Validate public keys with the SDK; base58 is case-sensitive and must not be lowercased.
- Distinguish the wallet owner, mint, token account, and token program. Derive the ATA for the actual token program. Absence of an ATA may mean it needs creation; a transport error does not mean zero balance. Include account-creation rent and transaction fees when checking available SOL.
- A syntactically valid address may be a PDA or an account of the wrong type. Apply role-specific checks instead of requiring every legitimate recipient to have an on-curve private key.

## TanStack Query and Freshness

- Use one owner for each piece of server state. With TanStack Query, wrap SDK reads in query functions and use subscriptions to update or invalidate that cache. Avoid an independent SDK-hook cache for the same balance or position.
- Query identity includes cluster, program/mint/token-program address, account, arguments, and commitment when relevant. Normalize `bigint` arguments to strings. Cancel or ignore stale responses after wallet changes; public reads can remain enabled while disconnected.
- After verified execution, refresh the balances and program accounts affected, using the account and cluster captured at submission. A refresh failure must not relabel a successful transaction as failed. Use a sufficient commitment/context slot where supported so the refresh does not immediately show pre-transaction state.
- Choose bounded polling or subscriptions according to freshness needs and provider limits. `staleTime` alone does not poll. Recover with a read after reconnecting, unsubscribe on cleanup, and avoid invalidating the whole application on every slot.

## Transaction Lifecycle

Capture the submitting account, cluster, operation parameters, signature when available, and lifetime information independently of current wallet UI state.

| State | Evidence and UI | Toast |
| --- | --- | --- |
| Preparing / simulating | Validate accounts, fees, instruction parameters, and simulation result | Inline progress; explain simulation errors |
| Awaiting signature | Wallet approval is outstanding | Loading: confirm in wallet |
| Submitted | RPC accepted bytes or a signature is known | Loading: awaiting confirmation; cluster-correct explorer link |
| Confirmed | Required commitment reached and execution error is absent; verify business result when needed | Success; refresh affected data |
| Rejected | User declines before submission | Info: canceled |
| Failed | Definite execution or validation failure | Error with an actionable reason |
| Status unknown | Submission/confirmation timed out or RPC evidence is unavailable | Warning: checking status; retain signature |
| Expired without execution | Lifetime ended and reconciliation supports that it did not execute | Warning: prepare a new attempt |

- RPC `sendTransaction` success acknowledges submission, not execution. Inspect `err` and confirmation status. Use explicit `confirmed` for ordinary user feedback when appropriate; reserve irreversible settlement for the required policy, usually `finalized`. Do not present `processed` as final.
- Fetch a fresh blockhash close to signing, retaining its `lastValidBlockHeight`. Align blockhash, simulation, and preflight commitments. Use simulation to estimate compute and apply a bounded priority-fee policy; avoid unlimited fee escalation or disabling preflight as the default fix.
- A wall-clock timeout does not prove expiry. Track block height against `lastValidBlockHeight`; slots and heights differ. Query the signature, including transaction history where needed, and reconcile business state. A missing status from an unavailable or pruned RPC is not proof of non-execution.
- While valid, bounded rebroadcast may send the same signed bytes. Rebuilding with a different blockhash creates a different transaction requiring signatures; only do so after resolving the previous attempt and obtaining the signing authorization needed for the new attempt. Expiry cannot undo an earlier successful execution.
- Do not mutate a signed message. Reconcile any wallet-returned transaction/signature with the submitted one. Durable nonce transactions require nonce-account lifetime checks rather than the recent-blockhash rule; use them only when the workflow calls for them.
- Keep a multi-transaction operation's partial results: separate transactions are not atomic. Before signing externally built transactions, inspect instructions, resolved lookup-table accounts, fee payer, recipients, amounts, and authority changes against the requested operation.

## Notifications and Verification

- Use one shared `ToastContainer` styled to the application. Assign a stable operation `toastId`; advance it with `toast.loading`/`toast.update`, clear `isLoading` on terminal or unknown states, and retain status on the page. Deduplicate rerenders and subscription callbacks.
- Bind `toast.promise` to a promise that includes the confirmation and business checks its success copy claims. Do not show success merely because a signing or submission promise resolved. Keep message-signing/login notices separate from transaction confirmation.
- Verify affected behavior with the project's test tools: exact amounts beyond safe integers; missing ATA; rejected signatures; expiry versus timeout; successful execution versus `err`; late responses after wallet/cluster switches; localized wallet controls/toasts; and targeted refresh. State clearly whether tests used mocks, a local validator, or a real wallet.

## Official References

- [Solana frontend](https://solana.com/docs/frontend), [Kit client](https://solana.com/docs/frontend/client), and [React bindings](https://solana.com/docs/frontend/react-hooks): current SDK and Wallet Standard integration; match the installed release.
- [Anchor TypeScript client](https://www.anchor-lang.com/docs/clients/typescript) and [client generation configuration](https://www.anchor-lang.com/docs/references/anchor-toml): provider compatibility and optional Codama generation.
- [Submission semantics](https://solana.com/docs/rpc/http/sendtransaction), [signature status](https://solana.com/docs/rpc/http/getsignaturestatuses), and [confirmation and expiry](https://solana.com/developers/cookbook/transactions/confirmation): evidence required for transaction states.
- [TanStack Query invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation) and [React-Toastify updates](https://fkhadra.github.io/react-toastify/update-toast/): cache refresh and notification APIs.
