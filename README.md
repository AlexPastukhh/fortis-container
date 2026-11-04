# Fortis Container — system documentation

> **Status:** first-stage documentation and source review are complete. The original Fortis Repo Dockerfile/build log and the matching Tunnel copy have now been recorded in [Container build provenance](docs/CONTAINER-BUILD-PROVENANCE.md); the exact historical build context and command remain unknown. Two first-stage host/runtime gates remain open: deploy the owner-approved Desktop Commander tool-description correction (blocked by root-owned package permissions in this session) and complete the Windows-host rendered Compose check. The owner-approved local Git repository is on `main` with its first documentation-baseline commit (`2119ccb`); no remote or deployment configuration change has been made. This directory is a documentation project, not a Docker container.

## Purpose

This project is the central map for the shared Fortis Repo workspace, its AI integrations, Fortis Approvals, authorization boundaries, source ownership, Git workflow, recovery and container-build provenance. It complements rather than replaces the source repositories. The original Windows Dockerfile and build log have now been located and documented, and an identical Dockerfile copy exists in Tunnel's historical Repo Mode directory. However, no canonical Git-managed build context or complete reproducible build definition has yet been established or added here.

## Start here

| Need | Document |
|---|---|
| Understand the whole system | [Architecture](docs/ARCHITECTURE.md) |
| Know what is verified now | [Current state](docs/CURRENT-STATE.md) |
| Understand Docker storage | [Containers and volumes](docs/CONTAINERS-AND-VOLUMES.md) |
| Understand the image recipe, original build evidence and remaining provenance gaps | [Container build provenance](docs/CONTAINER-BUILD-PROVENANCE.md) |
| Understand ChatGPT and Qwen | [AI integrations](docs/AI-INTEGRATIONS.md) |
| Understand machine auth and owner approval | [Authorization and approvals](docs/AUTHORIZATION-AND-APPROVALS.md) |
| Find the canonical source | [Source map](docs/SOURCE-MAP.md) |
| Work safely with Git and recover state | [Git and recovery](docs/GIT-AND-RECOVERY.md) |
| Understand terms and component names | [Glossary](docs/GLOSSARY.md) |
| Review agreed Docker names and the rename plan | [Naming and rename plan](docs/NAMING-AND-RENAME-PLAN.md) |
| See planned improvements | [Future improvements](docs/FUTURE-IMPROVEMENTS.md) |
| Inspect the baseline evidence | [Audit 2026-11-03](docs/audits/BASELINE-2026-11-03.md) |

## Scope and authority

This repository documents the Fortis Repo container environment and its adjacent systems. It does not own the implementation of Tunnel workers, Script Control Center, RDG, or Fortis Approvals.

- `tunnel` owns Repo1/Repo2 worker and shared Guard source.
- `script-control-center` owns the Windows Script Catalog, UI, adapters and updater.
- `rd-graphs` owns RDG; its original `fortis_approvals/` subtree remains preserved and untouched.
- `fortis-approvals` owns the canonical development source for the Fortis Approvals Gateway; its extracted package was owner-approved as a standalone repository.
- `fortis-container` owns this cross-project documentation and has its own local Git repository.

## Evidence labels

- **LIVE VERIFIED** — observed directly in the current Fortis Repo process or by a test run in this session.
- **SOURCE VERIFIED** — established by reading the current source code.
- **OWNER-REPORTED** — present in owner-provided current-state or deployment evidence, but not independently inspected here.
- **HISTORICAL** — dated evidence that must not be treated as current runtime state.
- **PLANNED** — proposed work, not implemented.
- **UNKNOWN** — not established by available evidence.

A source test or proxy log alone does not establish the exact tools selected in a Qwen chat or the full Docker runtime state.

## Path convention

Use `/workspace/repos/<repo>` as the canonical path to Git checkouts and `/workspace/files/<name>` for Workfiles. The aliases `/workspace/repo/Repos` and `/workspace/repo/Workfiles` currently resolve to the same directories; the mount evidence is recorded in the audit.

## Safety rule

Before changing Docker, credentials, mounts, networks, Windows launchers or active processes, read the relevant owner runbook and verify the exact live target. Documentation work must not stop, restart, recreate or reprovision a service.

## First-stage progress

