# Git workflow, credentials and recovery

## Workspace layout

- `/workspace/repo` is the root of the persistent `fortis-repo-workspace` volume; it is not itself a Git repository.
- `/workspace/repos` is the `Repos` subpath and contains Git checkouts.
- `/workspace/files` is the `Workfiles` subpath.
- The path aliases under `/workspace/repo/Repos` and `/workspace/repo/Workfiles` resolve to the same directories as `/workspace/repos` and `/workspace/files`.

Windows clones are separate directories. The documented Tunnel / Script Center delivery route is GitHub commits followed by a Windows Preview/Apply. There is no automatic filesystem synchronization of uncommitted files or runtime state.

## Current Git snapshot

| Repository | Branch / HEAD | Working tree |
|---|---|---|
| `tunnel` | `main` / `8172026` | 11 modified tracked files, 2 untracked task files; one worktree; no commit/push |
| `script-control-center` | `main` / `8fc2731` | 2 modified/staged entries, 44 untracked; second feature worktree |
| `rd-graphs` | `main` / `176ce44` | 58 modified/staged entries, 325 untracked, one deletion |
| `fortis-approvals` | `main` / no commit | Local Git initialized; 204 non-ignored untracked files; canonical development source owner-approved; no remote |
| `fortis-container` | `main` / `2119ccb` | First documentation-baseline commit; clean immediately after commit; no remote |

Never use `reset --hard`, `git clean`, broad stash, force-push or mass checkout to make these trees appear clean. Review only the files needed for the task. Do not commit unrelated work.

## Current owner-approved publishing convention

The root Fortis README records an owner decision from 2026-11-01 allowing direct commit/push to `main` for explicitly requested work. A feature branch or PR is not currently mandatory for every repository. This does not authorize force-push, branch deletion, history rewriting or overwriting another task's changes.

For Tunnel and Script Center, the documented Windows update is paired:
1. Review and test Docker source.
2. Publish the matching `tunnel/main` and `script-control-center/main` changes.
3. On Windows, run read-only Preview.
4. Only after review, run the explicit Apply.
5. Reconnect workers only as a separate owner-controlled action, one Repo at a time.

The paired updater does not stop/recreate the shared Fortis Repo container.

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

The current shared helper and the legacy file are GitHub credentials. They are not the Fortis machine grant, Gateway TLS key or SonarCloud token.

## Container restart and Git recovery

The root Fortis README documents `/home/node` as tmpfs, so global Git config may be lost after container recreation. The persistent workspace volume retains `.fortis-auth` files if the same volume is reattached. Do not assume that a newly created empty volume contains the credentials or repositories.

The helper can be re-enabled with the existing owner runbook script:

```bash
docker exec -u 1000:1000 fortis-repo-test \
  bash /workspace/repo/.fortis-auth/enable-shared-git-auth.sh
```

This changes the container user's Git config; it is not required for commands that explicitly specify the helper. If access fails, verify the correct volume and GitHub PAT scope through the owner-approved path. Never re-enter the PAT into chat or shell arguments.

## Worktrees and future Git organization

Use `git worktree list --porcelain` and `git status --short --branch` before starting work. Worktrees are useful for genuinely parallel tasks, but do not create branches/worktrees mechanically for every repository or task.

The current Script Center has a second feature worktree. Tunnel has one main worktree with the documentation/MCP-guidance changes listed above. RDG has one dirty main worktree. `fortis-approvals` and `fortis-container` are separate local Git repositories on `main`; `fortis-container` has the documentation-baseline commit `2119ccb`, `fortis-approvals` remains without a commit, and neither has a remote.

A more controlled Git model is PLANNED, not current:
- protected `main`;
- feature branches for substantial or parallel changes;
- Pull Requests and required CI for protected projects;
- explicit CODEOWNERS/review boundaries;
- narrow staging and commit scopes;
- controlled push credentials or a Git broker;
- no force-push and no automatic cleanup of another task's worktree.

## File transfer and backups

The root Fortis README documents `/workspace/repo/Workfiles/_fortis_windows_transfer_tmp/<task-id>/` for owner-reviewed one-off transfers. It is a temporary-purpose directory in a persistent volume, not a permanent source repository. Source files, tests and normative docs belong in their owning Git repository.

A SHA-256 match proves byte equality, not authorization to execute or deploy a file. Windows import/apply/run remains a separate owner-reviewed action.

Backups must cover both Git source and persistent runtime data. Git does not back up Docker volumes, Gateway databases, TLS private keys, machine grants, WebAuthn state or Sonar credentials. Those require separate volume-specific backup and restore procedures.
