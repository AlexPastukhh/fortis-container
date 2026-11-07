# Git workflow, credentials and recovery

## Workspace layout

- `/workspace/repo` is the root of the persistent `fortis-repo-workspace` volume; it is not itself a Git repository.
- `/workspace/repos` is the `Repos` subpath and contains Git checkouts.
- `/workspace/files` is the `Workfiles` subpath.
- The path aliases under `/workspace/repo/Repos` and `/workspace/repo/Workfiles` resolve to the same directories as `/workspace/repos` and `/workspace/files`.

Windows clones are separate directories. The documented Tunnel / Script Center delivery route is GitHub commits followed by a Windows Preview/Apply. There is no automatic filesystem synchronization of uncommitted files or runtime state.

## Last recorded Git snapshot (2026-11-04)

The rows below are a dated snapshot, not a live dashboard. `fortis-container` and `script-control-center` were rechecked read-only on 2026-11-04; the Tunnel and RDG rows remain earlier observations. Before any Git operation, inspect the exact repository's live branch, HEAD, remote and working tree; this document does not maintain live Git status.

| Repository | Branch / HEAD | Working tree |
|---|---|---|
| `tunnel` | `main` / `8172026` | 11 modified tracked files, 2 untracked task files; one worktree; no commit/push |
| `script-control-center` | `main` / `8fc2731` | Rechecked on 2026-11-04; second feature worktree existed at that snapshot; inspect live before acting |
| `rd-graphs` | `main` / `176ce44` | 58 modified/staged entries, 325 untracked, one deletion; not rechecked in this continuation |
| `fortis-approvals` | `main` / no commit | Local Git initialized; 204 non-ignored untracked files; canonical development source owner-approved; no remote; not rechecked in this continuation |
| `fortis-container` | `main` / `47e1761` (baseline commit `2119ccb` in history) | Rechecked on 2026-11-04; historical snapshot only, inspect live before acting |

Never use `reset --hard`, `git clean`, broad stash, force-push or mass checkout to make these trees appear clean. Review only the files needed for the task. Do not commit unrelated work.

## Ordinary project repository and Windows mirror workflow

The owner has selected the primary-clone + task-Worktree convention for ordinary application repositories: each Docker primary clone stays on `main`; AI development happens in a linked task Worktree; the task branch is pushed to GitHub and reviewed through its PR and configured Actions checks; after approval and merge, Windows updates only its primary clone to the merged `main`. Windows task Worktrees are not part of this workflow. The **canonical folder layout, commands and process are owned by the [Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md)**.

This supersedes the temporary 2026-11-01 direct-to-`main` simplification for ordinary application development. Repository-specific instructions and stricter branch-protection rules remain authoritative. This is currently a documentation/folder-convention rollout: the Mirror GUI has not yet gained Worktree discovery or the future read-only AI API, and no bulk Worktree migration has been performed.

