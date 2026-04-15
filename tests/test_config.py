import unittest
import os
import json
import shutil
import tempfile
from file_aggregator.config import load_config, save_config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_aggregator.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_empty_config(self):
        config = load_config(self.config_path)
        self.assertEqual(config, {})

    def test_save_and_load_config(self):
        test_data = {"target.md": ["src1.md", "src2.md"]}
        save_config(test_data, self.config_path)
        loaded_data = load_config(self.config_path)
        self.assertEqual(test_data, loaded_data)

    def test_load_corrupt_config(self):
        with open(self.config_path, 'w') as f:
            f.write("invalid json")
        config = load_config(self.config_path)
        self.assertEqual(config, {})

if __name__ == "__main__":
    unittest.main()
