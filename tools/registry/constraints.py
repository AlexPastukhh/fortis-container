"""Source-only, side-effect-free P5 component restriction evaluator.

A NO_REGISTRY_RESTRICTION result is not authorization; all existing UC,
Gateway policy and owner approvals still apply. Trusted snapshot provenance
and freshness MUST be checked by a future broker before operational use.
This module does no I/O and has no production activation path.
"""
from __future__ import annotations

import re
from collections.abc import Mapping


class ConstraintError(ValueError):
    """Malformed registry evidence: caller must fail closed, not retry effect."""


SOURCE_ONLY = frozenset({"source_edit", "source_review", "ci_read"})
EFFECTFUL = frozenset({
    "github_pr_publish", "gateway_request_write", "worker_claim",
    "gateway_check", "gateway_apply", "gateway_backup", "gateway_promote",
    "gateway_recovery", "container_replace", "state_write",
    "release_apply", "release_backup", "release_promote", "migration_apply",
})
ALL_OPERATIONS = SOURCE_ONLY | EFFECTFUL
_NAME = re.compile(r"[a-z0-9][a-z0-9._/-]{0,127}\Z")


def _fail(message):
    raise ConstraintError(message)


def _dict(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        _fail(f"{label}: invalid fields")
    return value


def _name(value, label):
    if not isinstance(value, str) or not _NAME.fullmatch(value) or "//" in value or ".." in value:
        _fail(f"{label}: invalid identity")
    return value


def _names(value, label, *, empty=True):
    if not isinstance(value, list) or (not empty and not value) or len(value) > 256:
        _fail(f"{label}: invalid list")
    result = [_name(v, label) for v in value]
    if len(set(result)) != len(result):
        _fail(f"{label}: duplicate identity")
    return set(result)


def _check_snapshot(snapshot):
    _dict(snapshot, ("schemaVersion", "components", "restrictions", "coverage"), "snapshot")
    if type(snapshot["schemaVersion"]) is not int or snapshot["schemaVersion"] != 1:
        _fail("snapshot: schema not supported")
    components = snapshot["components"]
    restrictions = snapshot["restrictions"]
    if not isinstance(components, list) or not isinstance(restrictions, list):
        _fail("snapshot: components/restrictions not lists")
    if len(components) > 256 or len(restrictions) > 1024:
        _fail("snapshot: oversized")
    by_id = {}
    known_resources = set()
    for component in components:
        _dict(component, ("id", "resources", "requires"), "component")
        ident = _name(component["id"], "component.id")
        if ident in by_id:
            _fail("component: duplicate id")
        resources = _names(component["resources"], "component.resources")
        requires = _names(component["requires"], "component.requires")
        if ident in requires:
            _fail("component: self dependency")
        by_id[ident] = (resources, requires)
        known_resources.update(resources)
    for _, requires in by_id.values():
        if not requires <= by_id.keys():
            _fail("component: unknown dependency")
    # Validate the entire graph, not only a request's reachable subtree.
    for component_id in by_id:
        _closure(component_id, by_id)
    seen = set()
    for rule in restrictions:
        _dict(rule, ("id", "components", "resources", "operations", "effect",
                     "phase", "reason", "sourceRef", "clearBy"), "restriction")
        ident = _name(rule["id"], "restriction.id")
        if ident in seen:
            _fail("restriction: duplicate id")
        seen.add(ident)
        comps = _names(rule["components"], "restriction.components")
        resources = _names(rule["resources"], "restriction.resources")
        if not comps and not resources:
            _fail("restriction: empty component/resource scope")
        if not comps <= by_id.keys() or not resources <= known_resources:
            _fail("restriction: unknown scoped component/resource")
        ops = _names(rule["operations"], "restriction.operations", empty=False)
        if not ops <= ALL_OPERATIONS:
            _fail("restriction: unknown operation")
        if rule["effect"] not in ("BLOCK", "REVIEW_REQUIRED"):
            _fail("restriction: invalid effect")
        for k in ("phase", "reason", "sourceRef", "clearBy"):
            if not isinstance(rule[k], str) or not rule[k].strip() or len(rule[k]) > 512:
                _fail(f"restriction: invalid {k}")
    coverage = _dict(snapshot["coverage"],
                     ("completeComponents", "completeResources", "fresh", "sourceRef"), "coverage")
    complete_components = _names(coverage["completeComponents"], "coverage.components")
    complete_resources = _names(coverage["completeResources"], "coverage.resources")
    if not complete_components <= by_id.keys() or not complete_resources <= known_resources:
        _fail("coverage: unknown component/resource")
    if type(coverage["fresh"]) is not bool:
        _fail("coverage: invalid freshness")
    if not isinstance(coverage["sourceRef"], str) or not coverage["sourceRef"].strip():
        _fail("coverage: sourceRef required")
    return by_id, complete_components, complete_resources


def _closure(start, components):
    result = set()
    visiting = set()

    def visit(current):
        if current in visiting:
            _fail("component: dependency cycle")
        if current in result:
            return
        visiting.add(current)
        for dependency in components[current][1]:
            visit(dependency)
        visiting.remove(current)
        result.add(current)

    visit(start)
    return result


def evaluate(snapshot: Mapping, request: Mapping) -> dict:
    """Evaluate *restrictions only*; never grants access to an operation.

    Components and their resources are obtained from the trusted catalog,
    never caller-provided affected-resource lists. New effectful operation
    names and incomplete/stale coverage require review, never silent approval.
    An active restriction is NEVER cleared by time/phase alone: only a new
    fully attested source snapshot can reflect a verified clearance.
    """
    components, covered_components, covered_resources = _check_snapshot(snapshot)
    _dict(request, ("component", "operation"), "request")
    component = _name(request["component"], "request.component")
    operation = _name(request["operation"], "request.operation")
    if component not in components:
        return {"result": "REVIEW_REQUIRED", "hits": [], "reason": "COMPONENT_NOT_CATALOGUED"}
    if operation not in ALL_OPERATIONS:
        return {"result": "REVIEW_REQUIRED", "hits": [], "reason": "OPERATION_NOT_CLASSIFIED"}
    effectful = operation in EFFECTFUL
    affected_components = _closure(component, components) if effectful else {component}
    # Always derive resources from the catalog; even a source-only operation
    # can be explicitly restricted on a shared resource. Only dependency
    # traversal is reserved for operations affecting a running component.
    affected_resources = set().union(*(components[x][0] for x in affected_components))
    hits = sorted(rule["id"] for rule in snapshot["restrictions"]
                  if operation in rule["operations"] and
                  (affected_components.intersection(rule["components"]) or
                   affected_resources.intersection(rule["resources"])))
    blocks = {rule["id"] for rule in snapshot["restrictions"] if rule["effect"] == "BLOCK"}
    if blocks.intersection(hits):
        return {"result": "BLOCKED", "hits": hits, "reason": "ACTIVE_RESTRICTION"}
    if hits:
        return {"result": "REVIEW_REQUIRED", "hits": hits, "reason": "ACTIVE_RESTRICTION"}
    if effectful and (not snapshot["coverage"]["fresh"] or
        not affected_components <= covered_components or
        not affected_resources <= covered_resources):
        return {"result": "REVIEW_REQUIRED", "hits": [], "reason": "COVERAGE_INCOMPLETE_OR_STALE"}
    return {"result": "NO_REGISTRY_RESTRICTION", "hits": [],
            "reason": "OTHER_POLICY_AND_OWNER_GATES_STILL_APPLY"}