The paired Tunnel / Script Center worker update is a specialized exception and remains governed by the [Script Center Windows update runbook](https://github.com/AlexPastukhh/script-control-center/blob/main/docs/GIT-WINDOWS-SOURCE-OF-TRUTH.md) and the [Tunnel Guard runbook](https://github.com/AlexPastukhh/tunnel/blob/main/runtime/windows-repo/README.md). Do not collapse that guarded updater into the ordinary application workflow.

## GitHub credential stores

The current shared helper is:
- helper: `/workspace/repo/.fortis-auth/git-credential-fortis-shared`;
- credential file: `/workspace/repo/.fortis-auth/github-shared/credentials`;
- parent directory mode: 0700;
- credential file mode: 0600, owned by UID 1000;
- helper mode: 0700.

The helper only answers HTTPS requests for `github.com/AlexPastukhh/<repo>`. GitHub still enforces the selected repository scope of the PAT. The credential is stored in Git credential-store format, which is not encrypted at rest.

The canonical helper can be selected explicitly for a Git command:

```bash
git -c credential.helper=/workspace/repo/.fortis-auth/git-credential-fortis-shared \
    -c credential.useHttpPath=true ls-remote --heads origin main
```

Use the same explicit helper only when a Git operation is authorized. Never print credentials, run `git credential fill`, place a token in a remote URL, command line, chat or log.

### Legacy credential store still present

A second file, `/workspace/repo/.fortis-auth/github-credentials`, exists with mode 0600. Its contents were not read. Local Git configuration in `rd-graphs`, `obs-planning-docs` and `tabnotifier-fileautosend-autochat` still references this file through `credential.helper=store --file=...`.

Do not delete this file or remove those local helper entries until each repository's access path is reviewed and migrated. The older interactive installer also writes this file. The existence of both stores means the phrase “one shared token/helper” is not a complete description of every current checkout.

The current global Git helper is a VS Code credential helper, not the Fortis shared helper. `enable-shared-git-auth.sh` may set the shared helper globally, but the global setting can be replaced by another tool. Prefer explicit helper selection after reviewing local per-repository settings.

### Security boundary

Both credential files live inside the persistent shared workspace, outside the Git repositories but readable by processes running as UID 1000. File mode 0600 protects against other UIDs; it does not protect the PAT from ChatGPT, Qwen or another same-UID process with file access. This is the documented F-R-17 risk.

### Planned Gateway GitHub credential — separate from Git CLI

The new Fortis Approvals GitHub integration will use a separate Gateway-only GitHub App credential or Fine-grained PAT, not either of the Repo credential files above. Target storage is a new external volume `fortis-github-token`, mounted read-only into Gateway at `/run/github-token`; the PAT file path is `/run/github-token/token`. This volume is not created or attached yet, and no GitHub operation is currently available through Gateway. Do not copy the existing Repo PAT into it. Do not remove or revoke the Repo Git credential helper until a separately reviewed Gateway-backed or brokered Git CLI workflow replaces it. The integration plan is maintained in the `fortis-approvals` repository under `docs/INTEGRATION-MODULARIZATION-AND-GITHUB-ONBOARDING-PLAN.md`.

The current shared helper and the legacy file are GitHub credentials. They are not the Fortis machine grant, Gateway TLS key or SonarCloud token.

## Container restart and Git recovery

The root Fortis README documents `/home/node` as tmpfs, so global Git config may be lost after container recreation. The persistent workspace volume retains `.fortis-auth` files if the same volume is reattached. Do not assume that a newly created empty volume contains the credentials or repositories.

The helper can be re-enabled with the existing owner runbook script:

```bash
docker exec -u 1000:1000 fortis-repo-test \
  bash /workspace/repo/.fortis-auth/enable-shared-git-auth.sh
```

This changes the container user's Git config; it is not required for commands that explicitly specify the helper. If access fails, verify the correct volume and GitHub PAT scope through the owner-approved path. Never re-enter the PAT into chat or shell arguments.

## Worktrees and repository layout

For ordinary application repositories, the [Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md) is the sole authority for primary-clone roles, the `Repos` / `Worktrees` directory convention and Docker → GitHub → Windows delivery. Use `git worktree list --porcelain` as Git's source of truth; do not infer Worktree membership from a directory name alone. This document retains only shared Git credential, repository-state and recovery guidance.

At the 2026-11-04 rollout snapshot, the Docker workspace contained the reserved empty directory `/workspace/repo/Worktrees`; no new project/task Worktrees had been created or existing ones moved, and pre-existing linked Worktrees remained under legacy paths in `Repos`. The then-documented Windows counterpart `%USERPROFILE%\Worktrees` is superseded by the target workflow: Windows keeps only its primary clone under `%USERPROFILE%\Repos\<repo>` on `main`; do not create Windows task Worktrees for ordinary application development. The Mirror GUI's full Worktree inventory and unconditional primary-branch warning plus AI read-only API remain future work. Recheck live filesystem and Git state before migration; see the canonical Mirror workflow for the operating convention.

Script Center and `fortis-container` were rechecked read-only on 2026-11-04; these values are historical observations, not current status. Tunnel and RDG values in the table above are also snapshots and must be rechecked before acting. `fortis-approvals` was last recorded as an owner-approved standalone repository on `main` without a commit or remote; inspect it live before any Git operation.

## File transfer and backups

The root Fortis README documents `/workspace/repo/Workfiles/_fortis_windows_transfer_tmp/<task-id>/` for owner-reviewed one-off transfers. It is a temporary-purpose directory in a persistent volume, not a permanent source repository. Source files, tests and normative docs belong in their owning Git repository.

A SHA-256 match proves byte equality, not authorization to execute or deploy a file. Windows import/apply/run remains a separate owner-reviewed action.

Backups must cover both Git source and persistent runtime data. Git does not back up Docker volumes, Gateway databases, TLS private keys, machine grants, WebAuthn state or Sonar credentials. Those require separate volume-specific backup and restore procedures.
