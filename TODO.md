# Forgejo Auto-Snapshot Dashboard - To-Do List

This checklist breaks down the development work based on the project's PRD.

## Milestone 1: Core CRUD + Snapshot (Local)

- [ ] **Project Setup:**
    - [ ] Initialize Flask application structure.
    - [ ] Configure SQLAlchemy with SQLite and set up `alembic` for migrations.
    - [ ] Create initial database models as defined in the PRD (`app_settings`, `projects`, `secrets`, etc.).
    - [ ] Generate the initial database migration.
- [ ] **Core UI (Dashboard):**
    - [ ] Create a `base.html` template using Bootstrap 5.
    - [ ] Implement the main dashboard page (`/`) to list projects.
    - [ ] Design and implement the "Project Card" as a reusable partial template.
    - [ ] Add the "Add Project" button and its corresponding modal/form.
- [ ] **Project Management API:**
    - [ ] Create the API endpoint `POST /api/projects/add`.
    - [ ] Integrate `tkinter.filedialog.askdirectory()` to enable a native folder picker, triggered by the API.
    - [ ] Implement the logic to initialize a new project in the database.
- [ ] **Git Initialization:**
    - [ ] In the "Add Project" flow, check if the selected folder is a Git repository.
    - [ ] If not, implement the `git init -b main` command.
    - [ ] Add functionality to create a default `.gitignore` file from a template.
- [ ] **Snapshot Engine (Local Commits):**
    - [ ] Implement the `SnapshotEngine` service.
    - [ ] Use `watchdog` to monitor file system events for each active project.
    - [ ] Implement the debounce logic (dirty flag + quiet period) to avoid excessive commits.
    - [ ] Implement the core snapshot logic: `git add -A` followed by `git commit`.
    - [ ] Add a check (`git diff --cached --quiet`) to prevent creating empty commits.
- [ ] **Scheduler Service:**
    - [ ] Integrate and configure `APScheduler` into the Flask app.
    - [ ] Create a service to manage per-project snapshot jobs based on their configured intervals.
    - [ ] Implement Run/Pause functionality to control the scheduler jobs for each project.
- [ ] **History View:**
    - [ ] Create the "History" page UI.
    - [ ] Implement the API endpoint `GET /api/projects/<id>/commits` to fetch commit history.
    - [ ] Display the list of commits on the history page.

## Milestone 2: Push + Webhooks

- [ ] **Configuration:**
    - [ ] Implement the "Global Settings" page for app-wide configurations.
    - [ ] Add functionality to configure the Forgejo URL and store a Personal Access Token (PAT) securely using the `keyring` library.
    - [ ] Implement the "Project Settings" modal/page.
    - [ ] Allow users to configure remote repository URLs, push mode, and branch strategy for each project.
- [ ] **Push Functionality:**
    - [ ] Extend the `SnapshotEngine` to handle pushing commits to a remote repository.
    - [ ] Implement `git remote add` (if not exists) and `git push` commands.
    - [ ] Ensure authentication works seamlessly using the stored PAT.
- [ ] **Webhook Receiver:**
    - [ ] Create the webhook endpoint `POST /hooks/forgejo`.
    - [ ] Implement HMAC-SHA256 signature verification to secure the endpoint.
    - [ ] Log incoming webhook deliveries to the `webhook_deliveries` table for diagnostics.
- [ ] **Upstream Sync:**
    - [ ] When a valid `push` event is received, trigger an upstream sync job.
    - [ ] The job should run `git fetch --all --prune`.
    - [ ] Implement a "safe" rebase attempt (`git rebase origin/<branch>`).
    - [ ] If the rebase fails due to conflicts, update the project status to `UPSTREAM_CHANGED` and reflect this in the UI.

## Milestone 3: Retention + Restore

- [ ] **Restore Functionality:**
    - [ ] Add a "Restore" button to each commit in the "History" view.
    - [ ] Implement the API endpoint `POST /api/projects/<id>/restore/<hash>`.
    - [ ] The restore logic should check out the files from the target commit and create a *new* commit with the message "restore: ...".
    - [ ] Implement a diff viewer to show changes for a selected commit.
- [ ] **Retention Policy:**
    - [ ] Create the `retention_policies` table and corresponding SQLAlchemy model.
    - [ ] Implement UI controls in settings to configure retention policies (e.g., keep last N, tiered daily/weekly).
    - [ ] Create a `RetentionWorker` service to enforce these policies.
    - [ ] Schedule a nightly job via `APScheduler` to run the retention worker.
    - [ ] The worker should safely prune old commits without breaking the repository's history.
- [ ] **Logging & Notifications:**
    - [ ] Configure Python's `logging` module to write to `logs/app.log` and per-project logs.
    - [ ] Create the "Logs" page in the UI to display log files.
    - [ ] Integrate `win10toast` or `plyer` to provide optional native desktop notifications.
    - [ ] Implement in-app Bootstrap toasts for immediate feedback on user actions.

## Milestone 4: Windows Service + Polish

- [ ] **Windows Autostart:**
    - [ ] Create `scripts/install_startup_task.bat` and `uninstall_startup_task.bat` using the `schtasks` command.
    - [ ] Wire these scripts to buttons in the "Global Settings" page.
- [ ] **UI/UX Polish:**
    - [ ] Implement the extended actions on the Project Card (Open in Explorer, Open in Terminal).
    - [ ] Implement LFS detection and provide a UI toggle in Project Settings.
    - [ ] Create a "Help" page explaining how the application works.
    - [ ] Implement the global status bar with a Forgejo health check.
- [ ] **Configuration Management:**
    - [ ] Add functionality to export all project configurations to a single JSON file.
    - [ ] Add functionality to import configurations from a JSON file.
- [ ] **Error Handling & Guards:**
    - [ ] Implement a disk space guard to pause projects if free space is low.
    - [ ] Add detection for `.git/index.lock` to prevent concurrent Git operations.
    - [ ] Implement exponential backoff for failed push attempts.
- [ ] **Testing:**
    - [ ] Write unit tests for critical utilities and services (`git_ops`, `snapshot_engine`, webhook verification).
    - [ ] Write integration tests for the end-to-end user flows.
    - [ ] Perform manual QA testing as outlined in the PRD.
