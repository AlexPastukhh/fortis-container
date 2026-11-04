# Authorization and approvals

## Do not conflate these mechanisms

Fortis uses separate machine authentication, upstream API credentials and human approval. They answer different questions and do not replace one another.

| Mechanism | What it proves | Where it is used | AI visibility |
|---|---|---|---|
| Repo → Gateway machine grant | Authenticates the Fortis Repo client to the Gateway machine ingress | `/run/fortis-client/grant` | Readable by processes running as the file's UID in Repo |
| Gateway TLS identity | Lets the Repo client authenticate the Gateway server | Gateway: `/run/r7-identity`; Repo client receives public `server.crt` | Gateway private key stays in Gateway; public certificate is available to Repo |
| SonarCloud token | Authenticates Gateway to the upstream SonarCloud API | Gateway: `/run/r7-sonar-token/token` | Not mounted into Fortis Repo |
| Owner WebAuthn | Authenticates the human owner for an approval decision | Fortis Approvals Gateway Owner Portal | Not an AI credential or machine-ingress route |
| GitHub PAT | Authenticates Git operations against GitHub | `/workspace/repo/.fortis-auth/` | Available to same-UID programs in Fortis Repo; current security risk |

The paths and volume identifiers containing `r7` are existing implementation names. They are preserved here to identify the current mounts, not used as the service's human-readable name.

## Request matrix: machine authentication, upstream authorization and owner approval

| Operation | Repo → Gateway machine grant | Gateway → upstream Sonar token | Owner approval | Current behavior |
|---|---|---|---|---|
| Ordinary local Desktop Commander file/search/process work | Not involved | Not involved | Not involved | Governed by the connected MCP tool surface and Linux file/process permissions; it does not pass through the Approval Gateway. |
| Four typed Sonar READ operations | Required | Used inside Gateway | Not required (`ALLOW`) | Gateway performs allowlisted Sonar reads and returns a typed projection. |
| `sonarcloud.accept_issue` proposal | Required | Used inside Gateway to read and freeze the exact Issue preview; used again only after approval to perform the mutation | Required (`ASK` + owner WebAuthn) before mutation | AI can create a `PENDING` request and read its status; it cannot approve or execute it. |
| Owner Approve / Reject | Not exposed to the machine client | Gateway uses its own Sonar token only on the approved execution path; Reject does not dispatch the Sonar adapter | Owner session and WebAuthn required | Separate Owner Portal route; Core rechecks policy and the frozen request. |
| Owner-approved local/internal action with no upstream API | If it uses Gateway machine ingress, the machine grant is still required | Not applicable | Could be required by such an action's policy | No such operation is currently demonstrated or implemented. |

**Important distinction for the three cases discussed:**

1. **Authentication and approval both required:** the current `sonarcloud.accept_issue` mutation. Repo authenticates to Gateway with the machine grant; Gateway authenticates to SonarCloud with its private token; the owner separately approves with WebAuthn before the mutation.
2. **Authentication required, approval not required:** the current typed Sonar READ operations. The same machine grant and Gateway-held Sonar token are used, but policy returns `ALLOW`, so no owner approval is requested.
3. **Approval required, no upstream API token required:** this is a possible pattern for a future local/internal action, but it is not an implemented current operation. Even in that pattern, if the request enters through Gateway machine ingress, Repo-to-Gateway machine authentication is still required. “No upstream token” does not mean “no machine authentication.”

There is no unauthenticated route through the Gateway machine ingress. The ingress authenticates the machine grant before dispatching typed reads, actions or request-status reads. Owner WebAuthn is a separate human decision, not a substitute for machine authentication or upstream API authorization.

## 1. Repo machine authentication

The typed client in `fortis_approvals/repo_sonar_tools.py` reads:
- client grant: `/run/fortis-client/grant`;
- public server certificate: `/run/fortis-client/server.crt`;
- fixed endpoint: `https://host.docker.internal:19104`.

