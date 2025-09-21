
# This worker will run on a schedule to prune old snapshots.
from services.retention_service import RetentionService
from data.projects import load_projects
from app_config.config_loader import load_config
from utils.logger import app_logger as logger

def run_prune_task():
    """The task that gets called to prune old snapshots for all projects."""
    logger.info("Starting prune task for all projects.")
    projects = load_projects()
    app_config = load_config()
    
    retention_policy = app_config.get('retention_policy') # Assuming this is how we get it
    if not retention_policy or not retention_policy.get('enabled'):
        logger.info("Snapshot pruning is disabled. Skipping.")
        return

    service = RetentionService(retention_policy)
    for project in projects:
        if project.get('pruning_enabled', True):
            service.prune(project['path'])
        else:
            logger.info(f"Pruning is disabled for project {project['name']}. Skipping.")
