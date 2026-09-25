# DeFi Integration and Protocol Development

Read the relevant sections when the task involves swaps, pricing, vaults, or lending. Do not add financial mechanisms to ordinary tokens or display-only DApps. First distinguish integrating an existing protocol from implementing a protocol, and preserve the existing model and parameter sources.

## Define Integration and Business Boundaries

- Record the target chain, protocol version, deployment-address sources, assets and units, fees, fund recipients, and interfaces and economic constraints that must remain compatible.
- Check dependencies such as routers, pools, vaults, and oracles against official deployment information and onchain code. Do not use example addresses, testnet configuration, or another version's ABI in the target environment.
- Define supported token behavior, including transfer fees, rebasing, wrapped native assets, and callbacks. Reuse the transfer and accounting constraints in [Contract Development](contracts.md).
- When integrating an established protocol, follow its actual parameters and limits. For a new model, first express fee, price, liquidity, and bad-debt assumptions as testable rules; do not guess risk parameters from commonly used values.

## Swaps: Quotes, Limits, and Routes

- Distinguish exact input from exact output. Explain the input, expected output, protocol fees, price impact, and user slippage limit; record the chain, route, parameters, and time or block associated with a quote.
- A quote helps construct a transaction but does not guarantee its execution price. Invalidate old quotes when input, account, chain, or route changes, and recheck the current transaction parameters before signing.
- For exact input, enforce a meaningful minimum amount received; for exact output, cap the amount spent. Use integers and explicit rounding directions. Do not set the minimum output to zero or remove meaningful tolerance limits to bypass failures.
- Establish the user-accepted deadline before signing, and ensure the execution path enforces it. Generating a fresh deadline from `block.timestamp` after the contract receives a transaction does not limit its time in the queue. If the router has no deadline parameter, check its wrapper entrypoint or another effective constraint.
- Minimum output, maximum payment, and deadline limits must reach the final execution parameters. Displaying them in the UI or simulating once does not constrain onchain execution.
- Validate the actual call target, allowed routes/pools, token order, fee tier, and final recipient. For aggregator-provided calldata, also check the target, value, and identifiable fund constraints; an external quote response is not authorization for arbitrary calls.
- Check allowance owner, token, spender, and amount. Handle Permit/Permit2 domains, nonces, deadlines, and amounts according to the actual version. Do not assume token permission binds the route, recipient, or all transaction parameters; wrapper entrypoints must still validate the caller and use of funds. See [DApp Integration](dapp.md) for shared approval UX.
- Distinguish transaction failure from quote invalidation. Exact-output swaps, price limits, or partial fills may leave input assets unspent; refund balances and handle excess approvals according to the route's semantics rather than leaving user assets in a wrapper contract.
- If the integration requires swap callbacks, flash callbacks, or hooks, verify the caller's relationship to the expected pool/entrypoint and bound payable assets and amounts. Arbitrary addresses must not collect funds through forged callbacks.

## Oracles: Units, Freshness, and Failure Behavior

- Check the feed's target chain, proxy address, asset pair, quote direction, and intended use. Normalize token decimals and feed decimals separately rather than assuming a fixed precision for both.
- When composing prices, check each component's units, rounding, and update time. Display prices, executable quotes, and lending collateral valuations serve different purposes; do not substitute an easily manipulated instantaneous pool price for risk pricing.
- Use an interface that exposes update timestamps. For asset prices expected to be positive, check value validity, missing or abnormal timestamps, and maximum acceptable data age. Reverts and invalid data must enter an explicit rejection or fallback path.
- Choose freshness thresholds from the specific feed's update mechanism and the application's tolerance, not an arbitrary copied heartbeat. Define fallback-source conditions and units; never silently return zero or reuse stale values indefinitely after failure.
- Chainlink `latestRoundData` exposes `updatedAt` for time checks. `answeredInRound` is deprecated; old round-check templates are not a substitute for freshness validation. Check the current official specification for the feed type in use.
- For L2 integrations where prices determine collateral, liquidation, or settlement, check the chain's sequencer risks and available uptime feeds. Where applicable, validate uptime state, state timestamps, and a recovery grace period; abnormal initialization state must not count as recovery.
- Choose the sequencer grace period and permitted operations according to the business. Distinguish risk-increasing borrowing/withdrawal, liquidation, and repayment paths; do not indiscriminately block every risk-reducing action with one check.
- For TWAP or custom pricing models, state the observation window, available history, liquidity, and manipulation-cost assumptions. Using an oracle alone does not prove that prices cannot be manipulated.

## ERC-4626: Assets, Shares, and Rounding

- Distinguish assets, shares, `totalAssets`, and the vault's current token balance. Accounting for assets deployed into strategies, unrealized yield, fees, and losses must follow the vault's model.
- `convertToAssets` / `convertToShares` are idealized conversions. Quote actual operations with the corresponding `preview*` method and independently check `max*` limits. A successful preview does not prove that limits, balances, approvals, or execution conditions are satisfied.
- Verify the standard's directional relationship between preview and execution in the same state rather than requiring all conversions to be losslessly equal:

