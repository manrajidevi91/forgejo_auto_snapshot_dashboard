
from datetime import datetime
from utils import git_ops
from utils.logger import app_logger as logger

class SnapshotEngine:
    def __init__(self, project_path):
        self.project_path = project_path

    def create_snapshot(self, push_remote=None, push_branch=None):
        """Creates a new snapshot (commit) of the project."""
        try:
            # Check for changes
            status = git_ops.git_status(self.project_path)
            if not status:
                logger.info(f"No changes detected in {self.project_path}. Skipping snapshot.")
                return False, "No changes"

            # Add and commit
            git_ops.git_add_all(self.project_path)
            commit_message = f"auto-snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            git_ops.git_commit(self.project_path, commit_message)
            logger.info(f"Successfully created snapshot for {self.project_path}")

            # Push if requested
            if push_remote and push_branch:
                git_ops.git_push(self.project_path, push_remote, push_branch)
                logger.info(f"Successfully pushed snapshot to {push_remote}/{push_branch}")
            
            return True, commit_message
        except Exception as e:
            logger.error(f"Failed to create snapshot for {self.project_path}: {e}")
            return False, str(e)
