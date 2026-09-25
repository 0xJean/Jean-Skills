# Wallet Authentication and Sessions

Use only when the task requires sign-in, private data, or a backend user identity. Preserve the existing authentication framework, session store, and deployment model; integrating RainbowKit does not require migrating NextAuth/Auth.js or adopting a particular version.

## Separate Connection, Authentication, and Authorization

- A wallet connection provides account and network state; it does not prove that the requester has authenticated with the backend. Address parameters, connection state, and client caches cannot establish a session.
- Public onchain reads and ordinary wallet interactions do not require sign-in by default. Add Sign-In with Ethereum (SIWE / ERC-4361) only when a backend identity is needed.
- SIWE proves control of an address. It does not authorize access to API resources, roles, or business actions; every protected endpoint must still enforce permissions on the server.
- Sign-in signatures, token approve/permit, transaction signatures, and EIP-7702 delegation authorizations are separate actions. Sign-in must not require asset approvals, account deployment, or onchain broadcasts.
- Reuse existing authentication endpoints and sessions rather than creating a conflicting wallet user system. Model the relationship between addresses and chains explicitly for the business.

## Issue and Verify Challenges on the Server

1. Generate a high-entropy random nonce that satisfies the SIWE format. Store a short-lived challenge and its expiry, bound to the browser's pre-authentication session or equivalent sign-in context.
2. Derive allowed scheme/domain, URI, and chain ID values from trusted application configuration. A challenge may also bind the target address, purpose, and server issuance time. Behind a proxy, do not trust arbitrary Host or forwarded headers as the expected domain.
3. Construct and parse SIWE messages with a standard library. The client may assemble the message, but the server must independently check expected challenge fields rather than treating submitted values as expected values.
4. Validate the message format, version, address, domain, URI, chain ID, nonce, issued-at, and applicable expiration-time / not-before restrictions. The server-side challenge TTL also applies.
5. Verify the exact received message bytes and signature. Do not translate, trim, or reconstruct the message before verification. Verify the account signature using the verifier on the challenge's chain.
6. After successful signature verification, consume the challenge atomically. Only the request that successfully consumes it may establish a session. Return the server session result; the client must not equate signing completion with successful sign-in.

- Bind the nonce to the sign-in context and expected request. Checking only that a random string exists in the database allows challenges to be reused across different sign-in flows.
- Use the server clock for time checks. Define bounded clock skew and maximum message age; reject expired, not-yet-valid, or unreasonably future-dated messages even when their signatures are valid.
- Use a conditional update, unique constraint, or atomic storage operation that requires the challenge to remain unused and unexpired. At most one concurrent submission of the same signature may succeed.
- Checking that a nonce is unused, creating a session, then deleting the nonce is not atomic. Commit consumption and session creation in one storage transaction where possible; across stores, fail closed and never restore a consumed nonce after a later failure.
- Keep RPC signature verification outside short database transactions. Recheck TTL, sign-in context, and challenge state when committing consumption; do not hold database locks while waiting for RPC.
- Bound request sizes, request rates, and challenge lifetimes. Distinguish malformed input, invalid signatures, consumed challenges, and temporary verification-service failures; avoid unlimited retries.

## EOAs, Contract Wallets, and Smart Accounts

- Use a SIWE verifier or viem Public Client verification method supported by the installed version. Check whether it validates both SIWE fields and the signature; implement any missing checks on the server.
- `publicClient.verifyMessage` handles the account signatures supported by that version. Do not replace contract-wallet verification with the EOA-only utility of the same name or plain `ecrecover`.
- For ERC-1271 contract wallets, verify the address on the chain specified by the SIWE chain ID. Do not substitute a contract at the same address on another chain or use the owner address as the session principal.
- Follow the verification library's applicable verification paths. Do not establish a session if an RPC failure prevents verification, the signature is ultimately invalid, or the format is unsupported. Distinguish service failures from invalid signatures; do not add a fallback that bypasses verification.
- EIP-7702 allows EOAs to have delegated code. Do not permanently classify accounts or select verification paths solely by whether an address has code. Account for the wallet's signature format, target chain, and actual verifier capabilities.
- When undeployed accounts or signatures for delegations not yet onchain are required, check actual library support and applicable states for formats such as ERC-6492 and ERC-8010. Do not assume every viem version or every 7702 wallet is compatible.
- Sign-in verification performs only reads or verification simulations. Do not deploy accounts, submit delegations, or export private keys to make a signature pass. State account/format limitations when support is missing, while preserving supported paths.
- Contract-wallet signature validity can change with the owner, threshold, or delegated implementation. Choose session lifetimes, reauthentication for sensitive actions, or invalidation on relevant state changes according to permission risk; one successful verification is not permanent proof of control.

