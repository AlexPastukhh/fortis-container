# Historical future-improvements snapshot — 2026-11-05

**Status:** HISTORICAL / SUPERSEDED. Active work is owned only by [BACKLOG-IMPROVEMENTS](BACKLOG-IMPROVEMENTS.md). The following text preserves earlier observations, not current instructions.

**Original status:** ACTIVE BACKLOG. Completed items are retained as milestones and link to evidence. Planned items are not authorized for implementation merely by being listed here.

## Priority group A — tool isolation, credentials and Git

These three topics belong next to each other because they share the same trust boundary.

**Execution status:** this is the sole living plan and records both planned work and accepted completions. Supporting evidence belongs in dated audits and topic-specific deployment records; no separate current-state dashboard is maintained. Before acting on any runtime or Git state, inspect the exact live target rather than relying on a dated snapshot. The detailed GO3 evidence, including the mount-diagnostic caveat, is maintained in the [Repo1/Repo2 Guard baseline audit](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md).

### A1. Tool isolation and metadata accuracy

- **Completed 2026-11-04 — Fortis path-guidance correction:** the hash-pinned Desktop Commander 0.2.52 derivative was deployed to `fortis-repo-test`; post-cutover Docker verification passed, both Repo1/Repo2 Guard Previews passed, Repo2 live MCP metadata was verified and Repo1's corrected description was owner-confirmed. The path-guidance plan item is closed. The old container remains stopped for rollback; Qwen reconnect is not required for acceptance by owner decision, while the separate source-provenance observation remains non-blocking. See the [deployment record](../patches/desktop-commander-0.2.52/README.md) and [GO3 baseline audit](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md).
- **Completed 2026-11-04 — Desktop Commander MCP UI suppression:** the behavior-compatible 0.2.52 patch preserves the deployed path-guidance behavior and adds the G2-proven `DESKTOP_COMMANDER_DISABLE_MCP_UI=1` image default. Candidate build, disposable runtime checks and normalized Windows-host pre-cutover checks passed; the owner then executed the typed-confirmation cutover successfully. Both Repo1/Repo2 Guard Previews passed; Repo2 live runtime directly verified the environment switch, false UI-preview decision, empty UI-resource list and blocked reads for both UI resources; Repo1 post-cutover reconnect is owner-confirmed. The former path-guidance container is preserved as rollback; no named volume was deleted and no Windows profile or tunnel lifecycle action was requested. Qwen reconnect is not required for acceptance by owner decision. See the [verification audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md), [AI integrations](AI-INTEGRATIONS.md) and the [deployment record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md).
- Define separate capability profiles for read, write, process execution and deployment.
- Decide whether ChatGPT and Qwen need separate Linux identities, containers, mounts or workspace roots.
- Separate shared project files from credentials, runtime state and owner-only files.
- Treat MCP tool filtering as an interface restriction, not an OS security boundary.
- Add lightweight unit tests for pure allowlist/policy decisions, while keeping OS permissions as the actual enforcement layer; validate real container boundaries manually rather than building Docker mocks.

#### Optional host PowerShell and container-control bridge (PLANNED)

The normal execution path remains inside the existing Repo container. Investigate a separately brokered, least-privilege path for the occasional task that genuinely needs the Windows host or needs to rebuild/manage the agent's own container. Do not expose an unrestricted host shell as the shortcut.

- Compare a dedicated non-admin Windows service account plus NTFS ACLs, PowerShell JEA, Constrained Language Mode, WDAC/AppLocker and a small typed-operation broker. Protected owner directories and secrets must deny the AI identity both read and write access; verify inherited ACLs, traversal, junctions/reparse points and alternate paths.
- Prefer typed operations with fixed verbs, validated parameters and canonicalized paths over arbitrary `powershell -Command`, CMD, script text or free-form command strings. Keep the broker out of the owner's interactive profile and credentials.
- If a command-policy layer is added, parse PowerShell syntax/AST and validate the full execution chain: aliases, encoded/dynamic invocation, child processes, external executables, environment variables, working directory, file paths and network destinations. A text blocklist alone is not an enforcement boundary.
- Use deterministic deny-by-default policy as the enforcement layer. A second local or remote model may provide risk scoring/explanations, but must be advisory only; it must never turn a policy-denied command into an allowed command. Unknown or high-impact operations require explicit owner approval and an auditable receipt.
- For container self-management, use a narrow host-side broker for a named agent-owned target and an allowlisted build context. Never mount the Docker socket/named pipe or grant generic Docker API/CLI access to the AI. Deny host binds, privileged mode, host namespaces/network, devices, `VolumesFrom`, published ports and volume deletion; require owner approval for stop/start/recreate or other lifecycle changes. Account for the fact that the current Repo container is shared by Repo1, Repo2 and Qwen.
- Design egress separately: allow only required external services through a controlled proxy/VPN with fail-closed behavior; block private/LAN, link-local, metadata and host-gateway destinations except explicitly approved API endpoints. Do not claim anonymity from a VPN alone; review DNS, timezone, locale and host-identifying metadata.
- Acceptance must include adversarial tests proving that protected files cannot be listed/read/written, command-policy bypasses fail closed, child processes inherit restrictions, and the broker cannot escape its target container or approved network/API surface.

