from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

from file_aggregator.config import load_config, save_config

class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_aggregator.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_load_empty_config(self) -> None:
        config = load_config(self.config_path)
        self.assertEqual(config, {})

    def test_save_and_load_config(self) -> None:
        test_data = {"target.md": {"sources": ["src1.md", "src2.md"], "enabled": True}}
        save_config(test_data, self.config_path)
        loaded_data = load_config(self.config_path)
        self.assertEqual(test_data, loaded_data)

    def test_config_migration(self) -> None:
        # Save old format
        old_data = {"target.md": ["src1.md", "src2.md"]}
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(old_data, f)
        
        # Load and verify migration
        loaded_data = load_config(self.config_path)
        expected_data = {"target.md": {"sources": ["src1.md", "src2.md"], "enabled": True}}
        self.assertEqual(loaded_data, expected_data)

    def test_load_corrupt_config(self) -> None:
        with open(self.config_path, 'w') as f:
            f.write("invalid json")
        config = load_config(self.config_path)
        self.assertEqual(config, {})

if __name__ == "__main__":
    unittest.main()