- [x] Read-only inventory of the current workspace and Git status.
- [x] Initial architecture, storage, AI integration, authorization and Git baseline.
- [x] Verify the current workspace mount aliases and the separate read-only `/run/fortis-client` mount; inspect file metadata without reading the grant.
- [x] Qwen STDIO candidate syntax and local six-tool read-only acceptance test.
- [x] Locate the original Windows Fortis Repo build directory; record its Dockerfile, build log, backup inventory, matching Tunnel Dockerfile hash and image-ID/digest correlation. Record the unresolved original build context and `.dockerignore` discrepancy in [Container build provenance](docs/CONTAINER-BUILD-PROVENANCE.md).
- [x] Record the owner-reported Qwen proxy transport, pinned six-tool source, and separate practical transcript evidence of 26 tools with successful write/process operations; source-to-session provenance remains non-blocking.
- [x] Extract Fortis Approvals into a separate repository; owner approved it as the canonical development source; 196-entry original SHA-256 manifest preserved, current-copy manifest tracks those same entries, with four documented copy-only changes plus a separate render-only Compose candidate outside the extraction manifest.
- [x] Run 198 tests across 26 selected offline/static suites; record missing-dependency blockers and correct two archive-pointer test references.
- [x] Reconcile key stale Tunnel documentation and label historical material.
- [x] Agree human-readable names (`Fortis Approvals Gateway`) and target Docker naming (`fortis-approvals-*`); do not introduce release-number labels now. R7/P1/P2 remain only in historical evidence.
- [x] Document the three separate request cases: machine authentication plus owner approval, machine authentication without owner approval, and the not-yet-implemented owner-approved action without an upstream API token. Explicitly record that the Gateway machine ingress has no unauthenticated route.
- [x] Normalize current explanatory documentation to `Fortis Approvals Gateway`; retain old volume, path, API and artifact identifiers only where they identify existing implementation or historical evidence.
- [x] Record the owner-confirmed validation policy: automate simple deterministic logic/static checks; use manual owner verification for Docker, Windows, WebAuthn, TLS and external API operations; do not build heavy mocks or test harnesses for them.
- [x] Trace the legacy bridge and direct Repo1/Repo2 launcher paths: current workers use the direct Desktop Commander entry point; the legacy bridge is not in their current process path. The corrected bridge candidate passes 4/4 source tests, but is not deployed.
- [ ] Deploy the owner-approved correction to installed Desktop Commander `system-info.js`: remove generic `/home` translation and `/home/[folder-name]` installer assumptions from both mounted and no-mount branches, preserve dynamic mountpoint reporting, then reconnect only the ChatGPT Fortis Repo MCP instance and verify `read_file` and `start_process` in the app UI. Source is established (`server.js:791-798`, `system-info.js:585-593`, `system-info.js:598-601`). Not applied: package is root-owned and the connected process is UID 1000 without write permission.
- [x] Owner approved the extracted Fortis Approvals tree as the canonical development source and a standalone repository.
- [x] Record owner-provided Qwen evidence of 26 tools and successful read/write/edit/move/process operations. The pinned six-tool read-only gateway source is not proven to be the source of that observed full tool surface; this provenance discrepancy is documented but is not a functional blocker.
- [x] Run post-edit Markdown link validation across both repositories: 34 non-archive Markdown documents, 94 local links, 0 broken.
- [x] Review terminology in the current normative set; preserve original identifiers in historical records and label their status explicitly.
- [x] Initialize local Git metadata for `fortis-approvals` and `fortis-container`; create the first local documentation-baseline commit only in `fortis-container`. No remote or push was created. Remote visibility and credential scope remain separate decisions.
- [x] Prepare a render-only Compose candidate using the approved target names; preserve the supplied runtime/security settings and clearly prohibit `up`/`create`/`start`/`down`.
- [ ] Complete the owner-side read-only Docker inventory and rendered Compose dry run for the approved target names. Docker CLI is unavailable in this Repo container, so this host-side step has not been run. No runtime resource has been renamed; a separate explicit approval is required before any data copy or runtime cutover.

The two unchecked items above are not documentation tasks. Owner approval for the Desktop Commander correction has been granted, but deployment is blocked because the installed package is root-owned and this MCP process has no write privilege; no active package file was changed and no MCP process was killed because no safe restart path was identified. Apply the patch through root-level container deployment, then reconnect only the ChatGPT Fortis Repo MCP instance and verify both descriptions. The Windows Docker inventory/render remains a host-side check unavailable from this Repo container. No runtime change is implied.

`fortis-container` now has its first local documentation-baseline commit on `main`; `fortis-approvals` remains initialized without a commit. Neither repository has a remote. Do not publish either repository until visibility and credential scope are explicitly settled.
