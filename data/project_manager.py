import json
import os
import uuid
from utils.paths import get_projects_data_file
from utils.logger import app_logger as logger
PROJECTS_FILE = get_projects_data_file()

def load_projects():
    """Loads the list of projects from projects.json."""
    if not os.path.exists(PROJECTS_FILE):
        return []
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading projects file: {e}")
        return []

def save_projects(projects):
    """Saves the list of projects to projects.json."""
    try:
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(projects, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving projects file: {e}")

def add_project(project_data):
    """Adds a new project to the list and saves it."""
    projects = load_projects()
    
    # Create a new project object
    new_project = {
        "id": str(uuid.uuid4()),
        "name": project_data.get('name', os.path.basename(project_data.get('path'))),
        "path": project_data.get('path'),
        "status": "PAUSED",
        "last_snapshot_time": "N/A",
        "pending_changes_count": 0,
        "branch": "main",
        "remotes": [],
        "snapshot_interval": 15,
        "snapshot_branch": "autosnap",
        "push_mode": "no_push",
        "forgejo_username": ""
    }

    projects.append(new_project)
    save_projects(projects)
    logger.info(f"Added new project: {new_project['name']}")
    return new_project

def update_project(project_id, update_data):
    """Updates an existing project."""
    projects = load_projects()
    project_updated = False
    for project in projects:
        if project['id'] == project_id:
            project.update(update_data)
            project_updated = True
            break
    
    if project_updated:
        save_projects(projects)
        logger.info(f"Updated project {project_id} with data: {update_data}")
        return next((p for p in projects if p['id'] == project_id), None)
    else:
        logger.warning(f"Attempted to update non-existent project {project_id}")
        return None