import importlib.util
import unittest
from unittest.mock import patch
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "pin_mod_versions.py"
SPEC = importlib.util.spec_from_file_location("pin_mod_versions", SCRIPT_PATH)
pin_mod_versions = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(pin_mod_versions)


class SelectLatestReleaseTests(unittest.TestCase):
    def test_prefers_matching_factorio_release_even_if_other_major_is_higher(self) -> None:
        releases = [
            {"version": "2.3.0", "info_json": {"factorio_version": "2.0"}},
            {"version": "11.3.0", "info_json": {"factorio_version": "1.1"}},
            {"version": "2.2.8", "info_json": {"factorio_version": "2.0"}},
        ]

        version, deps = pin_mod_versions.select_latest_release(releases, "2.0")

        self.assertEqual(version, "2.3.0")
        self.assertIsNone(deps)

    def test_rejects_releases_when_no_factorio_match_exists(self) -> None:
        releases = [
            {"version": "1.9.0", "info_json": {"factorio_version": "1.1"}},
            {"version": "1.8.5", "info_json": {"factorio_version": "1.0"}},
        ]

        version, deps = pin_mod_versions.select_latest_release(releases, "2.0")

        self.assertIsNone(version)
        self.assertIsNone(deps)

    def test_missing_factorio_version_is_not_compatible(self):
        self.assertEqual(pin_mod_versions.select_latest_release(
            [{"version": "9.0.0", "info_json": {}}], "2.1"), (None, None))

    def test_unfiltered_lookup_can_find_previous_pack_release(self):
        self.assertEqual(pin_mod_versions.select_latest_release(
            [{"version": "1.0.2", "info_json": {"factorio_version": "2.0"}}], None)[0], "1.0.2")

    def test_update_keeps_full_patch_and_uses_valid_equality(self):
        for mode, expected in [("gte", "example >= 1.2.9"), ("eq", "example = 1.2.9")]:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "info.json"
                path.write_text(json.dumps({"name": "test-pack", "version": "1.0.0",
                    "factorio_version": "2.1", "dependencies": ["example"]}))
                with patch.object(pin_mod_versions, "fetch_latest_version", return_value="1.2.9"), patch.object(
                        pin_mod_versions, "fetch_latest_release", return_value=(None, None)):
                    pin_mod_versions.process_file(str(path), mode, True, False, True, False)
                self.assertEqual(json.loads(path.read_text())["dependencies"], [expected])

    def test_missing_dependency_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "info.json"
            original = json.dumps({"name": "test-pack", "version": "1.0.0",
                "factorio_version": "2.1", "dependencies": ["missing"]})
            path.write_text(original)
            with patch.object(pin_mod_versions, "fetch_latest_version", return_value=None):
                self.assertEqual(pin_mod_versions.main(["--path", str(path), "--write", "--upgrade"]), 1)
            self.assertEqual(path.read_text(), original)

    def test_conflicts_do_not_get_version_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "info.json"
            path.write_text(json.dumps({"name": "test-pack", "version": "1.0.0",
                "factorio_version": "2.1", "dependencies": ["! incompatible"]}))
            with patch.object(pin_mod_versions, "fetch_latest_version") as fetch, patch.object(
                    pin_mod_versions, "fetch_latest_release", return_value=(None, None)):
                pin_mod_versions.process_file(str(path), "gte", True, False, True, False)
                fetch.assert_not_called()
            self.assertEqual(json.loads(path.read_text())["dependencies"], ["! incompatible"])


if __name__ == "__main__":
    unittest.main()
