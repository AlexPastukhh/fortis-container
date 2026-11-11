"""Schema+YAML integration tests; CI installs PyYAML/jsonschema beforehand."""
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_validation", ROOT / "tools/release/validate.py")
rv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rv)
HAS_DEPENDENCIES = (
    importlib.util.find_spec("yaml") is not None
    and importlib.util.find_spec("jsonschema") is not None
)


@unittest.skipUnless(HAS_DEPENDENCIES, "CI installs PyYAML and jsonschema")
class ReleaseSchemaExamplesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in (
            "README.md", "Dockerfile", "pyproject.toml",
            "src/info_hub/main.py", "alembic/env.py",
            "alembic/versions/001_migration.py", "docs/DEVELOPMENT.md"
        ):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n")
        schemas = ROOT / "docs/schemas"
        self.catalog = rv.load_data(
            (schemas / "feedbrain-catalog-example-v1.yaml").read_text(), "yaml"
        )
        self.impact = rv.load_data(
            (schemas / "feedbrain-release-impact-example-v1.yaml").read_text(), "yaml"
        )

    def test_examples_are_schema_and_semantically_valid(self):
        schemas = ROOT / "docs/schemas"
        rv.validate_schema(self.catalog, schemas / "build-target-catalog-v1.schema.json")
        rv.validate_schema(self.impact, schemas / "release-impact-v1.schema.json")
        self.assertEqual(
            rv.validate_catalog(self.catalog, self.root, "feed_and_search_and_bank_and_brain")["targets"],
            4
        )
        self.assertEqual(
            rv.validate_impact(self.impact, self.catalog, ["alembic/versions/001_migration.py"])["affectedTargets"],
            ["action-worker", "api", "migrate", "worker"]
        )

    def test_yaml_duplicate_key_fails_closed(self):
        with self.assertRaisesRegex(rv.ValidationError, "duplicate"):
            rv.load_data("a: 1\na: 2\n", "yaml")

    def test_yaml_anchor_fails_closed(self):
        with self.assertRaisesRegex(rv.ValidationError, "anchors"):
            rv.load_data("a: &alias 1\nb: *alias\n", "yaml")

    def test_schema_rejects_unknown_top_level_key(self):
        clone = deepcopy(self.catalog)
        clone["bogus"] = True
        with self.assertRaisesRegex(rv.ValidationError, "Additional properties"):
            rv.validate_schema(clone, ROOT / "docs/schemas/build-target-catalog-v1.schema.json")

    def test_schema_rejects_missing_release_impact(self):
        with self.assertRaisesRegex(rv.ValidationError, "required"):
            rv.validate_schema({}, ROOT / "docs/schemas/release-impact-v1.schema.json")


if __name__ == "__main__":
    unittest.main()
