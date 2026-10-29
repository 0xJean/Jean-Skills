# Backend, Authentication, and Indexing

Add a backend only for requested APIs, persistence, authentication, indexing, or jobs. For new services, prefer Node.js + TypeScript + Prisma and a compatible Solana SDK, normally `@solana/kit`. Preserve existing server frameworks, database choices, and legacy Solana clients when migration is not requested.

## Configuration and Data Precision

- Check Node, Prisma, database driver, SDK, and generated-client versions together. Configure RPC, cluster identity, program IDs, IDL/codecs, commitment, and database separately per environment. Validate configuration and RPC cluster identity at startup; hide credentials in logs.
- Keep read-only clients free of signing credentials. Validate address syntax, amounts, pagination, and business permissions at API boundaries. A request-supplied wallet address is not authentication; a supplied signature is not payment evidence.
- Represent chain amounts exactly using `bigint` or the client's equivalent. Serialize as canonical decimal strings. A Solana `u64` can exceed a database's signed 64-bit `BIGINT`: for PostgreSQL, `numeric(20,0)` can hold a `u64`, with an explicit `0..2^64-1` range check. Larger intermediate/account fields require their own range and precision. Check other connectors rather than assuming identical mappings.
- Preserve case in base58 addresses. Identify assets and accounts by cluster plus address, including token program where decoding or derivation depends on it. Store decimals separately from base-unit amounts.
- Version migrations, review changes against existing data, and apply them once per release. Reuse connection pools with a total budget across API and worker instances. Fetch RPC data outside short database transactions; atomically commit derived results and progress afterward.

## Wallet Authentication When Needed

- Wallet connection and public reads do not require a login session. When a session is needed, issue a fresh server-generated challenge containing the trusted domain/URI, intended account or binding policy, cluster if relevant, purpose, unpredictable single-use nonce, and issue/expiry times. Bind it to the requesting session; never trust a client-supplied replacement challenge.
- Feature-detect the wallet method. SIWS `solana:signIn` can use the matching `@solana/wallet-standard-util` verifier. For supported off-chain message signing or a raw `signMessage` fallback, use the correct format-specific decoder and verify the exact signed bytes. These envelopes and SIWS outputs are not interchangeable.
- Verify signature, public key/address correspondence, challenge fields, allowed origin/domain, time bounds, and intended signer on the server. Atomically consume the stored nonce only on success so concurrent replay cannot create multiple sessions. Signature validity alone does not enforce nonce consumption or application authorization.
- Use the verified output account as the session identity; a wallet can return a different account from an optional input hint. Enforce any pre-bound identity and require a new challenge when it changes. Clear or reauthenticate account-bound sessions after switching wallets.
- Use secure, HttpOnly cookies with an appropriate SameSite policy, CSRF protection for cookie-authenticated mutations, session expiry, and logout invalidation. Message authentication does not authorize transfers or automated signing. Do not silently substitute a transaction when message signing is unavailable.

## Chain Evidence and Indexing

