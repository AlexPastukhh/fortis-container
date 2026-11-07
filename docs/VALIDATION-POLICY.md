# Validation policy

**Status:** owner-confirmed working rule, 2026-11-03.

## Principle

Use the least complicated validation that gives meaningful evidence. The goal is correctness and an honest record of what was checked, not maximum automated-test coverage.

## Appropriate automated checks

Automate checks that are local, deterministic and proportionate:

- pure business logic and state transitions;
- data parsing, formatting and transformation;
- policy decisions, allowlists and schema validation;
- source-level unit tests that do not pretend to reproduce unavailable infrastructure;
- static checks, syntax checks, documentation links and source-manifest hashes.

For copied source trees, targeted static/unit checks are sufficient when they cover the changed logic. A complete test suite is not required merely because a source copy exists.

## Manual owner verification

Keep real-environment checks manual when they require live infrastructure, credentials, hardware or host access:

- Docker Engine, containers, Compose, volumes, networks, mounts and restore/cutover;
- Windows HOST processes, installed applications, Tunnel launchers and Desktop Commander reconnects;
- live TLS, WebAuthn, hardware-backed authentication and cryptographic provisioning;
- external APIs, SonarCloud mutations, live Approval decisions and end-to-end network flows.

Use a short owner runbook and record the result/evidence. Do not claim these checks passed based only on source inspection or a mock.

## What not to build

- Do not build a heavy mock environment to imitate Docker, Windows, WebAuthn or external services.
- Do not add dependencies to the live Repo container solely to force complex integration suites to run.
- Do not create automated test infrastructure solely to increase coverage of operations that require the real Docker host, owner authentication or external credentials.
- Do not treat a missing dependency or unavailable host tool as a product failure; mark that particular check BLOCKED / MANUAL and state what evidence is still needed.

## Evidence labels

Use explicit labels in current-state documentation:

- **SOURCE-VERIFIED** — established from the current source/configuration.
- **LIVE-VERIFIED** — observed against the exact running target.
- **OWNER-REPORTED** — supplied by the owner but not independently observed in this session.
- **MANUAL-PENDING** — requires an owner-side real-environment check.
- **UNKNOWN** — available evidence does not establish the fact.

A successful static test proves only the static behavior it exercises. It does not prove deployment, runtime isolation, live authentication or external API behavior.
