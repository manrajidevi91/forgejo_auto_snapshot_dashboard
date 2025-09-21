
import unittest
import os
import shutil
from utils import git_ops

class TestGitOps(unittest.TestCase):

    def setUp(self):
        self.test_dir = "./test_repo"
        os.makedirs(self.test_dir, exist_ok=True)
        git_ops.git_init(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_commit(self):
        with open(os.path.join(self.test_dir, "test.txt"), "w") as f:
            f.write("hello")
        git_ops.git_add_all(self.test_dir)
        git_ops.git_commit(self.test_dir, "Initial commit")
        # How to assert this? We'd need a way to read the log.
        pass

if __name__ == '__main__':
    unittest.main()
