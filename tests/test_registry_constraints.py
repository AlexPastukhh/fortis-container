"""No-network P5 restriction-only coordination checks."""
import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

spec = importlib.util.spec_from_file_location("constraints", Path(__file__).resolve().parents[1] / "tools/registry/constraints.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
G = "fortis-approvals/primary/gateway"
O = "fortis-approvals/owner/portal"
R = "rd-graphs/backend/api"


def fixture():
    return {"schemaVersion": 1,
        "components": [
            {"id": G, "resources": ["gateway-runtime", "gateway-state"], "requires": []},
            {"id": O, "resources": ["owner-ui-runtime"], "requires": [G]},
            {"id": R, "resources": ["rdg-runtime"], "requires": []}],
        "restrictions": [
            {"id": "gateway-quiescence", "components": [G], "resources": ["gateway-state"],
             "operations": ["gateway_request_write", "gateway_apply", "release_apply"],
             "effect": "BLOCK", "phase": "QUIESCENCE", "reason": "protected state",
             "sourceRef": "UC-GW-005", "clearBy": "owner receipt and new readback"},
            {"id": "gateway-backup", "components": [G], "resources": [],
             "operations": ["gateway_backup", "gateway_promote"],
             "effect": "REVIEW_REQUIRED", "phase": "VERIFY", "reason": "owner gate",
             "sourceRef": "UC-GW-005", "clearBy": "owner receipt"}],
        "coverage": {"completeComponents": [G, O, R],
                     "completeResources": ["gateway-runtime", "gateway-state", "owner-ui-runtime", "rdg-runtime"],
                     "fresh": True, "sourceRef": "offline-fixture-only"}}


class ComponentRestrictionTests(unittest.TestCase):
    def check(self, component, operation, obj=None):
        return rc.evaluate(fixture() if obj is None else obj,
                           {"component": component, "operation": operation})

    def test_gateway_block(self):
        self.assertEqual(self.check(G, "gateway_apply")["result"], "BLOCKED")
        self.assertEqual(self.check(G, "gateway_request_write")["result"], "BLOCKED")

    def test_dependency_and_unrelated_component(self):
        self.assertEqual(self.check(O, "release_apply")["result"], "BLOCKED")
        self.assertEqual(self.check(R, "release_apply")["result"], "NO_REGISTRY_RESTRICTION")

    def test_source_work_not_whole_repo_block(self):
        self.assertEqual(self.check(G, "source_edit")["result"], "NO_REGISTRY_RESTRICTION")

    def test_review_and_other_approval(self):
        self.assertEqual(self.check(G, "gateway_backup")["result"], "REVIEW_REQUIRED")
        self.assertEqual(self.check(G, "gateway_check")["reason"], "OTHER_POLICY_AND_OWNER_GATES_STILL_APPLY")

    def test_unknown_coverage(self):
        f = fixture(); f["coverage"]["completeResources"].remove("gateway-state")
        self.assertEqual(self.check(G, "gateway_check", f)["reason"], "COVERAGE_INCOMPLETE_OR_STALE")
        f = fixture(); f["coverage"]["fresh"] = False
        self.assertEqual(self.check(R, "release_apply", f)["result"], "REVIEW_REQUIRED")
        self.assertEqual(self.check(R, "source_edit", f)["result"], "NO_REGISTRY_RESTRICTION")
        self.assertEqual(self.check(G, "gateway_apply", f)["result"], "BLOCKED")

    def test_unknown_name_cannot_get_permission(self):
        self.assertEqual(self.check(R, "new_future_deploy")["reason"], "OPERATION_NOT_CLASSIFIED")
        self.assertEqual(self.check("new/project/runtime", "release_apply")["reason"], "COMPONENT_NOT_CATALOGUED")

    def test_request_cannot_omit_resources(self):
        with self.assertRaises(rc.ConstraintError):
            rc.evaluate(fixture(), {"component": G, "operation": "gateway_apply", "resources": []})

    def test_shared_resource_blocks_across_repos(self):
        f = fixture(); f["components"][2]["resources"].append("gateway-state")
        self.assertEqual(self.check(R, "release_apply", f)["result"], "BLOCKED")

    def test_explicit_source_freeze(self):
        f = fixture(); x = deepcopy(f["restrictions"][0]); x["id"] = "source-freeze"
        x["resources"] = []; x["operations"] = ["source_edit"]
        f["restrictions"].append(x)
        self.assertEqual(self.check(G, "source_edit", f)["result"], "BLOCKED")

    def test_phase_is_not_automatic_clearance(self):
        f = fixture(); f["restrictions"][0]["phase"] = "AFTER_CHECK"
        self.assertEqual(self.check(G, "gateway_apply", f)["result"], "BLOCKED")

    def test_invalid_snapshot_fails_closed(self):
        f = fixture(); f["restrictions"].append(deepcopy(f["restrictions"][0]))
        with self.assertRaisesRegex(rc.ConstraintError, "duplicate id"): self.check(R, "source_edit", f)
        f = fixture(); f["components"][1]["requires"] = ["missing/a/b"]
        with self.assertRaisesRegex(rc.ConstraintError, "unknown dependency"): self.check(O, "source_edit", f)
        f = fixture(); f["components"][0]["requires"] = [O]
        with self.assertRaisesRegex(rc.ConstraintError, "dependency cycle"): self.check(O, "release_apply", f)
        f = fixture(); f["restrictions"][0]["resources"] = ["undeclared"]
        with self.assertRaisesRegex(rc.ConstraintError, "unknown scoped"): self.check(G, "source_edit", f)
        f = fixture(); f["restrictions"][0]["clearBy"] = ""
        with self.assertRaisesRegex(rc.ConstraintError, "invalid clearBy"): self.check(G, "source_edit", f)

    def test_no_restrictions_is_not_authorization(self):
        f = fixture(); f["restrictions"] = []
        self.assertEqual(self.check(G, "gateway_request_write", f)["result"], "NO_REGISTRY_RESTRICTION")


if __name__ == "__main__":
    unittest.main()
