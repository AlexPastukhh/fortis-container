# Fortis glossary

| Term | Meaning |
|---|---|
| Fortis Repo | Shared Docker-based MCP / Desktop Commander working environment; not a Git repository |
| `fortis-repo-test` | Owner-documented name of the Fortis Repo runtime container |
| `fortis-repo-workspace` | Persistent workspace volume mounted at the root and subpaths used by Fortis Repo |
| `/workspace/repo` | Workspace volume root |
| `/workspace/repos` | `Repos` subpath containing Git checkouts |
| `/workspace/files` | `Workfiles` subpath |
| Tunnel | Windows-side transport and Repo worker implementation owned by the `tunnel` repository |
| Repo1 / Repo2 | Separate ChatGPT Repo worker profiles using the shared Fortis Repo runtime |
| Script Control Center | Windows Script Catalog / Control Center application owned by `script-control-center` |
| Desktop Commander | MCP server exposing file, search and process tools in the Fortis Repo environment |
| Qwen MCP path | Windows `uvx` / `mcp-proxy` loopback-SSE route that starts a separate Desktop Commander 0.2.52 process in the existing Fortis Repo container; owner-provided transcript reports 26 tools and successful read/write/process operations |
| Fortis Approvals Gateway | Human-readable name for the separate service that authenticates Repo requests, applies policy and mediates owner-approved Sonar actions |
| Owner WebAuthn | Human-owner authentication used for approval decisions in the Fortis Approvals Gateway Owner Portal |
| Sonar token | Upstream SonarCloud credential held by Fortis Approvals Gateway, not mounted into Fortis Repo |
| ASK | Policy outcome requiring a human owner decision before execution |
| ALLOW | Policy outcome permitting a typed operation without owner approval, subject to grants and validation |
| DENY | Policy outcome refusing the operation |
| R7 / P1 / P2 | Historical implementation and deployment identifiers retained only where needed for provenance; not new product, service, container or volume names |
| Canonical source | The source location designated to own future changes for a component |
| Deployed copy | Code included in the running image or installed Windows runtime |
| Runtime state | Persistent operational data, secrets or databases; not source code |
| Worktree | A Git checkout linked to another branch in the same repository's Git metadata |

## Naming rules

Use human-readable component names in explanatory documents and the owner-approved `fortis-approvals-*` prefix for new Approval Docker resources. Do not introduce a release-numbering scheme now. Preserve R7/P1/P2 only in historical evidence and old artifact names needed for provenance. Any actual Docker resource rename is a separate migration requiring a complete identifier map, dependency review, rendered-Compose dry run, data-integrity checks and rollback plan; no deployed resource has yet been renamed.
