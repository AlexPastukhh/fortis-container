# Documentation map

This directory is the central Fortis documentation set.

- [Architecture](ARCHITECTURE.md) — component relationships and trust boundaries.
- [Current state](CURRENT-STATE.md) — dated snapshot and known unknowns.
- [Containers and volumes](CONTAINERS-AND-VOLUMES.md) — storage and runtime resource map.
- [Container build provenance](CONTAINER-BUILD-PROVENANCE.md) — original Dockerfile, build log, image identity, source copies and unresolved rebuild inputs.
- [AI integrations](AI-INTEGRATIONS.md) — ChatGPT and Qwen routes and their actual status.
- [Authorization and approvals](AUTHORIZATION-AND-APPROVALS.md) — machine authentication, upstream credentials and owner decisions.
- [Source map](SOURCE-MAP.md) — canonical repositories, development copies, deployed copies and history.
- [Git and recovery](GIT-AND-RECOVERY.md) — current Git operation, credential handling and recovery.
- [Glossary](GLOSSARY.md) — stable component names.
- [Naming and rename plan](NAMING-AND-RENAME-PLAN.md) — owner-approved names, old→new mapping and pre-change requirements.
- [Future improvements](FUTURE-IMPROVEMENTS.md) — planned isolation, credential and Git improvements.
- [Validation policy](VALIDATION-POLICY.md) — lightweight automated checks versus manual Docker/Windows/WebAuthn/external-service verification.
- [Baseline audit](audits/BASELINE-2026-11-03.md) — evidence, commands and limitations.
- [Follow-up execution record](audits/FOLLOW-UP-2026-11-03.md) — Approval extraction, live mount recheck, Qwen proxy/tool-surface evidence, MCP description-source findings, container build-provenance follow-up and remaining gates.

## Documentation precedence

1. Fresh LIVE VERIFIED observations for the exact target.
2. Current source and deployment manifests, with their evidence limits.
3. Current-state documents with explicit OWNER-REPORTED labels.
4. Dated historical handoffs and archived candidate plans.

A newer document is not automatically more authoritative if it describes a candidate rather than the deployed runtime. Always check the evidence label and scope.
