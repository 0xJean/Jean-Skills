# DApp Integration

Use this reference for wallet connections, contract reads, transaction submission, and EVM frontend integration issues. Read only the sections relevant to the current change.

Navigation: [Project constraints](#establish-project-constraints) · [Wallet entry point](#wallet-entry-point-and-theme) · [Localization](#consistent-localization) · [Chains and ABI](#keep-chain-address-and-abi-consistent) · [Amounts](#amounts-and-user-input) · [Query refresh](#tanstack-query-and-onchain-refresh) · [Transaction states](#write-operation-states-and-results) · [Token approvals](#token-approvals-and-permit) · [Notifications](#react-toastify-notifications) · [Verification](#ssr-and-verification).

## Establish Project Constraints

- For new projects, default to TypeScript + React, RainbowKit for wallet entry points, wagmi + viem for contract interactions, TanStack Query for queries, and react-toastify for notifications. Choose the application framework to suit the product.
- Follow the user's current explicit requirements first, existing project constraints second, and defaults last. New modules reuse existing Providers, wallet SDKs, notifications, and i18n; do not migrate the whole project without a request.
- Determine actual versions from dependency manifests, lockfiles, existing calls, and type definitions. Before adding dependencies, check the selected RainbowKit release's React, wagmi, viem, and TanStack Query `peerDependencies`; do not blindly install `latest` for every package.
- Check APIs against the relevant major version. Default documentation across official sites may cover different generations; do not put newer wagmi Hooks into a RainbowKit project that only supports an older major version.

## Wallet Entry Point and Theme

- Use the connection entry point from `@rainbow-me/rainbowkit`. Prefer wagmi Hooks/Actions for React contract reads and writes; use viem for underlying clients, encoding, and tools outside the framework. Do not build a parallel wallet connection layer or duplicate query cache.
- Arrange `WagmiProvider` → `QueryClientProvider` → `RainbowKitProvider` according to compatible versions, and load RainbowKit styles. Keep client-side config and QueryClient instances stable.
- Configure RainbowKit's `theme` using site-wide design tokens: light/dark mode, accent color, foreground contrast, fonts, and border radius should follow the site rather than retain an unrelated default appearance.
- Use `ConnectButton` by default. For custom layout, button labels, or states, use `ConnectButton.Custom` or official modal Hooks while preserving disconnected, wrong-network, account, and mounted/ready states.
- Configure the connection modal through public APIs such as theme, locale, and custom connection entry points; do not rewrite its internals through private DOM selectors.
- Configure the chains, connectors, and RPCs actually supported. When WalletConnect is needed, use the project's `projectId`, not a plausible-looking example value.
- Add [wallet authentication](authentication.md) only when the product needs a login session. Read [smart accounts](smart-accounts.md) for smart accounts, sponsorship, or batch calls; connecting a wallet does not implicitly enable these capabilities.

## Consistent Localization

- Preserve existing locales. For a new project without a specified language set, default to `zh-CN` and `en-US`, with language switching, persisted selection, and an explicit fallback for unsupported locales.
- Use one locale state for pages, form validation, buttons, transaction states, and notifications. Store copy in dictionaries and use parameter interpolation instead of concatenating sentences that need translation.
- Explicitly map the application locale to a supported `locale` in the selected RainbowKit version. Do not let the page's selection and the modal's automatic browser-language detection operate independently.
- Update `RainbowKitProvider` and visible toasts when the language changes. Store semantic state and message keys, then translate at render time instead of retaining old-language strings indefinitely.
- Keep the default fallback consistent between pages and RainbowKit. A language change affects presentation only; it must not resubmit transactions or reset the wallet connection.
- The site controls the RainbowKit modal. Browser wallet extensions and standalone wallet apps control their own signing and confirmation screens; do not promise to change their language or theme.

## Keep Chain, Address, and ABI Consistent

- Look up deployment addresses and corresponding ABIs by chain ID, reusing the project's deployment manifest. Do not scatter addresses across components.
- Use ABIs from compiled contracts or trusted deployment artifacts, retaining custom errors and events needed for decoding.
- Preserve an inferable literal ABI type or use the project's code generation approach. Do not hide incorrect parameters with type assertions.
- Explicitly bind reads to the target chain. The wallet's current chain must not silently change which deployment the displayed data represents.
- Before writes, check the wallet account, wallet chain, and target deployment. If the target chain has no deployment address, show it as unavailable; never fall back to an address on another chain.
- When integration reads return no data, first check the RPC's actual chain ID, code at the address, ABI, and deployment version, then investigate page state.
- Frontend environment variables enter the browser bundle; include only public configuration. Keep server RPC credentials and signing keys on the server.

## Amounts and User Input

- Keep form amounts as decimal strings and onchain base units as `bigint` or the existing library's exact integer type.
- Fetch and cache the target token's `decimals`, scoped by chain and token address. Do not assume every ERC20 uses 18 decimals.
- Validate empty input, negative values, syntax, fractional digit count, and business limits before conversion. Explicitly reject input exceeding `decimals` instead of silently rounding.
- In viem, use `parseUnits(input, decimals)` and `formatUnits(value, decimals)` with the actual precision.
- Do not use `Number`, `parseFloat`, floating-point multiplication, or `10 ** decimals` for onchain amount calculations. Display truncation must not overwrite the underlying value.
- Format amounts with `Intl.NumberFormat` for the current locale and choose display precision explicitly. Preserve `bigint` or exact decimal strings; check the target browsers' support for exact string formatting first and use a precise decimal formatting approach when needed. Never convert to `Number` first.
- Do not pass localized display values directly to `parseUnits`. If inputs support localized separators, strictly normalize them to decimal strings according to the locale; otherwise state the accepted input format rather than guessing what a comma means.
- Serialize `bigint` using the project's decimal string convention or library serializer; do not pass it directly to `JSON.stringify`.
- Validate address syntax and reject the zero address only when the business requires it. Handle token balance, allowance, and native gas balance separately.

## Read and Wallet States

- Show loading, failure, empty, and success states. An RPC failure must not appear as a zero balance.
- Include account, chain, contract address, and call arguments in query identity. After an account or network switch, do not keep displaying the previous account's permissions or balances.
- Allow public reads that do not depend on an account while the wallet is disconnected. Run account-dependent reads only after all required parameters are available.
- Wallet switch requests can be rejected. Preserve the original state and allow a retry without repeatedly reopening the wallet automatically.
- Prevent duplicate submission of the same operation while awaiting a signature or pending confirmation. Discard old simulation results after the account, chain, or amount changes.

## TanStack Query and Onchain Refresh

- Reuse wagmi's existing query cache. Obtain invalidation keys from Hook results or the installed version's query-key/query-options helpers; do not guess wagmi's internal key structure.
- Custom query keys include the chain ID, contract address, function, arguments, and relevant account, spender, or block conditions that affect the result. Use serializable values, normalizing `bigint` arguments to strings in custom keys.
- After receipt-confirmed success, invalidate only the balances, allowances, supply, or business lists affected by that transaction. For example, approve refreshes the corresponding owner/spender allowance, while transfer refreshes relevant balances.
- Refresh using the chain and account captured at submission, not the wallet state after a later switch. Await `invalidateQueries`/refetch when needed. If the transaction succeeds but refresh fails, show the two results separately instead of relabeling the transaction as failed.
- `invalidateQueries` usually marks matching queries stale and refreshes active queries in the background. If the UI needs an immediate result, check `enabled`, static cache settings, and whether the query is active; do not assume every match refetches immediately.
- For changes caused by external transactions, choose event subscriptions, block-triggered refresh, or bounded polling to suit the page. Handle recovery reads after reconnecting, unsubscription, and unmount cleanup; do not create duplicate timers in each component.
- `staleTime` defines data freshness, not an automatic refresh interval. Configure `refetchInterval` when polling is required, considering visibility, RPC rate limits, and freshness needs. Avoid invalidating all site queries on every new block.
- Do not refetch raw onchain results when the locale changes. Translate and format amounts in the presentation layer; include locale in query identity only when returned content itself depends on language.

## Write Operation States and Results

Implement the following UI states instead of treating one library's `isPending` as the entire transaction lifecycle:

| State | Detection and presentation | Notification mapping |
| --- | --- | --- |
| Ready to submit | Valid input; account and target chain match | No toast needed |
| Simulating | Simulate with the actual account, target address, arguments, and `value` | Show form/button progress; decode and explain reverts on failure |
| Awaiting signature | Wallet request sent; awaiting confirmation or rejection | loading: Confirm in your wallet |
| Broadcast / awaiting confirmation | Hash received; wait for required confirmations on the submission chain | Update the same toast to confirming, with a transaction link |
| Success | Receipt execution succeeds and the business result meets the interface contract; refresh related queries | success: Operation confirmed |
| User rejected / canceled | Rejected before signing, or a cancellation replacement transaction is confirmed | info: Canceled; do not report onchain execution success |
| Failure | Definite submission failure or a reverted receipt | error: Understandable reason and an actionable next step |
| Status unknown | RPC timeout; broadcast or confirmation outcome remains uncertain | warning: Status pending verification; retain any known transaction link |

- A common viem flow is `simulateContract` → `writeContract` → wait for the receipt. Choose specific Hooks according to the installed version.
- Successful simulation applies only to the state used in that simulation; the actual transaction can still fail. A hash returned by a write call does not prove execution success.
- A successful receipt means the transaction did not revert, not necessarily that the business operation completed; for example, ERC20 can return `false`. Check the interface's return semantics during simulation, and verify business results through target contract events or state after confirmation when needed. Do not invent function return values from an ordinary receipt. If the result cannot yet be verified, show transaction execution and business verification separately; do not directly resubmit.
- Signing a message alone produces no transaction receipt. Display login or authorization signatures according to verification results without reusing “Transaction confirmed” copy.
- The table describes ordinary transactions. Adapt UserOperation and wallet batch results using [smart accounts](smart-accounts.md); do not wait for a transaction receipt using a userOpHash or batch ID as a transaction hash.
- Show successful L2 execution separately from the finality the business requires. See [deployment verification](deployment.md#chain-confirmation-fees-and-availability) for confirmation policies and full fees; do not apply one confirmation count to every chain.
- Associate each broadcast transaction with its submission chain, account, and business parameters. Continue tracking it on the original chain after a wallet switch.
- Handle replacement, speed-up, and cancellation by updating the hash being tracked. Do not report a successful cancellation receipt as success of the original operation.
- If a hash is known but waiting times out, retain an unknown/pending-verification state and keep querying that transaction. Do not automatically call the write operation again.
- Distinguish signature rejection, chain mismatch, insufficient funds, and contract errors from error types or causes. Show understandable messages and keep useful diagnostic context in logs with credentials removed.

## Token Approvals and Permit

- Determine the actual spender from a verified deployment. Read allowance by chain ID, token, owner, and spender. Skip approval when sufficient; do not default to unlimited allowance. Show the asset, recipient of the approval, and amount before signing.
- Handle approve and the business transaction separately in the ordinary flow: after a successful approval receipt, reread allowance, then simulate and submit the business call. Approval success does not complete a swap, deposit, or other operation. Preserve the existing approval state if the second step is canceled or fails.
- Verify the target token's approval rules. If it actually requires setting allowance to zero before setting a new amount, perform those steps according to its implementation; do not force an extra zeroing transaction on every ERC20. Use applicable interfaces from the installed OpenZeppelin version for contract-side wrappers.
- Use permit only when the token, account, and integration entry point all support it. Verify the actual variant, signing domain, nonce, deadline, owner, spender, and value. ERC-2612, DAI-style permit, and Permit2 are not interchangeable; consult official documentation for the applicable version and deployment when using Permit2.
- A permit signature expresses allowance authorization, not consent to arbitrary business operations or beneficiaries. The business entry point must independently constrain the payer, beneficiary, and parameters. Obtaining a signature does not change allowance; refresh based on the actual result after onchain execution. ERC-2612's deadline limits submission time and does not automatically expire an allowance already granted.
- In integrations you control, handle a permit submitted before your transaction. A consumed nonce alone must not block a still-valid business operation, but do not swallow arbitrary errors. Continue only when the actual allowance is sufficient and independent business authorization holds. Test already-submitted, expired, wrong-domain, and wrong-spender cases.
- Preserve an ordinary approve path. Do not assume contract wallets support standard ERC-2612 EOA signatures. On rejection or lack of support, offer an alternative without automatically requesting extra signatures or increasing approval amounts.
- See [DeFi development](defi.md) for swap and vault price protection and asset/share conversion. Handle atomicity and partial success of batched approve + call operations using [smart accounts](smart-accounts.md).

## react-toastify Notifications

- Place a shared `ToastContainer` in the common application layout, matching the site's theme, fonts, placement, and text direction. Keep operation state on the page as well as in transient notifications.
- Give each logical operation a stable `toastId` and advance through the table's states with `toast.loading` and `toast.update`. Deduplicate using operation state so Strict Mode, rerenders, or receipt polling do not repeatedly create notifications.
- Once a hash is available, associate the chain ID and actual transaction hash. On speed-up or replacement, update the same notification's link instead of creating a second, independent success notification.
- Explicitly set `isLoading: false` when loading ends, and choose type and closing behavior for success, failure, or unknown status. Do not show fabricated percentage progress during a long pending period.
- Bind `toast.promise` only to a Promise that covers the full meaning of its message. If the copy reports business success, the Promise must include the receipt and any business-result checks required by the interface; wrapping only the hash-returning `writeContractAsync` is insufficient.
- Share error mappings and i18n keys between pages and toasts. Do not toast every automatic background refresh; show recoverable network errors when they affect a user operation.

## SSR and Verification

- Handle server/client state boundaries only in projects using SSR. Put wallet access and Hooks in the correct client entry point.
- Configure wagmi SSR and any necessary initial-state restoration according to project versions. Do not access `window` or directly read browser storage on the server.
- Match the server's locale, theme, and initial state with the client. Isolate server request caches as required by the framework; never share an account-bearing QueryClient across users.
- Verify the main behaviors affected by the change: correct amount conversion, wrong network, rejected signatures, pending after broadcast, success, and revert.
- When changing caches or asynchronous flows, also verify account/chain switches and late responses from old requests. Amount tests must cover non-18-decimal tokens and values beyond the safe integer range.
- When changing wallet entry points, languages, or notifications, verify switching between supported languages, persistence after reload, consistent page/modal/toast language, light/dark themes, notification deduplication for the same transaction, and relevant data refresh after receipts. New projects must pass these checks in Simplified Chinese and English by default.
- Prefer existing test infrastructure and a local chain. If a real wallet cannot be connected, state the level actually verified; do not claim wallet end-to-end testing.

## Official References

- [RainbowKit installation](https://rainbowkit.com/docs/installation) / [Package dependencies](https://github.com/rainbow-me/rainbowkit/blob/main/packages/rainbowkit/package.json): use the selected release's peerDependencies; the main branch is only an entry point for discovery.
- [RainbowKit theming](https://rainbowkit.com/docs/theming) / [Custom connect button](https://rainbowkit.com/docs/custom-connect-button) / [Localization](https://rainbowkit.com/docs/localization): public configuration for wallet UI within the site.
- [React-Toastify updates](https://fkhadra.github.io/react-toastify/update-toast/) / [Deduplication](https://fkhadra.github.io/react-toastify/prevent-duplicate/) / [Promises](https://fkhadra.github.io/react-toastify/promise/): maintain notification state for one operation.
- [TanStack Query keys](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys) / [Invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation) / [Defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults): select documentation for the installed version.
- [wagmi and TanStack Query](https://wagmi.sh/react/guides/tanstack-query): use public query keys for invalidation.
- [wagmi setup and dependencies](https://wagmi.sh/react/getting-started): check configuration against the installed version.
- [viem simulateContract](https://viem.sh/docs/contract/simulateContract) / [writeContract](https://viem.sh/docs/contract/writeContract): the distinction between simulation and writes.
- [wagmi transaction receipts](https://wagmi.sh/react/api/hooks/useWaitForTransactionReceipt): confirmations, replacement, and chain selection.
- [viem value conversion](https://viem.sh/docs/ethers-migration#display-logic--input-utilities): precise amount parsing and formatting.
- [wagmi SSR](https://wagmi.sh/react/guides/ssr): hydration and persistence when needed.
- [ECMA-402 numeric conversion](https://tc39.es/ecma402/#sec-tointlmathematicalvalue): Intl's specification for exact numeric values; check target runtime compatibility separately.
- [ERC-2612](https://eips.ethereum.org/EIPS/eip-2612): permit domains, nonces, deadlines, and existing variants.
- [ERC-20](https://eips.ethereum.org/EIPS/eip-20#methods): callers must handle business failures that return `false`.
- [OpenZeppelin IERC20Permit](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v5.4.0/contracts/token/ERC20/extensions/IERC20Permit.sol): authorization intent, early submission, and non-permit entry points. The linked source version is a semantic reference; implement against the project's installed version.
