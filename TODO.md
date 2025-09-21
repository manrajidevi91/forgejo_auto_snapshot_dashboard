# Forgejo Auto-Snapshot Dashboard: To-Do List

This document outlines the features and tasks required to complete the project as specified in the `PRD.md`. Tasks are prioritized with core functionality first.

---

## Phase 1: Core Snapshot Functionality

*This phase focuses on making the application perform its primary function: automatically taking snapshots.*

-   **[x] Implement Snapshot Worker:**
    -   Create a background scheduler service (`scheduler_service.py`).
    -   Integrate `watchdog` for file system monitoring.
    -   Implement a debounce mechanism (`utils/debounce.py`) to avoid excessive commits.
    -   Create the core snapshot logic (`workers/snapshot_worker.py`) that runs `git add -A` and `git commit`.
    -   Ensure the worker avoids creating empty commits.

-   **[x] Dynamic Project Card Updates:**
    -   Create a backend endpoint to get the number of pending changes (`git status`).
    -   Update the frontend to periodically fetch and display the pending changes count.
    -   Update the "Last Snapshot Time" on the card after a successful snapshot.

-   **[x] Project Status Control (RUN/PAUSE):**
    -   Implement the backend logic for the `toggle-status-btn` to start/stop the snapshot worker for a specific project.
    -   Update the UI to reflect the correct status.

---

## Phase 2: Configuration & Branching

*This phase focuses on giving users control over how snapshots are taken.*

-   **[x] Snapshot Interval Control:**
    -   Add UI elements in the Project Settings modal to configure the snapshot interval (per-project).
    -   Update `project_manager.py` to store this setting.
    -   Make the `scheduler_service.py` use the per-project or global default interval.

-   **[x] Branching Strategy:**
    -   Add UI in the Settings modal to select the "Autosnap Branch".
    -   Modify the snapshot worker to use the specified branch.
    -   Add a "Merge to main" button and its corresponding backend logic.

-   **[x] `.env` Configuration:**
    -   Transition from `app_config/defaults.json` to a `.env` file for loading application settings like the Forgejo URL.

---

## Phase 3: Forgejo Integration & Remotes

*This phase connects the local snapshots to the remote Forgejo server.*

-   **[x] Manage Remotes in UI:**
    -   Add UI to the Settings modal to add/edit/remove Forgejo remote URLs for a project.
    -   Store remote information in `projects.json`.

-   **[x] Implement Push Logic:**
    -   Add "Push Mode" options (e.g., Forgejo-only, No Push) to the Settings modal.
    -   The snapshot worker should push to the remote after a commit based on the selected mode.
    -   Display remote badges on the project card.

-   **[ ] Authentication:**
    -   Create a `services/credentials_service.py` to securely store and retrieve Forgejo PATs using the Windows Credential Manager.
    -   Use the stored credentials for push operations.

-   **[ ] Conflict Handling:**
    -   Implement a pre-push check to `git fetch` and detect if the remote has diverged.
    -   Implement a safe rebase strategy or notify the user that a manual pull is required.

-   **[ ] Forgejo API Integration:**
    -   Add a "Test Connection" button.
    -   (Optional) Implement the "Create Repository from Dashboard" feature.

---

## Phase 4: History, Restore & Logging

*This phase builds out the user's ability to view and interact with their project history.*

-   **[ ] History & Log Viewer:**
    -   Create a new page/modal to display the `git log` for a project in a user-friendly timeline.
    -   Create a global log viewer page (`templates/pages/logs.html`) to display the contents of `logs/app.log`.

-   **[ ] Restore Functionality:**
    -   In the history viewer, add buttons to "Preview" or "Restore" a file from a specific commit.
    -   Implement the backend logic to perform the restore as a new commit.

-   **[ ] Manual Snapshots:**
    -   Add a "Create Manual Snapshot" button, allowing the user to enter a custom commit message.

---

## Phase 5: System Integration & UX Polish

*This phase focuses on making the application feel like a native Windows utility.*

-   **[ ] First-Run Wizard:**
    -   Create a sequence of modals on the first launch to guide the user through initial setup.

-   **[ ] Startup Task:**
    -   Implement the "Install as Startup Task" functionality using the Windows Task Scheduler.

-   **[ ] Notifications:**
    -   Trigger the existing toast partial for events like successful snapshots, push failures, etc.
    -   (Optional) Add native Windows notifications for critical errors.

-   **[ ] UX Shortcuts:**
    -   Implement right-click context menus on project cards.
    -   Add quick filters to the main dashboard to show projects by status.

-   **[ ] Health & Safety Features:**
    -   Implement Disk Space Guard (`utils/disk_guard.py`).
    -   Implement protection against adding system folders.

---

## Phase 6: Advanced Features & Finalization

-   **[ ] Retention Policy / Pruning:**
    -   Create a `workers/prune_worker.py` to run periodically.
    -   Implement the logic to prune old snapshots based on user-defined policies.

-   **[ ] Import/Export Configuration:**
    -   Add buttons and backend routes to export the `projects.json` file and import a valid one.

-   **[ ] Help Page:**
    -   Populate the `templates/pages/help.html` page with instructions.

-   **[ ] Backup of Backups:**
    -   (Optional) Implement the feature to mirror snapshots to a NAS.