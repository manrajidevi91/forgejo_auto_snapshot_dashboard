import subprocess
import os
import shutil
from .logger import app_logger as logger
from . import paths

def run_git_command(path, command):
    """Runs a Git command in a specified directory."""
    try:
        result = subprocess.run(
            command, 
            cwd=path, 
            check=True, 
            capture_output=True, 
            text=True, 
            shell=True
        )
        logger.info(f"Git command successful in {path}: {' '.join(command)}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed in {path}: {' '.join(command)}\nError: {e.stderr.strip()}")
        raise

def git_init(path):
    """Initializes a new Git repository and adds a default .gitignore."""
    run_git_command(path, ["git", "init"])
    try:
        template_path = os.path.join(paths.get_gitignore_template_dir(), 'gitignore_python.txt')
        dest_path = os.path.join(path, '.gitignore')
        if not os.path.exists(dest_path):
            shutil.copyfile(template_path, dest_path)
            logger.info(f"Created default .gitignore file in {path}")
    except Exception as e:
        logger.error(f"Failed to create .gitignore file in {path}: {e}")
        # We don't re-raise here because git init succeeded.
        # The main operation was successful, this is an enhancement.

def git_add_all(path):
    """Stages all changes."""
    return run_git_command(path, ["git", "add", "-A"])

def git_commit(path, message):
    """Creates a commit."""
    # Use -m flag for message
    return run_git_command(path, ["git", "commit", "-m", message])

def git_status(path):
    """Gets the status of the repository."""
    return run_git_command(path, ["git", "status", "--porcelain"])

def git_push(path, remote, branch):
    """Pushes to a remote repository."""
    return run_git_command(path, ["git", "push", remote, branch])

def git_checkout_branch(path, branch_name):
    """Ensures a branch exists and checks it out."""
    return run_git_command(path, ["git", "checkout", "-B", branch_name])

def git_remote_add(path, remote_name, remote_url):
    """Adds a new remote."""
    # It's safer to remove a remote if it exists, to avoid errors if the URL has changed.
    try:
        run_git_command(path, ["git", "remote", "rm", remote_name])
    except:
        # This will fail if the remote doesn't exist, which is fine.
        pass
    return run_git_command(path, ["git", "remote", "add", remote_name, remote_url])

def git_remote_remove(path, remote_name):
    """Removes a remote."""
    return run_git_command(path, ["git", "remote", "rm", remote_name])



# Add other git operations as needed based on PRD...