# Legacy Git credential helper — historical record (2026-11-04)

**Status: ARCHIVED, not an operational instruction.** The earlier
`docs/GIT-AND-RECOVERY.md` documented a shared GitHub PAT and direct Git CLI
credential-helper workflow under the Fortis Repo workspace. It also described
independent local helper files in individual repositories and same-UID token
exposure (F-R-17). Those descriptions concern the historical workspace and
are not permission to use, inspect, print, restore or revoke any credential.

**Accepted current route:** all GitHub network operations from Fortis Repo use
UC-CONT-003 and the registered typed Gateway client; unsupported repo or
operation is STOP → UC-CONT-018, never fallback to the previous helper. Provider
credentials remain in Gateway, not in the shared Repo workspace.

Precise historical source and context are preserved in Git revisions before
the use-case migration. Removing historical documentation **does not delete**
the actual credential files or eliminate their exposure; reviewing/revoking
unused tokens requires a separate owner-controlled security task.
