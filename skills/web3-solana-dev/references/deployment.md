# Deployment and integration

Use for deployment preparation, local integration, public releases, upgrades, and recovery. Preserve the project's release tools and loader model. Read [program development](programs.md) for state compatibility and [testing](testing.md) for behavioral verification.

## Resolve the target and build

- Identify the cluster, actual RPC, program ID, fee payer, program-address creation signer, upgrade authority, application administrators, and any buffer authority separately. A program-address keypair is not automatically the program's upgrade authority or a spending wallet. Query the RPC's genesis hash when checking cluster identity; an address or endpoint label alone does not establish the network.
- Compare the intended address with Rust `declare_id!`, `Anchor.toml`, generated IDL/client metadata, and the deployment manifest. Do not regenerate program keys or rewrite a live program ID just to resolve a build mismatch. Keep different cluster deployments explicit.
- Record the source revision, Cargo/JavaScript lockfiles, Anchor CLI and crates, Solana/Agave tools, SBF platform-tools/architecture, and build flags. The installed host Rust version alone does not identify the SBF compiler. Use supported combinations; do not upgrade every dependency independently. Inspect installed command help before applying deployment or IDL instructions from another release.
- Complete relevant tests and build the actual SBF artifact. Test its compatibility with the intended runtime. Estimate program storage, any extension or buffer allocation, transaction fees, and required SOL; avoid automatically funding a shortfall or changing the payer.

Read-only inspection examples; substitute the intended RPC and public program address:

```bash
anchor --version
solana --version
solana program deploy --help
solana --url "$SOLANA_RPC_URL" genesis-hash
solana --url "$SOLANA_RPC_URL" program show "$SOLANA_PROGRAM_ID"
```

Prefer explicit per-command cluster selection to changing the developer's global CLI configuration. Inspect project scripts before running them: a test or migration wrapper may deploy to its configured public cluster.

## Signing credentials

- Solana keypair JSON files are **plaintext secret keys**. A BIP39 passphrase supplied to `solana-keygen` protects mnemonic recovery, not the saved JSON. `.gitignore` or restrictive file permissions do not encrypt a wallet. Foundry Cast Wallet is not a Solana signing solution.
- For real developer, funding, and authority wallets, use an existing hardware wallet or controlled external signer with verified Ed25519/Solana support. Confirm that the exact CLI, transaction format, and signer role support it. Solana CLI hardware keypair URLs do not imply that every Anchor wallet provider or SDK accepts them. If necessary, build with Anchor and use a compatible deployment/signing path; do not export the key to make a tool work.
- Keep private keys, mnemonics, and unlock secrets out of chat, tracked files, `.env`, frontend bundles, command arguments, and captured output. Never run a wallet-generation tutorial that prints real recovery material into tool logs. Let the developer complete required secret entry in their own private interactive flow. CI should use the established external signing facility rather than a plaintext key file.
- Disposable local-validator test signers may use ephemeral keypairs confined to the test environment. Never reuse them as public-network funding or authority wallets. Build-generated `*-keypair.json` files also contain signing material: isolate local artifacts, exclude them from distributable bundles, and plan public program-address creation separately from funding and upgrade control.
- When the required signer is unavailable, finish artifacts, tests, configuration, and the release procedure; mark only the signing-dependent step pending.

## Execute within the authorized scope

Local deployment and simulation are development checks. Public deployment, initialization, upgrades, authority transfer, and making a program immutable must fit the user's authorized cluster and operations. Reuse existing explicit authorization. If it is absent, finish reviewable preparation before asking only about the remaining public action. Devnet authorization does not include mainnet.

For local integration, use an isolated validator, deploy/load the compiled program, initialize its required accounts, and exercise the affected client flow. A validator reset invalidates prior account state; rediscover and initialize it deliberately. A local validator containing copied public accounts still does not broadcast to the public network.

For an authorized public release:

1. Verify the selected cluster, public signer addresses, existing program/loader state, authority, and expected artifact. Review upgrade effects on existing accounts and clients before replacing code.
2. Simulate the relevant instructions against suitable state. A loader deployment is a sequence of transactions; an application simulation is not proof that this entire release will succeed. Resolve simulation failures rather than disabling preflight by default.
3. Execute the established deployment procedure and track its component transactions and buffers. Confirm execution without error at the required commitment; RPC acceptance or a returned signature is only submission evidence.
4. Fetch the actual deployed program and loader metadata, expected upgrade authority, and initialized application state. Verify the client can decode and use that deployment with the intended IDL.

## Recover without duplicating operations

- On timeout or transport failure, query known signatures and actual program/application state before another broadcast. A null status may require transaction-history lookup or a healthy RPC on the same cluster; it does not prove rejection.
- While a recent-blockhash transaction remains valid, rebroadcasting the same signed bytes retains its identity. A new blockhash requires new signatures and creates a distinct transaction. Establish expiry using its recorded `lastValidBlockHeight` and current block height, then reconcile whether the original already executed before reconstructing a business action. Wall-clock timeout alone is insufficient.
- Durable-nonce transactions have a different lifetime: inspect the nonce account and whether its value was consumed. Do not apply recent-blockhash expiry logic or blindly advance a nonce to recover them.
- For partial deployment or initialization, resume only missing steps based on observed state. Identify buffer ownership and contents before reuse or cleanup. Do not close programs/buffers, reclaim balances, or transfer authority as an incidental retry.

## Verification and handover

- For source verification, use the project's reproducible build method, such as a supported `anchor build --verifiable` or `solana-verify` workflow. Pin the build environment and compare the built executable with the deployed program on the correct cluster. Record the actual verification result; source matching is not a security audit.
- Keep IDL/client generation, optional onchain IDL publication, and executable verification distinct. Check the installed Anchor version's metadata mechanism and authority requirements. Publishing an IDL does not prove that it describes the deployed code. Do not publish private source or metadata unless that is part of the release scope.
- Confirm an intended multisig/governance recipient can exercise the required authority before handover, then fetch onchain state to verify the transfer. Do not add a multisig to an unrelated fix. Removing upgrade authority is irreversible for the applicable loader; treat immutability and closure as explicit operations, never routine cleanup.
- Deliver the cluster/genesis identity, program ID, source/build identifier, artifact and IDL provenance, public authorities, transaction signatures, confirmed execution status, deployment slot, and verification status as applicable. Preserve existing manifest formats and update the DApp's cluster mapping. Distinguish compilation, simulation, submission, execution, and source verification in the report.

## Official references

- [Solana program deployment](https://solana.com/docs/programs/deploying): loader metadata, program identity, upgrades, and immutable programs.
- [Anchor CLI](https://www.anchor-lang.com/docs/references/cli) and [Anchor.toml](https://www.anchor-lang.com/docs/references/anchor-toml): version-specific build, cluster, program, and client configuration.
- [Anza filesystem wallets](https://docs.anza.xyz/cli/wallets/file-system) and [hardware wallets](https://docs.anza.xyz/cli/wallets/hardware): plaintext keypair behavior and supported signer URLs.
- [sendTransaction](https://solana.com/docs/rpc/http/sendtransaction), [confirmation and expiry](https://solana.com/developers/cookbook/transactions/confirmation), and [durable nonces](https://docs.anza.xyz/cli/examples/durable-nonce): submission, lifetime, and recovery semantics.
- [Anchor verifiable builds](https://www.anchor-lang.com/docs/references/verifiable-builds) and [Solana verified builds](https://solana.com/docs/programs/verified-builds): reproducibility and deployed executable checks.
