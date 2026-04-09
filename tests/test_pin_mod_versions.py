import importlib.util
import unittest
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

    def test_falls_back_to_highest_version_when_no_factorio_match_exists(self) -> None:
        releases = [
            {"version": "1.9.0", "info_json": {"factorio_version": "1.1"}},
            {"version": "1.8.5", "info_json": {"factorio_version": "1.0"}},
        ]

        version, deps = pin_mod_versions.select_latest_release(releases, "2.0")

        self.assertEqual(version, "1.9.0")
        self.assertIsNone(deps)


if __name__ == "__main__":
    unittest.main()
