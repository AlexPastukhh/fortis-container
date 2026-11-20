# Documentation map

Начать с короткого входа [главного реестра](use-cases/README.md) и полностью
прочитать UC-CONT-002/003 и [UC-GW-009 — UNCERTAIN/Owner Portal](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009);
весь каталог не просматривать. Этот файл — карта
технических owners по выбранной задаче.

This is the topic index for the Fortis Container documentation set. The repository-root [README](../README.md) is the compact entry point; use this file when you need the full catalogue, a recommended reading path or the authority rules. [Future improvements](BACKLOG-IMPROVEMENTS.md) is the single living plan; dated snapshots and audits are historical evidence, not live dashboards.

## Reading paths

- **New to the system:** [Architecture](ARCHITECTURE.md) → [Source map](SOURCE-MAP.md) → relevant topic documents.
- **Qwen MCP setup:** [AI integrations](AI-INTEGRATIONS.md) for the shared tool catalog and boundaries → `/workspace/files/Qwen-Fortis-MCP/README.md` for the Qwen-specific Windows transport and retained legacy artifacts.
- **Container/runtime work:** [Containers and volumes](CONTAINERS-AND-VOLUMES.md) → [Container build provenance](CONTAINER-BUILD-PROVENANCE.md) → [Validation policy](VALIDATION-POLICY.md).
- **Authenticated external-service request or new integration:** [Fortis Approvals Gateway agent guide](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md) → this repository's [authorization boundary](AUTHORIZATION-AND-APPROVALS.md) for current runtime boundaries and owner approval.
- **Repo1/Repo2 Guard or GO3:** [GO3 Guard baseline audit](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md) → canonical Tunnel and Script Center runbooks linked from [Source map](SOURCE-MAP.md).
- **Proposed change or rename:** [Future improvements](BACKLOG-IMPROVEMENTS.md) → the relevant priority section → [Validation policy](VALIDATION-POLICY.md). A plan is not authorization to execute.
- **Git or recovery:** [Git and recovery](GIT-AND-RECOVERY.md) → [Source map](SOURCE-MAP.md) → the owning repository's runbook.
- **Ordinary application repo / Worktree handoff:** [Canonical Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md) → this repository's [Git and recovery](GIT-AND-RECOVERY.md) only for credential and recovery details.

## Topic index

### System and current runtime

- [Architecture](ARCHITECTURE.md) — components, request paths and trust boundaries.
- [Containers and volumes](CONTAINERS-AND-VOLUMES.md) — runtime topology, storage, mounts, networks and persistence.
- [Container build provenance](CONTAINER-BUILD-PROVENANCE.md) — original Dockerfile/build evidence, image identity, historical source copies and unresolved reproducibility inputs.
- [Desktop Commander path-guidance patch and deployment record](../patches/desktop-commander-0.2.52/README.md) — source pin, patch scope, deployed image, rollback container and live Repo1/Repo2 description verification.
- [Desktop Commander MCP UI suppression deployment](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md) — G2 environment-switch precedent, deployed Docker patch/image, cutover result, live Repo2 runtime verification and owner-confirmed Repo1 reconnect; Qwen reconnect is not required for acceptance.

### Integrations and security

- [AI integrations](AI-INTEGRATIONS.md) — ChatGPT/Repo1/Repo2 and Qwen routes, the canonical 26-tool Desktop Commander catalog, capability boundaries and evidence limits.
- [Authorization and approvals](AUTHORIZATION-AND-APPROVALS.md) — current machine authentication, upstream credentials and owner approval as separate controls.
- [Fortis Approvals Gateway agent guide](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md) — canonical AI entry point for the Gateway's role, ALLOW / ASK / DENY semantics and the procedure for adding a credentialed service. The Fortis Approvals repository owns this guide.

### Source, operations and planning

