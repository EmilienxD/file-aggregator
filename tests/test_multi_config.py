from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from file_aggregator.config import (
    merge_config_slices,
    resolve_config_paths,
    set_project_config_paths,
    list_projects_config,
)
from file_aggregator import aggregator


class TestMergeConfig(unittest.TestCase):
    def test_later_file_overrides_duplicate_target(self) -> None:
        slices = [
            ("/a.json", {"t.md": {"sources": ["1.md"], "enabled": True}}),
            ("/b.json", {"t.md": {"sources": ["2.md"], "enabled": False}}),
        ]
        merged = merge_config_slices(slices)
        self.assertEqual(merged["t.md"]["sources"], ["2.md"])
        self.assertFalse(merged["t.md"]["enabled"])


class TestProjectSettings(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.settings_path = os.path.join(self.test_dir, "settings.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_resolve_and_list_projects(self) -> None:
        a = os.path.join(self.test_dir, "a.json")
        b = os.path.join(self.test_dir, "b.json")
        with patch("file_aggregator.config.GLOBAL_SETTINGS_FILE", self.settings_path):
            set_project_config_paths("demo", [a, b])
            paths = resolve_config_paths("demo")
            self.assertEqual(paths, [os.path.abspath(a), os.path.abspath(b)])
            default_path, projects = list_projects_config()
            self.assertIn("demo", projects)
            self.assertEqual(projects["demo"], [os.path.abspath(a), os.path.abspath(b)])


class TestAggregatorMultiFile(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.path_a = os.path.join(self.test_dir, "a.json")
        self.path_b = os.path.join(self.test_dir, "b.json")
        for name, body in (("s1.md", "A"), ("s2.md", "B")):
            p = os.path.join(self.test_dir, name)
            with open(p, "w", encoding="utf-8") as f:
                f.write(body)
        self.s1 = os.path.join(self.test_dir, "s1.md")
        self.s2 = os.path.join(self.test_dir, "s2.md")

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_register_new_goes_to_first_file_by_default(self) -> None:
        paths = [self.path_a, self.path_b]
        aggregator.register_target(
            "out.md", [self.s1], config_paths=paths
        )
        self.assertTrue(os.path.isfile(self.path_a))
        self.assertFalse(os.path.isfile(self.path_b))
        with open(self.path_a, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("out.md", data)

    def test_register_into_second_file(self) -> None:
        with open(self.path_a, "w", encoding="utf-8") as f:
            f.write("{}")
        paths = [self.path_a, self.path_b]
        aggregator.register_target(
            "out.md", [self.s1], config_paths=paths, into_path=self.path_b
        )
        with open(self.path_b, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("out.md", data)

    def test_update_existing_stays_in_same_file(self) -> None:
        with open(self.path_a, "w", encoding="utf-8") as f:
            json.dump({"out.md": {"sources": [self.s1], "enabled": True}}, f)
        paths = [self.path_a, self.path_b]
        aggregator.register_target("out.md", [self.s2], config_paths=paths)
        with open(self.path_a, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["out.md"]["sources"], [self.s2])
        self.assertFalse(os.path.isfile(self.path_b))

    def test_remove_finds_correct_file(self) -> None:
        with open(self.path_a, "w", encoding="utf-8") as f:
            json.dump({"a.md": {"sources": [self.s1], "enabled": True}}, f)
        with open(self.path_b, "w", encoding="utf-8") as f:
            json.dump({"b.md": {"sources": [self.s2], "enabled": True}}, f)
        paths = [self.path_a, self.path_b]
        aggregator.remove_target("b.md", config_paths=paths)
        with open(self.path_b, encoding="utf-8") as f:
            self.assertEqual(json.load(f), {})
        with open(self.path_a, encoding="utf-8") as f:
            self.assertIn("a.md", json.load(f))


if __name__ == "__main__":
    unittest.main()