| Operation | Preview bound to check |
| --- | --- |
| deposit | Previewed shares received must not exceed actual shares received |
| mint | Previewed assets required must not be less than actual assets required |
| withdraw | Previewed shares consumed must not be less than actual shares consumed |
| redeem | Previewed assets received must not exceed actual assets received |

- Reflect custom fees consistently in previews, execution, and event semantics. Check each operation's rounding direction against the standard and business composition so repeated small deposits/withdrawals cannot accumulate cost-free gains.
- Check first deposits into an empty vault, small deposits rounded to zero shares, direct donations changing the exchange rate, and deposits after full redemption. Do not assume an external vault excludes these behaviors.
- With OpenZeppelin, check the installed version's virtual assets/shares, decimal offset, and overridden functions. Do not replace its implementation with an older mitigation copied from a tutorial, or treat inheritance from a standard component as validation of the entire strategy.
- Apply the business's minimum shares/minimum assets or maximum payment limits to deposits and withdrawals through a router/wrapper that enforces them. A previous preview does not protect the user's final execution outcome.
- Test asset receipt, recipients, authorization to spend an owner's shares, and external strategy calls separately. Support fee-on-transfer or rebasing assets only when the implementation explicitly supports and validates them.

## Lending, Collateral, and Liquidation (When In Scope)

- Identify the actual market model, collateral and debt assets, interest accrual timing, borrowing capacity, and liquidation conditions. Read LTV, liquidation thresholds, incentives, caps, and mode settings from the target protocol; do not transplant constants from another market.
- Before borrowing, withdrawing, or disabling an asset as collateral, check post-operation constraints using current prices and accrued debt. A health metric shown in the UI does not replace the contract's checks.
- Distinguish principal, accrued interest, debt shares, available liquidity, and protocol fees. Repayment, liquidation, and withdrawal must use consistent units and rounding rules.
- For liquidation, verify eligibility, repayment limits, debt assets actually received, collateral deducted, incentives, and fees. Handle collateral exhaustion, remaining dust debt, and bad debt; transaction success alone is insufficient.
- Under applicable assumptions such as fixed prices, define invariants for fund flows, debt changes, fee allocation, and share relationships. Keep the reference model independent of the implementation and justify error bounds by precision.
- Price shocks can cause insolvency, and some liquidations do not improve health. Distinguish solvent, liquidatable, and bad-debt states according to the model; do not assert that collateral always exceeds debt.
- If the protocol uses flash loans, verify the authorized initiator/callback caller, recipient, and repayment of principal plus fees. Account for external flash liquidity available within one transaction when defining relevant price and share assumptions.

## Conditional Tests and Delivery

Use [Testing and Debugging](testing.md) to select regression, fuzz, invariant, and fixed-block fork tests for the paths actually involved:

| Work in scope | Useful boundaries and failure cases |
| --- | --- |
| Swaps | State changes after a quote, slippage boundaries, expiry, wrong route/recipient, insufficient balance/allowance, refunds, and forged callbacks |
| Oracles | Different decimals, invalid prices/timestamps, stale data, call failures, unsynchronized sources, and applicable L2 outage/recovery grace-period boundaries |
| ERC-4626 | Preview/execution relationships, fees and rounding, first deposits and donations, small deposits and zero shares, losses, and deposits after full redemption |
| Lending | Elapsed interest accrual, both sides of borrowing/liquidation thresholds, price shocks, partial/full repayment, collateral exhaustion, and bad-debt accounting |

- Economic invariant tests must execute valid deposits/withdrawals, borrowing/repayment, or liquidations. Repeated reverts caused by invalid inputs do not validate an economic model.
- Use forks to verify integration with the actual target deployment. Use controlled mocks or local models for exceptional conditions difficult to trigger at a historical block. Fixed-block tests do not prove future prices, liquidity, or parameters remain unchanged.
- Report parameter sources, units, fee/rounding policies, oracle failure/recovery behavior, actual tests, and unverified assumptions. When changing only an integration, do not present the result as a security guarantee for the underlying protocol or economic model.

## Official References (Use the Target Protocol Version)

- [Uniswap Single Swaps](https://developers.uniswap.org/docs/protocols/v3/guides/swapping/single-hop-swapping): swap input/output limits, deadlines, and refunds of unused input; use the relevant documentation for other routers.
- [Chainlink Data Feeds API](https://docs.chain.link/data-feeds/api-reference), [Developer Responsibilities](https://docs.chain.link/data-feeds/developer-responsibilities): feed interfaces, units, freshness, and application-side data constraints.
- [Chainlink L2 Sequencer Uptime Feeds](https://docs.chain.link/data-feeds/l2-sequencer-feeds): supported networks, state timestamps, initialization differences, and recovery grace periods.
- [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626): precision and interface semantics for convert, preview, max, and deposit/withdrawal operations.
- [OpenZeppelin ERC-4626](https://docs.openzeppelin.com/contracts/5.x/erc4626): first-deposit/donation risks, virtual offsets, and fee extensions.
- [Aave Health Factor & Liquidations](https://aave.com/help/borrowing/liquidations): an example of lending health and liquidation constraints; still check the target market and version rather than generalizing its parameters.
