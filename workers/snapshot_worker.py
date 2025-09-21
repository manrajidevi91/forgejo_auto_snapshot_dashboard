from data import project_manager
from utils import git_ops
from utils.logger import app_logger as logger
from datetime import datetime
import os

def take_snapshot(project_id):
    """
    Performs the snapshot logic for a given project.
    Includes committing changes and optionally pushing to a remote.
    """
    logger.info(f"Running snapshot for project_id: {project_id}")
    
    projects = project_manager.load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)

    if not project:
        logger.error(f"Snapshot failed: Project with id {project_id} not found.")
        return

    if project.get('status') != 'RUNNING':
        logger.info(f"Skipping snapshot for paused project: {project.get('name')}")
        return

    project_path = project.get('path')
    snapshot_branch = project.get('snapshot_branch', 'autosnap')
    push_mode = project.get('push_mode', 'no_push')

    if not project_path or not os.path.isdir(project_path):
        logger.error(f"Snapshot failed for {project.get('name')}: Path '{project_path}' not found.")
        return

    try:
        # 1. Ensure the correct branch is checked out
        git_ops.git_checkout_branch(project_path, snapshot_branch)

        # 2. Check for changes
        status_output = git_ops.git_status(project_path)
        if not status_output:
            logger.info(f"No changes for '{project.get('name')}'. Skipping snapshot.")
            return

        # 3. Add and commit changes
        logger.info(f"Changes detected for '{project.get('name')}'. Committing on branch '{snapshot_branch}'.")
        git_ops.git_add_all(project_path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"auto-snapshot: {timestamp}"
        git_ops.git_commit(project_path, commit_message)

        # 4. Update project's last snapshot time
        project_manager.update_project(project_id, {"last_snapshot_time": timestamp})
        logger.info(f"Successfully created snapshot for project '{project.get('name')}'")

        # 5. Push to remote if configured
        if push_mode == 'forgejo':
            # For now, we assume the primary remote is named 'origin'.
            # This can be made configurable later.
            remote_name = 'origin'
            remotes = project.get('remotes', [])
            if any(r['name'] == remote_name for r in remotes):
                logger.info(f"Pushing changes for '{project.get('name')}' to remote '{remote_name}'.")
                try:
                    git_ops.git_push(project_path, remote_name, snapshot_branch)
                    logger.info(f"Successfully pushed snapshot for '{project.get('name')}'")
                except Exception as push_error:
                    logger.error(f"Failed to push for '{project.get('name')}': {push_error}")
                    # Optionally, set status to ERROR or create a notification
            else:
                logger.warning(f"Push mode is 'forgejo' but remote '{remote_name}' not found for project '{project.get('name')}'.")

    except Exception as e:
        logger.error(f"An error occurred during snapshot for project '{project.get('name')}': {e}")
        project_manager.update_project(project_id, {"status": "ERROR"})