- Before crediting a payment or completing an order, independently retrieve execution results and verify cluster, `meta.err`, required commitment, program/instruction, signer or payer as applicable, recipient, mint/token program, exact amount, and the order identifier. A memo, client callback, or event string alone is insufficient.
- Request only transaction versions the decoder actually supports, configuring `maxSupportedTransactionVersion` accordingly. Resolve loaded addresses for versioned transactions and inspect relevant inner instructions or verified account changes; do not assume one transaction contains only one transfer.
- Pick finality by effect. Use finalized records for irreversible off-chain settlement. If showing processed/confirmed data early, label it provisional and provide rollback/reconciliation before deriving irreversible effects.
- For scoped history, paginate `getSignaturesForAddress` and fetch transaction details. It returns newest first: collect/reorder a bounded range before applying order-sensitive effects. Subscriptions provide timely hints; they do not replace persisted backfill and recovery. Confirm the provider retains the required history.
- Persist cluster, scope, last fully processed signature/slot, and finality checkpoint. A slot alone is not a unique transaction cursor. Record transaction signature and a stable instruction/event position for each effect; use a composite unique key such as cluster + signature + instruction path + event ordinal, with documented decoder semantics.
- In one database transaction, insert deduplicated evidence, update business state, and advance progress. Repeated backfill, duplicate notifications, or process restarts must not credit twice. Keep the operation-level idempotency key as well: a replacement transaction has a different signature.
- Recover gaps by replaying an overlap from the persisted checkpoint and reconciling provisional records against canonical finalized evidence. If rollback affects derived balances, reverse or rebuild those effects. On missing/pruned history or unsupported decoding, stop cursor advancement and expose the gap instead of silently declaring synchronization complete.
- Do not treat arbitrary logs as authenticated Anchor events. Decode with the correct program IDL and execution context; failed transactions can emit logs, and provider logs may be truncated. Use transaction/account evidence or a suitable indexed feed when log-only history cannot satisfy completeness.
- Use bounded RPC retries, timeouts, pagination, and concurrency. Record commitment and context slot with cached reads; `minContextSlot` is a freshness floor, not a request for an exact historical snapshot.

## Signing Workers and Recovery

- Add a server signer only when automated writes are in scope. Use the approved external signer or protected signing mechanism from [deployment](deployment.md); do not solve unattended startup by placing a seed/private key in `.env`, Prisma, source files, PM2 configuration, or logs.
- Persist job identity, business idempotency key, expected effects, transaction signature, and lifetime before relying on retries. On restart, reconcile the existing attempt first, using the [DApp transaction rules](dapp.md#transaction-lifecycle). A timeout must not create a second independently executable payment.
- Solana ordinary transactions do not use an EVM-style sequential sender nonce. Coordinate competing business jobs and shared writable accounts; durable nonce accounts, if used, need separate serialization and nonce-state checks. Give indexers and signing workers one active owner or a proven lease/claim mechanism, including deployment overlap.

## PM2 on Persistent Hosts

- Prefer PM2 for new Node services on long-running hosts. Preserve a managed platform's or container orchestrator's existing supervisor. PM2 restarts a process; it cannot guarantee RPC, database, network, or host availability.
- Run built artifacts with a committed ecosystem configuration, explicit working directory, bounded restart backoff, readiness checks, and log retention. Treat API, indexer, and signer instance counts separately; increasing API workers must not duplicate jobs.
- Handle `SIGINT`/`SIGTERM`: stop accepting work, release subscriptions, finish or roll back bounded in-flight tasks, save recoverable progress, and close database connections. Set `kill_timeout` accordingly; send a `wait_ready` ready signal only when required dependencies are usable.
- Within authorized deployment scope, configure startup recovery and save the intended process list. Check the runtime user and Node path after upgrades. Health endpoints should expose dependency failures and indexer lag; `online` alone is not proof that business processing works.

## Verification and Sources

Test the behaviors touched: maximum integer round trips, challenge replay/expiry/wrong origin, forged payment claims, duplicate indexing, missing-history handling, partial progress, and restart recovery. Test rollback when provisional processing is changed. Report actual results and recovery entry points without claiming production resilience from configuration alone.

- [Solana message authentication](https://solana.com/docs/frontend/messages-and-auth) and [SIWS specification and verifier](https://github.com/phantom/sign-in-with-solana): signing formats and server verification.
- [Transaction lookup](https://solana.com/docs/rpc/http/gettransaction), [address history](https://solana.com/docs/rpc/http/getsignaturesforaddress), and [log subscriptions](https://solana.com/docs/rpc/websocket/logssubscribe): indexing primitives and limitations.
- [Production confirmation policy](https://solana.com/docs/tools/production-readiness): provisional versus finalized effects.
- [Prisma PostgreSQL types](https://www.prisma.io/docs/orm/overview/databases/postgresql) and [PM2 graceful start/shutdown](https://pm2.keymetrics.io/docs/usage/signals-clean-restart/): version-specific persistence and process behavior.
