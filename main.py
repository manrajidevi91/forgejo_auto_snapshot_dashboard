from flask import Flask, render_template, jsonify, request, send_from_directory
from app_config.config_loader import config_loader
from utils.logger import app_logger
from utils.paths import get_templates_dir, get_static_dir
from data import project_manager
from utils import git_ops
import os

# --- Service and Worker Imports ---
from services.scheduler_service import scheduler_service
from workers.snapshot_worker import take_snapshot

# --- Flask App Setup ---
app = Flask(__name__,
            template_folder=get_templates_dir(),
            static_folder=get_static_dir())

# --- API Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = project_manager.load_projects()
    return jsonify(projects)

@app.route('/api/add_project', methods=['POST'])
def add_project_route():
    data = request.get_json()
    project_path = data.get('path')
    if not project_path:
        return jsonify({"success": False, "message": "No project path provided"}), 400
    try:
        if not os.path.isdir(os.path.join(project_path, '.git')):
            git_ops.git_init(project_path)
        new_project = project_manager.add_project({'path': project_path})
        return jsonify({"success": True, "message": "Project added successfully", "project": new_project}), 201
    except Exception as e:
        app_logger.error(f"Failed to add project at {project_path}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project_route(project_id):
    data = request.get_json()
    
    # Get the current project state
    projects = project_manager.load_projects()
    current_project = next((p for p in projects if p['id'] == project_id), None)
    if not current_project:
        return jsonify({"success": False, "message": "Project not found"}), 404

    # Handle remote changes
    if 'remotes' in data:
        try:
            handle_remotes_update(current_project, data['remotes'])
        except Exception as e:
            app_logger.error(f"Failed to update remotes for project {project_id}: {e}")
            # Don't save the partial update if git commands fail
            return jsonify({"success": False, "message": f"Error updating remotes: {e}"}), 500

    # Update the rest of the project data
    updated_project = project_manager.update_project(project_id, data)
    if updated_project:
        return jsonify({"success": True, "project": updated_project})
    
    return jsonify({"success": False, "message": "Project not found"}), 404

def handle_remotes_update(project, new_remotes_data):
    project_path = project['path']
    current_remotes = {r['name']: r['url'] for r in project.get('remotes', [])}
    new_remotes = {r['name']: r['url'] for r in new_remotes_data}

    # Remotes to add/update
    for name, url in new_remotes.items():
        if name not in current_remotes or current_remotes[name] != url:
            app_logger.info(f"Adding/updating remote '{name}' for project {project['id']}")
            git_ops.git_remote_add(project_path, name, url)

    # Remotes to remove
    for name, url in current_remotes.items():
        if name not in new_remotes:
            app_logger.info(f"Removing remote '{name}' from project {project['id']}")
            git_ops.git_remote_remove(project_path, name)


@app.route('/api/projects/<project_id>/toggle_status', methods=['POST'])
def toggle_project_status(project_id):
    projects = project_manager.load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    if not project:
        return jsonify({"success": False, "message": "Project not found"}), 404

    interval = project.get('snapshot_interval', 15)
    new_status = "RUNNING" if project.get('status') != "RUNNING" else "PAUSED"
    
    if new_status == "RUNNING":
        scheduler_service.schedule_snapshot(project_id, take_snapshot, interval)
    else:
        scheduler_service.pause_snapshot(project_id)

    updated_project = project_manager.update_project(project_id, {"status": new_status})
    return jsonify({"success": True, "new_status": new_status, "project": updated_project})

@app.route('/api/projects/<project_id>/pending_changes', methods=['GET'])
def get_pending_changes(project_id):
    projects = project_manager.load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    if not project:
        return jsonify({"success": False, "message": "Project not found"}), 404
    try:
        status_output = git_ops.git_status(project['path'])
        changes_count = len(status_output.splitlines()) if status_output else 0
        return jsonify({"success": True, "pending_changes": changes_count})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/project_card_template')
def get_project_card_template():
    return send_from_directory(os.path.join(get_templates_dir(), 'partials'), 'project_card.html')

# --- Main Execution ---
def initialize_scheduler():
    scheduler_service.start()
    projects = project_manager.load_projects()
    running_projects = [p for p in projects if p.get('status') == 'RUNNING']
    app_logger.info(f"Found {len(running_projects)} running projects to reschedule.")
    for project in running_projects:
        interval = project.get('snapshot_interval', 15)
        scheduler_service.schedule_snapshot(project['id'], take_snapshot, interval)

if __name__ == '__main__':
    app_config = config_loader.get_app_config()
    initialize_scheduler()
    app.run(host="127.0.0.1", port=3000, debug=app_config.get("FLASK_DEBUG", False))
