# Fortis Container — documentation hub

> This repository is the cross-project documentation and evidence map. It is not a Docker deployment repository or an execution runbook. Use this README as the entry point, topic documents as technical sources of truth, and Future Improvements as the single living plan.

## Start here

| First question | Read |
|---|---|
| What work is planned next? | [Future improvements](docs/FUTURE-IMPROVEMENTS.md) |
| Which document should I read for a task? | [Full documentation map](docs/README.md) |
| What exactly did the latest Repo1/Repo2 GO3 dry verification prove? | [GO3 Guard baseline audit](docs/audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md) |

## Choose a route

| Task | Primary document |
|---|---|
| Understand components and trust boundaries | [Architecture](docs/ARCHITECTURE.md) |
| Understand live container storage and mounts | [Containers and volumes](docs/CONTAINERS-AND-VOLUMES.md) |
| Connect Fortis Repo to Observatory API (candidate) | [Scoped Repo API client](tools/observatory-api/README.md) |
| Understand ordinary project clones, Worktrees and Docker → GitHub → Windows handoff | [Canonical Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md) |
| Trace the Dockerfile, image and build evidence | [Container build provenance](docs/CONTAINER-BUILD-PROVENANCE.md) |
| Correct Desktop Commander Docker path guidance | [Patch and deployment status](patches/desktop-commander-0.2.52/README.md) |
| Suppress Desktop Commander MCP UI in the shared Repo container | [Deployment and verification record](patches/desktop-commander-0.2.52-mcp-ui-headless/README.md) |
| Understand ChatGPT and Qwen routes, the 26-tool catalog and capability boundaries | [AI integrations](docs/AI-INTEGRATIONS.md) |
| Understand machine auth and owner approval | [Authorization and approvals](docs/AUTHORIZATION-AND-APPROVALS.md) |
| Use Fortis Approvals as the authenticated-service Gateway; add a service and define ALLOW / ASK / DENY | [Gateway agent guide](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md) |
| Find canonical source ownership | [Source map](docs/SOURCE-MAP.md) |
| Work safely with Git or recover state | [Git and recovery](docs/GIT-AND-RECOVERY.md) |
| See planned work, including approved Gateway naming and rename gates | [Future improvements](docs/FUTURE-IMPROVEMENTS.md) |
| Choose proportionate checks | [Validation policy](docs/VALIDATION-POLICY.md) |

## Authority and DRY

- [Future improvements](docs/FUTURE-IMPROVEMENTS.md) is the sole living plan; completed items link to evidence and planned items remain unauthorized until separately approved.
- Topic documents own their detailed explanations. The [documentation map](docs/README.md) explains this division.
- [AI integrations](docs/AI-INTEGRATIONS.md) owns the cross-client Desktop Commander catalog and capability boundaries; the Qwen Workfiles README owns only Qwen transport details and retained artifact status.
- The Fortis Approvals repository owns the Gateway's AI-agent instructions, service-integration procedure and operation-policy model. This hub owns the cross-project container/credential boundary snapshot and links to that guide rather than duplicating its checklist.
- The Mirror repository owns the ordinary project `Repos` / `Worktrees` convention and Docker → GitHub → Windows workflow; this repository owns container topology, credentials and recovery evidence, and links rather than duplicating that workflow.
- Dated audits own the evidence and limitations for a particular verification. Other documents should summarize and link rather than copy full evidence.

When statements conflict, use the exact-target live evidence first, then current source/manifests, then explicitly labelled owner-reported state. Historical and candidate records do not override deployed state.

## Dry-run and safety boundary

The GO3 Guard Preview is a read-only preflight, not a tunnel-start or reconnect test. The target-name Compose candidate is render-only; its location, approved mapping and migration gates are recorded in [Future improvements — section B](docs/FUTURE-IMPROVEMENTS.md#fortis-approvals-gateway-resource-naming-and-migration-planned). Do not run Docker lifecycle commands (up, create, start, down), replace containers, copy volumes, edit Windows profiles, change credentials or repair runtime configuration as part of documentation or dry verification. Any such action requires separate review and explicit owner authorization.

Follow [Validation policy](docs/VALIDATION-POLICY.md) for the boundary between automated static checks and manual owner verification. Follow [Source map](docs/SOURCE-MAP.md) for implementation ownership; this repository does not replace the Tunnel, Script Control Center, RDG or Fortis Approvals source repositories.