### A2. Authentication and credential isolation

- **Plan prepared 2026-11-05 — Gateway-mediated GitHub integration:** use a separate provider package, typed Gateway operations, operation-level ALLOW/ASK/DENY, and a new Gateway-only Fine-grained PAT or GitHub App credential in external volume `fortis-github-token` (read-only at `/run/github-token`). The volume and integration are not implemented or deployed. Keep the existing Repo Git credential helper for direct Git CLI operations until a separately reviewed replacement is proven; do not copy or revoke its PAT as part of Gateway onboarding. See `fortis-approvals/docs/INTEGRATION-MODULARIZATION-AND-GITHUB-ONBOARDING-PLAN.md`.
- **Separate remaining work — direct Git CLI credential isolation:** replace the shared AI-readable Repo PAT with a Git credential broker or narrowly scoped operation service. This is not automatically solved by adding a separate GitHub API credential to Gateway.
- Avoid placing long-lived credentials in the common workspace.
- Include the Repo Observatory API token and Repo machine grant in the same secret inventory; move them to per-agent secret mounts or brokers, and do not treat mode `0600`, directory mode `0700` or a read-only mount as protection from same-UID AI processes.
- Give each agent or service its own machine identity and least-privilege scopes where appropriate.
- Review the Repo machine grant exposure to same-UID processes.
- Keep the Gateway-held GitHub credential, legacy Repo Git PAT, Gateway Sonar token, machine grant, TLS identity and owner WebAuthn as separate credential domains.
- Define rotation, revocation, backup and incident-response procedures.

### A3. Controlled Git workflow and task isolation

The operating convention for ordinary application repositories is now agreed and owned by the [canonical Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md): primary clones stay on `main`; AI task work happens in linked Worktrees; feature branches pass through GitHub and the configured Actions checks before an owner-controlled Windows Worktree handoff. Do not maintain a second copy of its folder layout or commands here.

At the 2026-11-04 rollout snapshot, the Docker `Worktrees` root existed but was empty; no new project Worktrees had been created and existing linked Worktrees in legacy `Repos` paths had not been moved. Remaining Mirror implementation work includes linked-Worktree inventory, an unconditional non-main warning and the AI read-only API. The existing GUI's `АКТУАЛЕН · НЕ MAIN` label is conditional on fully synchronized Docker/GitHub/Windows state; see the canonical Mirror workflow for its exact behavior. Recheck live filesystem and Git state before any migration.

Remaining implementation work:
- Configure protected `main`, Pull Requests and required checks per repository where appropriate.
- Add CODEOWNERS or equivalent ownership metadata for shared source boundaries.
- Route write/push credentials through a broker with repository and operation scopes.
- Preserve no-force-push, no-history-rewrite and no-automatic-cleanup rules.

## Priority group B — source boundaries and releases

- **Completed 2026-11-03:** source inventory, original SHA-256 manifest and owner-approved standalone `fortis-approvals` repository at `/workspace/repos/fortis-approvals`; the original RDG subtree remains untouched. See the [source extraction audit](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/audits/SOURCE-EXTRACTION-2026-11-03.md).
- **Completed 2026-11-03:** selected offline/static regression run on the extracted candidate: 198 tests passed across 26 suites. Two historical-pointer test suites were corrected to read the preserved archive originals and verify the deploy-path archive pointers separately. This is not a full-suite or live Gateway/Sonar acceptance; missing `cryptography` and `fido2` still block additional WebAuthn-dependent tests. See the [test report](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/TEST-RESULTS-2026-11-03.md).
- **Owner-approved 2026-11-03:** the extracted tree is the canonical development source in the standalone `fortis-approvals` repository; local Git is initialized on `main`, while the original RDG subtree remains untouched. No commit or remote exists yet. Remote visibility, branch policy and credential scope remain separate decisions.

### Fortis Approvals Gateway naming cleanup (COMPLETED — 2026-11-05)

**Owner decision:** the active Gateway is R7-P1 / Compose project `fortis-r7-p1`. There is no G2/G4/R7 runtime conflict. The task was a minimal naming cleanup only; no deployment migration or data movement was wanted.

**Owner-provided Windows PowerShell output confirms successful in-place changes:**