- [Release planning contract v1](RELEASE-PLANNING-CONTRACT.md) — normative cross-repository build units, deployment targets and PR Release Impact. Current Publisher/CD Queue milestones live only in the [single roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue); the contract is not a deployment service.
- [Fortis Release Registry P5 — design candidate](RELEASE-REGISTRY-P5-DESIGN.md) — proposed durable storage, typed trust boundary, desired records, CAS, unknown/recovery and negative tests; owner decisions required, no live Registry API.
- [P5 component release restrictions](RELEASE-REGISTRY-P5-COMPONENT-RESTRICTIONS.md) — exception-only constraints on components/shared resources and operations; independent work is not automatically frozen, and no restriction is not a permission.
- [P5 durable component restriction candidate](RELEASE-REGISTRY-P5-DURABLE-CONSTRAINTS.md) — offline SQLite CAS, immutable events, loss-of-ACK receipts and backup; NOT a live release policy or Registry API.
- [P5 desired release preview candidate](RELEASE-REGISTRY-P5-DESIRED-PREVIEW.md) — deterministic offline target/environment plan from unverified claimed merge/CI/catalog evidence; no Registry ingestion.
- [P5 durable desired candidates](RELEASE-REGISTRY-P5-DESIRED-STORE.md) — offline idempotent SQLite journal, immutable desired lineage and supersession; no trusted ingest API or installed state.
- [P5 post-merge evidence readiness](RELEASE-REGISTRY-P5-POST-MERGE-EVIDENCE.md) — existing scoped Gateway READ gaps, fail-closed offline assessor and proposed owner-reviewed trusted collector contract.
- [Source map](SOURCE-MAP.md) — canonical source ownership, development copies, deployed copies and historical artifacts.
- [Git and recovery](GIT-AND-RECOVERY.md) — shared credential boundaries, dated repository-state snapshots and recovery practices; ordinary project Worktree layout and delivery flow are owned by Mirror.
- [Canonical Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md) — ordinary project primary clones, Worktrees, GitHub Actions checks and Docker → GitHub → Windows handoff.
- [Future improvements](BACKLOG-IMPROVEMENTS.md) — the sole living plan and prioritized backlog, including approved Gateway naming, proposed Docker mapping and migration gates; items remain planned unless separately approved.
- [Validation policy](VALIDATION-POLICY.md) — proportionate static checks versus manual host/runtime verification.
- [Glossary](GLOSSARY.md) — stable component names and terminology.

## Audit and evidence records

Audits preserve what was checked, the evidence supplied, limitations and decisions at a point in time. The archived `CURRENT-STATE-ARCHIVE-2026-11-04.md` and `NAMING-AND-RENAME-PLAN-ARCHIVE-2026-11-04.md` are retained as historical snapshots/decision records only; neither is an active status dashboard or plan. Audits and archives are not executable runbooks.

- [Repo1/Repo2 container and Shared Guard baseline — 2026-11-04](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md) — pre-cutover GO3 Windows owner-run output, base-image identity, Guard Preview results and corrected mount diagnostic; current deployment is linked separately above.
- [AI container isolation audit — 2026-11-04](audits/AI-CONTAINER-ISOLATION-2026-11-04.md) — read-only review of the shared execution context, workspace mounts, host/network reachability, command execution limits and the proposed brokered PowerShell/container-control design.
- [Desktop Commander MCP UI deployment verification — 2026-11-04](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md) — candidate and preflight evidence, successful production cutover, live Repo2 runtime acceptance and owner-confirmed Repo1 reconnect; Qwen reconnect is not required.
- [Follow-up execution record — 2026-11-03 onward](audits/FOLLOW-UP-2026-11-03.md) — chronological follow-up evidence, source investigations, Windows backup review and Approval Gateway functional revalidation.
- [Baseline audit — 2026-11-03](audits/BASELINE-2026-11-03.md) — initial inventory, source boundaries, test results and original limitations.

## DRY: document authority

| Question | Single source of truth | Other documents should… |
|---|---|---|
| What is the runtime topology and storage map? | [Containers and volumes](CONTAINERS-AND-VOLUMES.md) | Link rather than restate the full mount inventory. |
| How was the image built and where did it come from? | [Container build provenance](CONTAINER-BUILD-PROVENANCE.md) | Link rather than repeat source/hash history. |
| How should AI use the Gateway or add a credentialed service and operation policy? | [Fortis Approvals Gateway agent guide](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md) | Keep the integration procedure in Fortis Approvals; this hub links to it and owns only the container credential-boundary snapshot. |
| Who owns each implementation? | [Source map](SOURCE-MAP.md) | Link to the owning repository and its runbook. |
| What tools do ChatGPT and Qwen expose, and what are their shared capability boundaries? | [AI integrations](AI-INTEGRATIONS.md) | Keep the cross-client 26-tool catalog here; Qwen README owns only transport-specific details and legacy artifact status. |
| What is the ordinary project clone / Worktree and Windows handoff convention? | [Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md) | Link here; do not restate the process in Fortis Container docs. |
| What work is planned, including approved names and migration gates? | [Future improvements](BACKLOG-IMPROVEMENTS.md) | Keep the sole plan here; link to technical evidence rather than duplicating it. |
| What did a specific verification prove? | The corresponding dated audit | Keep evidence there; link to it rather than duplicating it. |
| How should a check be performed? | [Validation policy](VALIDATION-POLICY.md) plus the owning runbook | Do not create parallel test policies. |


## Evidence precedence and safety

1. Fresh evidence for the exact live target, with its execution context stated.
2. Current source, manifests and deployment configuration, within their stated scope.
3. Dated audits and deployment records, interpreted within their stated scope and evidence class.
4. Historical handoffs and candidate plans. A newer candidate is not more authoritative than an older deployed-state observation merely because its date is newer.

Keep **DRY documentation** and **dry-run execution** distinct. DRY documentation means one authoritative home for each fact or plan. A dry run means a non-mutating Preview/render only: it does not start a tunnel, reconnect a client, deploy an image, create resources or prove application health. For Docker, Windows, mounts, TLS, WebAuthn and external APIs, follow the manual owner-verification boundary in [Validation policy](VALIDATION-POLICY.md).