## Sessions, Cookies, and Request Protection

- Derive the session principal from the verified message address. Retain necessary context such as the verification chain, authentication time, and expiry. Do not bind identity to a mutable ENS name or trust a replacement user ID in a request.
- Rotate the anonymous session identifier on successful sign-in. Enforce expiration, revocation, and permissions on the server. A signature is sign-in evidence, not a long-lived bearer token replayed with every API request.
- Use `HttpOnly` for browser session cookies, and HTTPS with `Secure` in production. Explicitly choose an appropriate `SameSite` policy and narrowly scoped domain. Keep session credentials out of URLs, logs, and persistent frontend storage.
- For cookie-authenticated sign-in verification, sign-out, and business write endpoints, use the framework's CSRF protection and validate trusted Origins. SameSite is defense in depth; a SIWE nonce is not automatically complete CSRF protection.
- For cross-origin frontend/backend deployments, define trusted origins, credential transmission, and cookie policy explicitly. Do not fix sign-in failures by reflecting arbitrary origins or using permissive CORS.
- Explicit sign-out must revoke the server session and clear its cookie, while the client clears private queries and identity state. Disconnecting the wallet or clearing local state alone does not invalidate the server session.
- When signing out or replacing the sign-in context, invalidate its challenges and issued sessions on the server. Check the context version atomically when consuming a challenge so an in-flight sign-in response cannot re-establish a valid session after sign-out.
- If the existing system uses stateless sessions, explain how sign-out and revocation take effect. Do not claim that clearing a browser cookie revokes all previously issued credentials.
- Authentication logs should record outcomes, error categories, and necessary correlation information, not reusable session tokens, complete sign-in signatures, or cookies.

## RainbowKit and UI Consistency

- Use authentication integration or a custom adapter supported by the installed version. Reuse existing backend nonce, verify, session, and sign-out capabilities; the session framework and version used in documentation examples are not mandatory choices.
- Manage connection state separately from authentication state. RainbowKit's loading / authenticated / unauthenticated status must come from the server session query, not directly from wagmi's connected state.
- After an account switch, the new wallet must not inherit the previous session principal's private data or action permissions. Follow product policy: sign out and authenticate again, or clearly identify the retained session principal and prevent accidental use under the wrong identity.
- After a chain switch, check the session's chain constraints. A contract wallet at the same address on another chain is not automatically authenticated. Whether a chain-independent EOA session remains valid follows the established policy; do not unconditionally prompt for another signature.
- If the account changes, the user signs out, or the challenge is replaced while a signature is pending, discard stale frontend request results. A late success response must not restore a signed-out identity.
- Recheck the session after page refreshes and when restoring multiple tabs. On sign-out or expiry, clear private caches selectively; public onchain caches need not all be cleared.
- After rejection or session expiry, allow a new challenge without repeatedly opening the wallet. Use the site's i18n for sign-in prompts and errors; translating the UI must not alter signed message bytes.

## Key Checks and Delivery

Run the relevant checks below for the account types and authentication flows actually supported. Generating adapter configuration alone is not completion.

| Scenario | Expected result |
| --- | --- |
| Wallet connection or public balance read only | No authenticated session is created; public reads remain available |
| Normal sign-in and tampered fields | The valid path succeeds; incorrect domain, URI, chain, nonce, address, signature, or time constraints are rejected |
| Concurrent replay of one challenge | At most one session is established; expired or consumed challenges cannot be reused |
| EOA and target smart accounts | Supported ERC-1271, 7702, and other paths work; wrong chains, invalid results, and RPC failures do not bypass verification |
| Account/chain switches and late responses | Old identity permissions, private caches, and signature results do not leak into the new context; session restoration follows the defined policy |
| Sign-out, expiry, and CSRF | The server session and access to private endpoints expire together; cross-site writes are rejected |
| Authenticated user without business permission | SIWE sign-in does not grant access to another user's resources or bypass role and onchain permissions |

Report supported account types, verification chains, challenge/session storage, expiration and revocation policy, and actual test results. List unverified smart-account formats separately rather than claiming support for all wallets.

## Official References (Check Against Installed Versions)

- [ERC-4361: SIWE](https://eips.ethereum.org/EIPS/eip-4361): message format, domain/time binding, onchain signature verification, and session principals.
- [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271): contract-account signature verification and state-dependent validity.
- [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): how delegated code affects assumptions about account types.
- [viem Public Client verifyMessage](https://viem.sh/docs/actions/public/verifyMessage): differences from the EOA-only utility and currently supported signature formats.
- [RainbowKit Custom Authentication](https://rainbowkit.com/docs/custom-authentication): connecting the authentication adapter to server session state.
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): cookies, session rotation, expiry, and revocation.
