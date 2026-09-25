# Deployment and integration

Use this reference for local and testnet deployment, deployment failure recovery, and ABI/address synchronization. Preserve existing project scripts and tools; new Foundry projects can use the workflow below.

Navigation: [Scope](#establish-the-target-and-scope) · [Build inputs](#pin-reproducible-inputs) · [Signing credentials](#cast-wallet-and-signing-credentials) · [Local workflow](#local-workflow) · [Testnets](#testnet-workflow) · [Chain differences](#chain-confirmation-fees-and-availability) · [Recovery](#failure-recovery) · [Permissions and operations](#permission-handover-and-operations) · [Deliverables](#deliverables).

## Establish the target and scope

- Identify the target chain, contracts, constructor arguments, initialization calls, administrative accounts, and signing method from the task and existing configuration.
- Continue authorized development work such as builds, tests, local deployment, and simulation. A fork simulation using a remote RPC does not broadcast to that network.
- Continue testnet or mainnet broadcasts within the chains and operations already authorized in the current conversation. Do not request permission again merely because the workflow advances to another step.
- If the task covers deployment preparation only, or broadcast authorization is unclear, finish the scripts, parameters, tests, and simulation before clarifying the specific broadcast action.
- Stop only the affected action when required signing capability, authorization, or critical parameters are missing. Continue local work that can still be completed.
- Read existing proxy, factory, multisig, CREATE2, or upgrade workflows before acting; do not replace them with ordinary direct deployment.

## Pin reproducible inputs

- Check tool versions and command help. Pin solc, dependencies, optimizer settings, EVM target, linked libraries, and constructor arguments.
- Before release, check relevant compiler bugs using [contract development](contracts.md), and complete applicable tests and static analysis using the [testing strategy](testing.md). Record unresolved items during preparation; source verification is not security validation.
- The target chain must support the EVM features used by the compiled artifacts. Do not arbitrarily raise the EVM target to eliminate compilation errors.
- Distinguish deployer from owner/admin explicitly in deployment scripts. Do not let the script runner's address implicitly determine the final administrator.
- Produce reviewable chain, public account address, target contract, and parameter details. Do not print environment files, private keys, seed phrases, or keystore passwords.
- Use the Cast Wallet keystore workflow below for local developer wallets. Existing hardware wallets or remote signing services may be retained. Confirm signing options with the local `forge script --help`.

## Cast Wallet and signing credentials

- Use Foundry's Cast Wallet to create or import encrypted JSON keystores, normally in `~/.foundry/keystores`. Distinguish wallet aliases, public addresses, and intended uses, avoiding name collisions. Keep keystores outside the repository and frontend-accessible directories, with restricted local read permissions.
- Import existing wallets interactively with hidden input. Have the developer enter the private key and password in their own interactive terminal; do not ask for secrets in chat or through automation that records input. Specify an output directory when creating a wallet; bare `cast wallet new` may print the private key to the terminal.

```bash
# Choose one as needed; first confirm that the example alias evm-deployer is unused
cast wallet import evm-deployer --interactive
cast wallet new "$HOME/.foundry/keystores" evm-deployer
```

- Use `vm.startBroadcast()` or a verified public sender in deployment scripts. Do not use `vm.envUint("PRIVATE_KEY")` / `startBroadcast(privateKey)` to load a real private key from `.env`. Select the encrypted account in Forge with `--account evm-deployer`, or the appropriate `--keystore` for a custom location, and unlock through hidden password input.
- Never store private keys or seed phrases in `.env`, `.env.local`, shell profiles, configuration, PM2 configuration, repositories, or logs. Do not store keystore passwords there or alongside the keystore. Do not bypass the interactive flow with `--private-key`, `--unsafe-password`, or plaintext password arguments.
- `.env.example` should describe required configuration only. It may contain chain IDs, RPC configuration names, public addresses, and account aliases, but must not instruct developers to add real private keys. A plaintext private-key file violates this convention even when excluded by `.gitignore`.
- CI and unattended backends cannot rely on an interactive unlock prompt. Use controlled external signing, or an existing encrypted keystore with independent key-management facilities. Supply passwords only temporarily as needed and clear them afterward; do not decrypt and export private keys or create a temporary plaintext `.env`. Complete builds and simulation when signing is unavailable, and report signing setup separately as pending.
- Anvil's public test accounts are for isolated local nodes only. Use impersonation or unlocked local accounts for tests without importing a real developer wallet. Store encrypted keystore backups separately from their passwords.

## Local workflow

1. Run relevant contract tests and compile; fix issues related to this deployment.
2. Start or reuse a verified local Anvil node. Development unlocked accounts are for that node only.
3. Simulate the deployment script, checking contracts, constructor arguments, and initialization. Do not put simulated artifacts in the authoritative deployment manifest.
4. Broadcast the same script to the local node, obtain actual receipts, and verify deployed code and important initial state.
5. Connect the local ABI, chain ID, and confirmed addresses to the frontend, then complete the target read and write flows.

These commands show the expected shape. Substitute the project's script and public deployer address before running them; `EVM_DEPLOYER` is an address, not a private key:

```bash
forge build
forge script script/Deploy.s.sol:DeployScript --rpc-url http://127.0.0.1:8545 --sender "$EVM_DEPLOYER"
forge script script/Deploy.s.sol:DeployScript --rpc-url http://127.0.0.1:8545 --sender "$EVM_DEPLOYER" --unlocked --broadcast
```

`vm.startBroadcast` / `vm.stopBroadcast` mark script calls that should become transactions; the CLI's `--broadcast` sends them.
Simulation without `--broadcast` does not prove that a contract exists on the RPC's chain. Inspect wrappers too: they may broadcast or execute external commands themselves.

## Testnet workflow

1. Query the chain ID through the actual RPC and compare it with configuration and the user's target. Check the signer's public address, gas balance, constructor arguments, and asset or permission recipients.
2. Simulate against target-chain state without broadcasting, using the sender and parameters intended for the broadcast. Investigate any revert first.
3. Broadcast within the authorized scope using the project's signing method, recording every transaction hash. Do not add `--skip-simulation` merely to bypass a failure.
4. Wait for receipts and verify status, deployed addresses, code, and important configuration such as owner, initial supply, or dependency addresses.
5. Submit source verification when the task requires it, and record the verifier's actual status. Verification failure does not mean deployment failed.

Source verification must use the compiler version, optimizer settings, constructor arguments, and linked libraries used for deployment. Retry verification alone; do not redeploy the contract to retry verification.
Apply these input and result checks to mainnet while following the project's release workflow. Authorization for testnet deployment does not imply mainnet authorization.

## Chain confirmation, fees and availability

- Define execution outcomes, conditions for recognizing transactions in business state, and finality conditions for the target chain. Use the same policy in the frontend, indexer, and release workflow. A successful receipt alone does not establish irreversibility; choose confirmations and waiting periods according to the chain and business risk.
- For L2s, consult the chain's official sequencing, data submission, and finality model. OP Stack's unsafe/safe/finalized distinction, for example, does not apply universally. Bridge withdrawal challenge or waiting periods are separate from ordinary L2 transaction confirmation.
- Estimate total fees, including L1 data fees and chain-specific costs beyond execution gas. Use the SDK's chain-specific interfaces instead of always treating `gas × gasPrice` as the total. Allow for these costs in balance checks and UI estimates, and state that estimates may change.
- Distinguish RPC service failure from a stalled sequencer or chain. For the former, use a verified endpoint on the same chain if available. For the latter, preserve submitted operations, stop pointless retries, and check their state after recovery; changing RPCs or rebroadcasting does not resolve the underlying outage.
- For L2 DeFi operations that depend on prices, also apply the [DeFi oracle rules](defi.md) for sequencer status and recovery grace periods. RPC reachability alone is insufficient.

## Failure recovery

| Symptom | Next step |
| --- | --- |
| Simulation reverts | Inspect the trace/custom error, sender, permissions, parameters, and onchain dependencies |
| Broadcast times out or disconnects | Check known hashes, sender nonce, broadcast records, and chain state to determine whether transactions were accepted |
| Receipt shows failure | Identify the failed transaction and cause; earlier successful transactions remain effective |
| A multi-transaction script completes partially | Record completed steps and prepare remaining calls from chain state, avoiding duplicate initialization or transfers |
| Source verification is pending or fails | Check the verification request or correct its parameters, retaining the deployed address |

- A timeout does not mean nothing was sent. When state is uncertain, stop new broadcasts, preserve diagnostic information, and do not blindly rerun the deployment script.
- `forge script --resume` does not simulate again and depends on the original transaction nonces. Check sent transactions and the account nonce before deciding to use it.
- Do not automatically repeat the same business action with a new nonce, add funds, switch networks, or replace administrative accounts to recover a task.
- Keep simulated predicted addresses separate from actual receipts. Publish only confirmed deployments as usable addresses.

## Permission handover and operations

- Execute handovers only as part of release or permission-change tasks. Verify the target chain and the final owner/admin, multisig, or governance address's ability to receive and exercise the required permissions. List the deployer's temporary and permanent roles. Frontend configuration alone does not prove a permission change.
- Two-step ownership requires acceptance by the new owner. In systems with multiple roles, check both roles and their administrators. For timelocks, verify proposers, executors, delay, and administration to avoid locking governance. Do not automatically add multisigs or timelocks to simple contracts.
- First prove in simulation or tests that the target administrator can perform required operations. After onchain acceptance or role grants, verify actual state. Revoke temporary deployer permissions within the authorized handover scope and verify that those calls are no longer allowed. If the recipient's signature is missing, mark only that step as pending.
- Release handover should include relevant operational observations: permission or implementation changes, important asset events, indexing progress, and prolonged pending operations. Identify owners, triggers, and recovery entry points. Configure monitoring only as needed for the task; do not subscribe to services or create background schedules by default.
- Distinguish recovery targets: rolling back frontend or backend versions does not undo chain state or automatically reverse database migrations. Non-upgradeable contracts have no direct rollback; replacing a proxy implementation also does not undo past state changes.
- Recovery plans must use existing, authorized pause, upgrade, migration, or repair mechanisms with defined executors and verification steps. Do not add withdrawal backdoors or administrative powers for convenience. Recovery transactions still require authorization for the specific chain and operation.

## Deliverables

- Preserve the project's deployment manifest format. For a new project, record at least chain ID, network purpose, contract name, address, transaction hash, and deployment block.
- Associate the source commit or identifiable build version, ABI artifacts, compiler settings, and required constructor arguments so the deployment can be reproduced and verified.
- Record the public addresses of the signer and final administrator, initialization outcomes, source-verification status, and available block-explorer links.
- Synchronize ABI and addresses to the DApp in the same change. Resolve addresses by chain; do not present placeholder addresses as valid deployments on unsupported networks.
- Resetting a local node may invalidate its deployment manifest. Integration entry points should detect missing code instead of continuing to display an earlier success.
- Distinguish "compiled," "simulation succeeded," "broadcast," "receipt succeeded," and "source verified" in reports. Claim only stages supported by evidence.
- Before committing raw logs or tool artifacts, inspect them for credentials, absolute paths, and unrelated runtime data. Retain required public deployment data in the manifest.

## Official references

- [Foundry deployment and source verification](https://getfoundry.sh/forge/deploying): deployment commands and broadcasting.
- [Foundry Cast](https://getfoundry.sh/cast/overview): wallet command entry point; confirm creation, import, and keystore options with the installed `cast wallet new --help`, `cast wallet import --help`, and `forge script --help`.
- [Foundry startBroadcast](https://getfoundry.sh/reference/cheatcodes/start-broadcast): transaction boundaries within scripts.
- [Foundry scripting internals](https://github.com/foundry-rs/foundry/blob/master/docs/dev/scripting.md): simulation, sending, and resume semantics; confirm CLI options with the installed `forge script --help`.
- [OpenZeppelin Access Control](https://docs.openzeppelin.com/contracts/5.x/access-control): two-step ownership, roles, multisigs, and timelocks.
- [OP Stack Finality](https://docs.optimism.io/op-stack/transactions/transaction-finality), [Fees](https://docs.optimism.io/op-stack/transactions/fees), and [Sequencer Outages](https://docs.optimism.io/op-stack/protocol/outages): confirmation, fee, and outage behavior for that chain; consult the corresponding official specification for other chains.
- [Ethereum contract upgrades](https://ethereum.org/developers/docs/smart-contracts/upgrading/): immutable contracts, migrations, and proxy upgrade boundaries.
