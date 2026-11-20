# Fortis Registry P5 — durable desired-release candidates (2026-11-20)

**SOURCE-ONLY REFERENCE / NOT LIVE / NOT AN AUTHORITATIVE RELEASE QUEUE.**
This adds an offline persistent candidate journal to the accepted
[P5 desired-release preview](RELEASE-REGISTRY-P5-DESIRED-PREVIEW.md), complementing
the [component-scoped restrictions model](RELEASE-REGISTRY-P5-COMPONENT-RESTRICTIONS.md)
and [offline restriction snapshot journal](RELEASE-REGISTRY-P5-DURABLE-CONSTRAINTS.md).
The desired queue and active restrictions are distinct data domains; the
Registry must not enumerate everything permitted to work in parallel.

## Identity, scope, trust

`tools/registry/desired_store.py::DesiredCandidateStore` is an explicit-path
SQLite store with **no default location, no background worker and no live API**.
It accepts the exact *unverified preview result DTO* produced by
`tools/registry/desired_preview.py` (or an equivalent fixture). The store
rechecks record hash/shape, per-target scope and no-deployment consistency,
not original GitHub merge evidence. It does **not** independently establish:

- Merge inclusion in the selected `main`; complete changed paths and PR
  pagination; exact PR-body Release Impact, CI, or pinned catalog authenticity.
- Actor identity or authorization. The `actor` argument is a caller-provided
  label, **not** a machine credential or owner approval.
- Whether any component is installed, worker is quiescent, Gateway must stop,
  or a protected release attempt/backup actually succeeded.
- Whether a supplied `ancestryRef` is a valid protected proof. It is only a
  reference to an unverified claim; **not** permission to supersede a release
  in a live queue.

All persisted records are `PLANNED_UNVERIFIED`, their `actual=null`, artifact
`NOT_BUILT`, and all results expose `evidenceVerified=false`. The store has no
`DEPLOYED`, `REPORTED_COMPLETE`, `ALLOWED`, auto-CD or controller endpoint.
A future independently reviewed typed collector and actor-scoped admission
operation must validate every trust boundary before a real Registry is live.

## Data model and invariants

The reference schema separates `meta`, append-only `batches`, immutable
`records`, and ordered `events` linked by SHA-256. Each desired record binds
**repository + target + environment + selected source SHA + catalog SHA/digest**;
source-only build units are not physical deployment subjects. One selected
merged `main` SHA with several relevant PRs yields one desired version for
that target/environment; each record retains the **complete covered lineage**.
A validated no-deployment preview stores a candidate audit batch with
**zero records**, not a fake deployment. A batch with mixed catalog/source,
missing identifiers or fabricated installed state is rejected.

One `BEGIN IMMEDIATE` transaction verifies prior local chain, checks global
expected revision and operation-ID fingerprint, and atomically appends
original result, exact preview, rows and event. Same operation ID with
identical immutable payload returns the original receipt (lost ACK-safe);
conflicting reuse is refused. New request ID with already stored preview
is refused, rather than logging duplicate releases. Concurrent CAS allows
one committed revision and rejects other stale attempts. No hidden retries.

**Supersession is append-only.** New source SHA for an existing repository /
target / environment requires an explicit exact `supersedesRecordId`, same
catalog pin and a nonempty `ancestryRef` claim. It cannot overwrite prior
record or copy prior actual state. Wrong predecessor, changed catalog or
same source SHA masquerading as a new installed version stops; future
catalog migrations require a separate reviewed continuity contract. A new
independent component target can still be recorded without blocking the
whole repository or inventing restrictions. The store itself never uses a
release window to permit an effectful operation.

## Integrity, backup and limitations

`verify()` checks SQLite integrity and FK constraints, revision sequence,
preview/record hashes, operation fingerprints, immutable event chain and
supersession relationships. These checks detect many accidental or partial
mutations; they **do not prevent a privileged DB writer from rebuilding
hashes**. Production needs independent protected checkpoints and retention.

`backup_to(new_path)` creates one verified **inactive** SQLite-consistent
snapshot, never overwrites an existing path or restores into a live DB.
Path is explicitly supplied, with protected file checks; restore/permissions,
mount, encryption, owner, credentials and Windows controller evidence require
separate reviews. The code does not create a Production directory or volume.
The prior offline restrictions SQLite store is a separate candidate database;
these files do not form an installed shared Registry schema or migration.

## Offline source validation

Run from repo root:

`PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py' -q`

Fixtures cover duplicate replay, conflicting `operationId`, lost ACK,
concurrent CAS, multiple desired targets, no-deployment, cross-target
parallelism, explicit supersession and immutable older records, changed
catalog drift, wrong SHA, false installed state, SQLite tampering, restart,
backup and path safety. Preview compatibility tests **mock the external
JSON Schema gate only** (because the current Fortis Repo Python lacks pinned
`jsonschema`); the real preview itself fails closed when that dependency is
missing. Full unmocked schema integration in pinned CI remains pending.

Before any actual queue is live: authenticate actor, extend typed Gateway
READ to immutable complete merge/catalog/CI evidence, bind exact component
catalog identities, add independent integrity checkpoint/restore acceptance
and obtain owner-controlled operational grants. No P4 Deployments READ
re-release, GitHub Deployments WRITE, Windows release or Production change
is part of this source-only milestone.
