# Backend, Indexing, and Process Operations

Add a backend only when the task needs APIs, persistence, event indexing, or background jobs. For new projects, default to TypeScript + Node.js + Prisma + viem. Preserve the existing database, HTTP framework, and deployment approach; do not add a service to a simple DApp without a need.

## Structure and Versions

- Read existing run scripts, the Node.js version, lockfiles, database models, and deployment configuration to choose compatible stable releases. Prisma client, migration, and connection configuration can change between major versions; follow the project version and local CLI.
- Separate API, chain reads, database access, and background job responsibilities. Small projects can share one codebase; do not assume they need microservices, message queues, or distributed components.
- Configure chain ID, RPC, contract addresses, and database per environment. Validate required configuration and the RPC's actual chain at startup. Never log connection strings containing credentials.
- Validate API inputs for addresses, chains, amounts, pagination, and business permissions. Database business records do not replace contract permissions or onchain transaction results.
- When wallet login is needed, implement server challenges, signature verification, and sessions using [wallet authentication](authentication.md). Do not trust a wallet address merely asserted in a request body, or add login by default for public chain reads.

## Prisma and Data Precision

- Keep database models and migrations in version control. Generate and review migrations in development, then apply committed migrations during deployment; do not let every API worker race to run migrations at startup.
- Check the local version for the exact client generation and migration commands. Do not apply development resets, direct schema synchronization, or unreviewed data deletion to existing production data.
- For existing data, assess non-null columns, unique constraints, and backfill effects. Keep old and new application versions temporarily compatible during staged changes, and verify migration results in an authorized environment.
- Reuse the database client and connection pool within each long-running process; do not create or disconnect them per request. Include PM2 instances, indexers, and migration jobs in the total connection budget. Check pool options against the installed Prisma adapter.
- Keep database transactions short. Fetch and validate RPC data outside the transaction, then atomically commit related data and progress. Do not hold database locks while waiting for an uncertain network response.
- Represent onchain integers as `bigint` in JavaScript and agreed decimal strings in APIs; never convert them to `number` before storage. Define JSON serialization and deserialization rules.
- Database columns mapped from Prisma `BigInt` are typically 64-bit integers and cannot hold the full `uint256` range. Check the actual range of the selected database and connector.
- Store full `uint256` values in an exact numeric column with sufficient precision and zero fractional digits, such as PostgreSQL `numeric(78,0)`, or as validated canonical decimal strings. Also enforce the range from `0` to `2^256 - 1`.
- Do not assume the default Decimal precision is sufficient or apply `numeric(78,0)` unchanged to every database. Text storage needs explicit numeric sorting and aggregation; check the client representation of exact numeric values against the Prisma version.
- Store amounts in base units and handle token decimals and display conversion separately. Include chain ID in multichain data and contract addresses in asset identities; use a consistent canonical form for address comparisons.

## viem Reads and Onchain Results