| Object | Before | After / confirmed result |
|---|---|---|
| Running container | `fortis-r7-p1-fortis-1` | `fortis-approvals-gateway` |
| Container ID | `0852c39c9e5d0889290f94128b93555522d9447f9bebc7d880397bd43b4f5a6b` | Same ID; not recreated |
| Runtime status | Running / healthy before rename | `Up 44 minutes (healthy)` after rename |
| Image ID | `sha256:e751f6ca0cfe6ce290cf580de2f243071ee1f3e681baa8827c6cea41a16fa402` | Same image ID |
| Existing image tag | `fortis-r7-unified-read-ask-candidate:review-p2-20261103-a3e87c0c` | Retained |
| Added image tag | Absent | `fortis-approvals-gateway:current` → same image ID |
| Compose project/service | `fortis-r7-p1` / `fortis` | Retained; labels unchanged by the rename |
| Volumes, ports, networks, app config | Existing configuration | No volume, port, network or app-config operation was performed |

The container inspect output also showed the historical Compose config path `C:\Users\alexa\Downloads\fortis-r7-p2-rollout-go3-20261103\compose-r7-p2-20261103.yaml`. Its Compose image label referenced `sha256:6e3f806b...`, which was absent from the local image store; the actual container image was `sha256:e751f6ca...`. The new tag was correctly applied to the actual image ID, not the stale Compose label.

**Operations performed:** one `docker tag` and one `docker rename`. No stop/start, Compose up/down, container recreation, image build/pull, volume operation, data copy, credential operation, port change or application configuration change was performed. The post-operation evidence directly confirms the container ID, friendly name, healthy status and new image tag. A separate post-rename inspect of mounts/ports/networks and application E2E was not included in the supplied output; the commands used do not modify those properties.

**Compose caveat:** Docker's runtime rename does not change Compose project/service labels or the Compose file. If the container is later recreated by Compose, its generated name may return unless the authoritative Compose source is updated with `container_name: fortis-approvals-gateway`. Do not edit or redeploy the historical P2 Compose file as part of this completed naming-only task. If permanent Compose-managed naming is later required, handle that as a separate planned change with a reviewed deployment procedure.

**Rollback if ever needed:** rename the same container back to `fortis-r7-p1-fortis-1`. The extra image tag may be removed only after confirming it still points to the same image ID; do not remove the underlying image. No rollback is currently indicated.

The old full-migration candidate `fortis_approvals/deploy/compose-fortis-approvals-dryrun.yaml` is superseded. Retain it only as historical evidence; never run it with `up`, `create`, `start` or `down`.

- **Owner decision 2026-11-03:** do not create a separate Qwen repository or move its files now. Keep `/workspace/files/Qwen-Fortis-MCP` in place; revisit ownership only if the integration later needs independent release/versioning.
- **Completed 2026-11-05 — ChatGPT / Qwen MCP documentation consolidation:** `AI-INTEGRATIONS.md` now owns the 26-tool catalog and shared capability boundaries; the active Qwen route is documented as Windows `uvx` / `mcp-proxy` loopback SSE → `docker exec` → Desktop Commander 0.2.52. Updated the Qwen Workfiles README, architecture, source map, glossary and documentation navigation. No Windows configuration, running process, container, runtime source or MCP connection was changed. The Qwen route remains OWNER-REPORTED; a full JSON schema comparison is not archived.
- Review stale module docstrings in `fortis_approvals/repo_action_contract.py` and `fortis_approvals/sonar.py` as a separate code-maintenance task; do not infer deployed behavior from old comments.
- Separate canonical source, development worktree, deployed image and historical snapshot in release manifests.
- Add reproducible build metadata and source-to-image provenance.
- Keep runtime secrets and state out of source repositories.

## Priority group C — backup and recovery

- Define per-volume backup policy and retention.
- Test restore into an isolated environment before relying on backups.
- Preserve image digests, Compose references, source manifests and required package versions.
- Document recovery of Repo workspace, Git credentials, Gateway state, TLS identity, machine grants and Sonar credentials separately.
- Add post-restore integrity and connectivity checks.

## Priority group D — Approval and multi-agent growth

- Extend actor-specific machine identities and scopes.
- Expand typed service operations only with explicit policy and tests.
- Preserve the human owner as the authority for ASK operations.
- Add audit receipts and reconciliation for any new mutation.
- Do not add autonomous schedulers or multi-agent writes without a separate safety review.

## Implementation gates

Before changing any item:
1. Confirm the current deployed source and target.
2. Review the relevant threat model and owner scope.
3. Prepare a read-only Preview and rollback plan.
4. Use proportionate validation: simple unit/static checks for pure logic; manual owner verification for Docker CLI, volumes, Windows HOST, TLS, WebAuthn and live external APIs. Do not build heavy automation solely to imitate those environments.
5. Obtain explicit owner approval for runtime, credential or Windows changes.
6. Update this document with the accepted completion and link the dated audit or deployment evidence.