The client enforces TLS 1.3, uses a fixed host and fixed routes, and sends the grant as an Authorization Bearer credential. Its source explicitly states that the grant is not a SonarCloud credential. The grant file is checked as a regular, non-symlink file with mode 0600, owned by the current effective UID, and outside the workspace paths.

The Gateway machine ingress separately requires HTTPS, validates the Authorization header, authenticates the grant to an actor and applies a per-actor rate limit. It accepts only typed reads, typed actions and request-status reads; it does not expose owner routes or a generic HTTP proxy.

**LIVE VERIFIED in the current Repo container (metadata only; secret contents were not read):** `/run/fortis-client` is the `fortis-r7-client` ext4 volume mounted `ro`. It contains `grant` and `server.crt`. The grant is a regular file owned by UID 1000 with mode 0600; the public certificate is owned by UID 1000 with mode 0644. The current Desktop Commander process runs as UID 1000, so it can read the grant. Read-only mount semantics prevent writes; they do not prevent reads by the owning UID. This is not per-agent credential isolation.

## 2. Upstream Sonar authorization

The SonarCloud token is loaded by the Gateway server from `/run/r7-sonar-token/token`. The Gateway composes the machine ingress, Core, Owner Portal and Sonar adapters. The Repo client never receives the Sonar token.

The Sonar adapter pins official regional origins and a small route/parameter allowlist. It does not accept arbitrary URLs, HTTP methods or credentials from the AI request.

## 3. Approval is a separate owner decision

Current Gateway policy:
- Four typed Sonar READ operations are policy `ALLOW`; they do not require owner approval.
- `sonarcloud.accept_issue` is policy `ASK`; the machine actor can submit a proposal but cannot approve or execute it.
- The proposal creates a frozen `PENDING` request.
- The owner reviews the exact request in the Fortis Approvals Gateway Owner Portal and uses WebAuthn with user verification.
- On approval, Core rechecks the request/policy/grants, dispatches the single permitted Sonar transition, reads the issue back independently and records the result.
- Reject ends as `REJECTED` without adapter dispatch.

The 2026-11-03 live evidence records one actual Approve → `EXECUTED` → Sonar `ACCEPTED` readback and one Reject → `REJECTED` path. The evidence notes that no packet trace was captured for Reject; the no-dispatch conclusion follows the implementation contract and recorded state.

For the current `accept_issue` flow, owner approval does **not** replace upstream authorization: the machine grant authenticates Repo to Fortis Approvals Gateway, WebAuthn authorizes the human decision, and the Sonar token held by Gateway authenticates the upstream Sonar mutation. These are three distinct controls in one operation.

A different pattern — an owner-approved local/internal action that does not call an upstream API and therefore needs no upstream API token — is conceptually possible, but it is not demonstrated by the current live Sonar flow and is not documented as an implemented Gateway capability. Do not infer it from the existence of ASK alone.

This is not an automatic approval system. The AI cannot impersonate the owner, create an owner WebAuthn assertion or invoke the owner decision route.

## 4. GitHub authorization is separate

The GitHub PAT is not the Repo machine grant and is not the Sonar token. Current storage and residual legacy references are described in [Git and recovery](GIT-AND-RECOVERY.md).

The current shared credential file is stored in the persistent workspace, outside Git checkout directories, but same-UID processes can read it. File mode 0600 and directory mode 0700 protect against other local users; they do not isolate one AI process from another process running as UID 1000.

## 5. Future security work

Place credential isolation directly beside tool isolation in the future roadmap:
- per-agent machine identities and scopes;
- a broker for GitHub operations rather than a PAT in the shared workspace;
- no direct token reads by general-purpose AI processes;
- approval gates for privileged Git actions where appropriate;
- separate tool capability profiles and OS-level boundaries.

See [Future improvements](FUTURE-IMPROVEMENTS.md).
