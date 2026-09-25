# Smart Accounts and Wallet Capabilities

Read only when the task involves smart accounts, contract-wallet signatures, ERC-4337, EIP-7702, batched calls, sponsorship, or session keys. Ordinary wallet connection does not create, migrate, or upgrade an account by default. Preserve existing account implementations and providers within the task's scope.

Navigation: [Mechanisms](#distinguish-the-mechanisms) · [Compatibility](#check-account-and-service-compatibility) · [Signatures](#contract-wallet-signatures) · [UserOperation](#erc-4337-operation-lifecycle) · [Fees](#nonces-fees-and-paymasters) · [7702](#eip-7702-delegation) · [Batching](#eip-5792-capability-discovery-and-batching) · [Session keys](#session-keys-when-needed) · [Verification](#verification-and-delivery).

## Distinguish the Mechanisms

| Mechanism | Purpose | Do not assume |
| --- | --- | --- |
| Smart account | Account logic defines validation, execution, recovery, and other capabilities | Every smart account uses the same EntryPoint or supports every module |
| ERC-4337 | Submit, validate, and execute UserOperations through a bundler and EntryPoint | A UserOperation is an ordinary onchain transaction, or requires a paymaster |
| ERC-1271 | A contract account declares whether a signature is valid | Recovering the owner's EOA address proves contract-wallet authorization |
| EIP-7702 | An EOA authorizes persistent code delegation | Delegation is a temporary one-off call, or automatically provides ERC-4337 capabilities |
| EIP-5792 | Wallet batch calls, status queries, and capability discovery | Batches always execute atomically, or the wallet necessarily uses ERC-4337 internally |

## Check Account and Service Compatibility

- Record the target chain, wallet/account implementation and version, owner/validator, factory, deployed or predicted address, and SDK/lockfile versions. Use account addresses and owner addresses for their distinct purposes.
- For ERC-4337, check the EntryPoint address, deployed code, version, bundler support, and paymaster support. Execution RPC, bundler RPC, and paymaster services are different interfaces.
- Validate the combination using version-matched SDK, account, and provider documentation plus actual onchain state. EVM compatibility does not establish support for a particular EntryPoint, 7702, or wallet capability.
- Prefer the SDK's account adapters, nonce handling, encoding, and gas preparation. Do not mix UserOperation, hash, or paymaster encodings from different EntryPoint versions.
- Check local type definitions and official APIs before coding. For example, viem's `createBundlerClient`, `sendUserOperation`, and wallet `sendCalls` serve different paths; do not invent Hooks or parameters from similar names.
- Preserve existing wallet connection and query integrations. Do not create a second React wallet state system merely to use smart accounts. Add account/service configuration only when required by the task.

## Contract-Wallet Signatures

- Use onchain ERC-1271 verification or an equivalent SDK path for contract wallets. Check the standard success value `0x1626ba7e`; a call that does not revert is not sufficient, and signatures need not all be exactly 65 bytes.
- viem's Public Client `verifyMessage` / `verifyTypedData` Actions differ from the pure utility functions with the same names. EOA recovery alone cannot replace contract-account verification.
- Bind verification to the correct chain, account, message domain, and business context. Changes to the wallet owner, validator, or related state can change the validity of old signatures; do not cache a past success permanently.
- If undeployed accounts are supported, verify the counterfactual signature scheme, such as ERC-6492, using the actual wallet and SDK. An address temporarily lacking code does not prove that its signature is an EOA signature.

## ERC-4337 Operation Lifecycle

1. Prepare calls using the actual sender, target chain, and EntryPoint. For the first operation, also check account deployment/initialization data and the predicted address.
2. Use the matching SDK/bundler version to estimate and simulate validation and execution. Confirm the signing method, validity window, nonce, and fee source; a successful ordinary `eth_call` does not replace full UserOperation validation.
3. Sign and submit within the task's authorization. Save the business operation ID, sender, EntryPoint, nonce, and UserOperation hash. Bundler acceptance does not prevent later dropping or validation failure.
4. Query the UserOperation receipt and record its associated onchain transaction. Check inclusion, operation execution success, and achievement of the business objective separately.
5. Track the final outcome according to the target chain's confirmation policy, then refresh relevant queries or business records. Follow the [DApp State Conventions](dapp.md) for UI and notifications.

| Identifier | Tracking method |
| --- | --- |
| `userOpHash` | Bundler UserOperation query/receipt interfaces; do not treat it as an ordinary transaction hash |
| `transactionHash` | The onchain receipt of the actual bundle transaction; one transaction may contain several UserOperations |
| `batchId` | The wallet/SDK calls-status interface; do not directly construct a transaction-explorer URL from it |

- viem's `waitForUserOperationReceipt` returns an operation receipt. Check its `success`, failure reason, logs, and associated transaction rather than only the outer `receipt.status`.
- Check the account's batch failure semantics. If inner calls may fail without reverting the operation, operation-level success may still leave the business objective unmet. Verify each required result using relevant events, return semantics, and state.
- On RPC timeout or a missing receipt, keep the outcome unresolved and query the known operation and nonce. Do not blindly resend with another nonce or declare failure merely because the query interface does not yet know the operation.
- Replace or speed up an operation according to the actual bundler policy, linking the original operation to the new hash. Recheck fees, signatures, and paymaster data; do not assume a fixed fee-bump ratio or a universal cancellation API.

## Nonces, Fees, and Paymasters

- Keep UserOperation nonces separate from the owner's ordinary transaction nonce. Manage concurrency according to the account/EntryPoint nonce-key and sequence model; multiple workers must not independently allocate the same nonce channel.
- Distinguish gas for calls, account validation, pre-verification, and paymaster stages. Use estimates from the matching version; ordinary transfer gas or arbitrarily increased limits are not substitutes for diagnosis.
- Sponsorship is optional. State who pays, whether settlement uses ERC20, limits, and quote expiry. If sponsorship is rejected, expires, or runs out, do not silently charge the user instead.
- A paymaster stub used for estimation is not final authorization. After callData, nonce, gas, or fees change, obtain fresh valid data and any required signatures according to the protocol.
- Use combined-service shortcuts only when the service explicitly also supports paymaster RPC. An ordinary bundler endpoint is not automatic free sponsorship.
- Failed operations may still consume nonce and gas. Check actual receipts plus account and EntryPoint state before recovery; distinguish business failure from fees already incurred in the UI.

## EIP-7702 Delegation

- Check support in the target chain, wallet, SDK, and delegated implementation. Prepare delegation only when explicitly required and covered by the task's authorization; wallet connection alone must not trigger an upgrade or authorization request.
- Delegated target code executes in the account's context with much broader authority than an ordinary contract call. Reuse the selected wallet's reviewed implementation and initialization flow; do not generate an ad hoc delegate contract to replace its design.
- Check the authority, delegation target, chain ID, authorization nonce, and actual broadcaster. `chainId = 0` grants a cross-chain authorization scope; do not use it as a convenient default.
- Delegation persists until changed or cleared. A revert during transaction execution does not automatically undo already-processed delegation; after failure, read delegation state separately from the business outcome.
- Do not use `code.length == 0`, an empty `eth_getCode` result, or `tx.origin` comparisons as reliable wallet-type, authorization, or reentrancy checks. A delegated EOA can have code.
- When revoking or migrating delegation, check effects on account storage, modules, and existing asset approvals. Clearing delegation does not clear storage, revoke token allowances, or invalidate every historical signature.

## EIP-5792 Capability Discovery and Batching

- Query `wallet_getCapabilities` or the SDK equivalent for the connected account and target chain. Recheck after account/chain changes rather than hard-coding support by wallet brand.
- Atomic capability states `supported`, `ready`, and `unsupported` differ. `ready` still requires the user to accept an upgrade; it is not an already-active capability. Use a conservative path if capability queries fail or capabilities are absent.
- Explicitly require atomicity when the business requires all calls to succeed together. Protocol fields such as `atomicRequired` may differ from SDK parameters such as viem's `forceAtomic`; check and test the mapping for the installed version.
- Fall back to sequential transactions only when partial completion is acceptable, explaining per-transaction signatures, fees, and partial-success semantics. Do not automatically enable SDK fallback to bypass missing atomicity support.
- Save the batch ID, chain, account, and call order, and use the corresponding calls-status query. A synthetic ID generated by SDK fallback may not work with the wallet's native RPC.
- Check batch status, the `atomic` flag, and receipts for executed calls. On partial success, retain each step's result and recover only necessary steps; do not replay the entire approve, transfer, or other completed sequence.
- If a batch has been submitted but its outcome is unknown, continue querying its original ID. Do not switch to individual resubmissions after a timeout. Do not mark required capabilities optional, since ignoring them could change fee or execution semantics.

## Session Keys (When Needed)

- Check the actual permission model supported by the account, validator, or module. A wallet connection session, a website login session, and a session key able to execute account operations are distinct capabilities.
- Scope permissions to the target chain, account, contracts, functions, necessary parameters, asset/amount budgets, and validity window, and provide revocation. Do not allow arbitrary calls, delegatecall, or module administration when the business does not require them.
- Enforce permissions in the account or validation module, not only through frontend filtering. Treat restricted keys as credentials; keep them out of logs, source repositories, and unprotected persistent browser storage.
- Test expiry, revocation, disallowed targets/functions, budget overruns, replay, and concurrent budget consumption. Ensure batching or proxy paths cannot bypass restrictions.

## Verification and Delivery

- Test the paths in scope: first-operation deployment and already-deployed accounts, wrong signatures/domains, nonce conflicts, validation rejection, execution reverts, paymaster failures, timeouts, and replacement recovery.
- For 7702, cover authorization validity, delegation state after execution failure, and revocation. For 5792, cover unsupported capabilities, rejected upgrades, atomicity requirements, and partial success.
- Verify actual SDK and service interfaces locally or on an appropriate testnet. If only bundler or wallet responses are mocked, state that limit rather than claiming full onchain verification.
- Report chain/account/EntryPoint/SDK versions, capabilities used, fee sources, operation and transaction identifiers, and verification results. Smart-account mechanisms outside the task do not need implementation.

## Official References

- [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337): EntryPoint, UserOperation, nonce, and paymaster semantics; check the specific deployed version.
- [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) / [viem Signature Verification Action](https://viem.sh/docs/actions/public/verifyMessage): contract-account signatures and onchain state.
- [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): code delegation, authorization scope, and persistence after failure.
- [EIP-5792](https://eips.ethereum.org/EIPS/eip-5792): capability discovery, atomicity, and batch status.
- [viem Bundler Client](https://viem.sh/account-abstraction/clients/bundler) / [sendUserOperation](https://viem.sh/account-abstraction/actions/bundler/sendUserOperation) / [Wait for an Operation Receipt](https://viem.sh/account-abstraction/actions/bundler/waitForUserOperationReceipt): SDK operation paths.
- [viem Paymaster Client](https://viem.sh/account-abstraction/clients/paymaster) / [sendCalls](https://viem.sh/docs/actions/wallet/sendCalls): sponsorship and wallet batching; do not apply the documentation's current API to older dependencies without checking.
