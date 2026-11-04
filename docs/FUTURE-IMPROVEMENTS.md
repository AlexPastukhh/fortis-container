# Future improvements

**Status:** PLANNED. None of the items in this document are authorized for implementation merely by being listed here.

## Priority group A — tool isolation, credentials and Git

These three topics belong next to each other because they share the same trust boundary.

**Source-only follow-up (2026-11-03):** the Tunnel checkout contains a corrected candidate for the legacy Repo bridge's mount guidance; its 4/4 source tests pass. The installed bridge was not updated, and the current ChatGPT tool schema still contains stale Windows-mount wording. The installed Desktop Commander package also has generic Docker path-translation text. The active description/wrapper chain remains unresolved. No runtime metadata or package was changed.

### A1. Tool isolation and metadata accuracy

- Identify the active source chain for Desktop Commander tool descriptions and remove stale hard-coded Windows mount/path-translation claims. Prefer stable role descriptions and link to current-state documentation rather than embedding mutable mount details in every tool.
- Define separate capability profiles for read, write, process execution and deployment.
- Decide whether ChatGPT and Qwen need separate Linux identities, containers, mounts or workspace roots.
- Separate shared project files from credentials, runtime state and owner-only files.
- Treat MCP tool filtering as an interface restriction, not an OS security boundary.
- Add lightweight unit tests for pure allowlist/policy decisions, while keeping OS permissions as the actual enforcement layer; validate real container boundaries manually rather than building Docker mocks.

### A2. Authentication and credential isolation

- Replace the shared AI-readable GitHub PAT with a Git credential broker or narrowly scoped operation service.
- Avoid placing long-lived credentials in the common workspace.
- Give each agent or service its own machine identity and least-privilege scopes where appropriate.
- Review the Repo machine grant exposure to same-UID processes.
- Keep Gateway Sonar token, machine grant, TLS identity, owner WebAuthn and GitHub PAT as separate credential domains.
- Define rotation, revocation, backup and incident-response procedures.

### A3. More controlled Git workflow

- Protect `main` for repositories where a PR-based model is appropriate.
- Use feature branches for substantial work and true parallel development.
- Use Pull Requests, required CI and explicit review boundaries.
- Add CODEOWNERS or equivalent ownership metadata for shared source boundaries.
- Define when direct-to-main remains acceptable and who can authorize it.
- Use worktrees deliberately for parallel tasks; avoid uncontrolled branch/worktree proliferation.
- Route write/push credentials through a broker with repository and operation scopes.
- Explicitly prohibit force-push, history rewriting and cleanup of another task's worktree.

The current direct-to-main owner-approved convention remains the active rule until an explicit change is agreed.

## Priority group B — source boundaries and releases

- **Completed 2026-11-03:** source inventory, original SHA-256 manifest and owner-approved standalone `fortis-approvals` repository at `/workspace/repos/fortis-approvals`; the original RDG subtree remains untouched. See the [source extraction audit](../../fortis-approvals/docs/audits/SOURCE-EXTRACTION-2026-11-03.md).
- **Completed 2026-11-03:** selected offline/static regression run on the extracted candidate: 198 tests passed across 26 suites. Two historical-pointer test suites were corrected to read the preserved archive originals and verify the deploy-path archive pointers separately. This is not a full-suite or live Gateway/Sonar acceptance; missing `cryptography` and `fido2` still block additional WebAuthn-dependent tests. See the [test report](../../fortis-approvals/docs/TEST-RESULTS-2026-11-03.md).
- **Owner-approved 2026-11-03:** the extracted tree is the canonical development source in the standalone `fortis-approvals` repository; local Git is initialized on `main`, while the original RDG subtree remains untouched. No commit or remote exists yet. Remote visibility, branch policy and credential scope remain separate decisions.
- **Owner-approved naming direction:** use `Fortis Approvals Gateway` as the product/service name, `fortis-approvals` as the source repository, Compose project, `gateway` as the service, `fortis-approvals-gateway-1` as the generated container target, `fortis-approvals-gateway` as the image name, and `fortis-approvals-*` role-based volume names. Do not introduce release-number labels now; R7/P1/P2 remain only in historical evidence. See [Naming and rename plan](NAMING-AND-RENAME-PLAN.md).
- **Runtime resource rename — PLANNED, not performed:** a render-only target Compose candidate now exists at `fortis_approvals/deploy/compose-fortis-approvals-dryrun.yaml`. Still verify the actual Compose project/container/image/volume identifiers on the Docker host, reconcile the owner-reported old container name with the preserved Compose reference, inventory dependent scripts and clients, render and compare the candidate configuration, then prepare data-preserving volume migration and rollback. Do not rename or recreate active resources as part of documentation work.
- **Owner decision 2026-11-03:** do not create a separate Qwen repository or move its files now. Keep `/workspace/files/Qwen-Fortis-MCP` in place; revisit ownership only if the integration later needs independent release/versioning.
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
6. Update this document and the current-state evidence after acceptance.