- Configure `createPublicClient` with the target chain and transport, then use `publicClient` to read blocks, contracts, logs, and receipts. Read services do not need a signing account by default.
- When several reads require one snapshot, bind them to the same block number or an available block identifier. Record the chain and block with cached data and communicate its freshness to consumers.
- Database balances, order statuses, and event views are indexed results. The canonical chain state under the chosen confirmation policy remains authoritative. A transaction hash reported by a client cannot directly mark a business operation successful.
- Verify receipt status, target contract, relevant events, and business parameters. Distinguish pending, confirmed, failed, and reorg-invalidated results; see [DApp integration](dapp.md) for the transaction lifecycle.
- Set reasonable RPC timeouts, concurrency limits, and bounded retries. Failed reads can retry with backoff; after a broadcast timeout, check the transaction hash and nonce before taking further action instead of blindly resubmitting.
- Separate L2 execution, business crediting, and finality using the [chain confirmation policy](deployment.md#chain-confirmation-fees-and-availability). For smart account operations, check the [operation's own result](smart-accounts.md); success of the bundler's outer transaction alone cannot justify crediting.

## Event Indexing When Needed

- Define the starting block, contracts, and event scope. Backfill history with chunked `getLogs` requests; use subscriptions or `watchContractEvent` for timely change detection. After reconnecting, recover missing logs from the persisted cursor.
- The cursor must identify at least the indexing job, chain, last fully processed block number, and block hash. Record each event's block number, block hash, transaction hash, and log index.
- Give raw logs an idempotent composite unique key, such as `chainId + blockHash + logIndex`. Insert events, update derived state, and advance the cursor in one transaction. Repeated reads must not credit balances or grant benefits twice.
- Use a confirmation depth or RPC-supported safe/finalized tags appropriate to the target chain. Label unconfirmed data if it is displayed early. Confirmation depth is not a universal constant across chains.
- Rescan an overlapping range and compare recorded block hashes or parent links. On a reorg, roll back to the common ancestor, undo or rebuild affected derived state, then replay canonical chain events.
- Retain reversible processing records or define how to rebuild from a confirmed checkpoint. Deleting raw logs alone must not leave behind their balance, order, or other effects.
- If a reorg exceeds retained history, stop advancing, surface the specific error, and recover through the defined rebuild procedure. Do not keep serving incorrect state that appears current.
- Default to one indexing worker in the first version. Add coordination, such as database leases, only when multiple instances are needed. Overlapping instances during PM2 cluster operation or reload must not process the same job concurrently.

## Signing and Background Onchain Writes

- Server-side signing is not a default backend capability. Add it only when the business explicitly needs automated onchain writes and the task covers those operations.
- Manage development wallets as encrypted keystores with `cast`, following [deployment and signing](deployment.md). Do not put development private keys, seed phrases, or keystore passwords in `.env`, PM2 configuration, code, or logs.
- For noninteractive services, prefer the project's existing external signing service or controlled signing mechanism. If a keystore cannot be unlocked interactively, complete reads, simulation, and deployment preparation first; do not export a plaintext private key to solve a startup problem.
- Persist business idempotency identifiers and transaction records for write jobs; recover existing transaction state before resuming after a restart. Manage each signing account's nonce through one writer or an explicit coordination mechanism, never independently in each cluster instance.

## PM2 and Recovery

For new Node.js services deployed on long-running VMs or hosts, default to PM2. Preserve existing container orchestration, managed platforms, or process supervisors so two layers do not both restart the same process.

- Commit an ecosystem configuration suited to the project's module format, specifying the entry point, working directory, instance count, and environment. Run built artifacts in production instead of development watch or interactive commands.
- Configure automatic restarts with delay or exponential backoff, such as `exp_backoff_restart_delay`, to avoid restart storms during database or RPC failures. Adjust thresholds to actual resources and workloads.
- API and indexer services can be separate processes. Before scaling APIs, confirm they do not depend on process-local sessions. Default indexers, scheduled jobs, and signing workers to one instance, and handle instance overlap during deployments.
- Provide health checks: liveness reflects process responsiveness, while readiness reflects dependencies the service needs. Indexing services also expose the last processed block, synchronization lag, and latest error. `pm2 online` does not prove business health.
- When using `wait_ready`, send the ready signal only after required dependencies and listening ports are ready. Match timeouts to the actual startup process so one brief RPC failure does not cause endless restarts.
- Handle `SIGINT` and `SIGTERM`: stop accepting requests and jobs, cancel subscriptions, let in-flight operations finish or roll back, then close database connections and listening ports. Bound shutdown time and give PM2's `kill_timeout` enough time for cleanup.
- Log errors with timestamps and job identifiers, and configure rotation, size limits, or retention. Use existing system rotation or `pm2-logrotate` to keep logs from filling the disk.
- Within the already authorized deployment scope, configure `pm2 startup`, verify the generated command's runtime user and Node.js path, and save the intended process list with `pm2 save`. After upgrading Node.js, check that the startup script still points to the correct version.
- At release, check processes, health endpoints, logs, and recovery procedures. Verify recovery after an unexpected exit and cursor resumption in an appropriate test environment. Rebooting hosts or interrupting production processes is not a default acceptance step.

PM2 can restart an exited process; RPC, database, network, and host failures still require timeouts, reconnection, and health checks. Match recovery measures to the task's scale. Do not describe PM2 as a high-availability guarantee or assume a complex distributed architecture is required.

## Delivery Checks

As relevant to the change, verify API input validation and permissions, round-tripping maximum amounts, migration results, duplicate event handling, and restart resumption. Cover rollback and replay when changing reorg handling. Report run entry points, migration and recovery steps, and actual verification results; generating a PM2 configuration alone does not verify stable service operation.

## Official References by Project Version

- [Node.js Signal Events](https://nodejs.org/api/process.html#signal-events): shutdown signals and behavior after registering handlers.
- [Prisma Connection Management](https://docs.prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections/connection-management) / [Migration workflows](https://www.prisma.io/docs/orm/migrations/how-migrations-work): connection reuse and migration commands across major versions.
- [Prisma PostgreSQL type mappings](https://docs.prisma.io/docs/orm/core-concepts/supported-databases/postgresql): column ranges and precision; consult the corresponding connector for other databases.
- [viem Public Client](https://viem.sh/docs/clients/public) / [watchContractEvent](https://viem.sh/docs/contract/watchContractEvent): public reads and subscription APIs.
- [PM2 Restart Strategies](https://pm2.keymetrics.io/docs/usage/restart-strategies/) / [Graceful Start/Shutdown](https://pm2.keymetrics.io/docs/usage/signals-clean-restart/): restart backoff, readiness, and shutdown time limits.
- [PM2 Startup](https://pm2.keymetrics.io/docs/usage/startup/) / [Log Management](https://pm2.keymetrics.io/docs/usage/log-management/): startup recovery and log rotation.
