
import unittest
import os
import shutil
from services.snapshot_engine import SnapshotEngine
from utils import git_ops

class TestSnapshotEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = "./test_snapshot_repo"
        os.makedirs(self.test_dir, exist_ok=True)
        git_ops.git_init(self.test_dir)
        self.engine = SnapshotEngine(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_snapshot_no_changes(self):
        success, message = self.engine.create_snapshot()
        self.assertFalse(success)
        self.assertEqual(message, "No changes")

    def test_create_snapshot_with_changes(self):
        with open(os.path.join(self.test_dir, "test.txt"), "w") as f:
            f.write("hello world")
        success, message = self.engine.create_snapshot()
        self.assertTrue(success)
        self.assertTrue(message.startswith("auto-snapshot:"))

if __name__ == '__main__':
    unittest.main()
