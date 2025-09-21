# Product Requirements Document: Forgejo Auto-Snapshot Dashboard

## 1. Overview & Goal

**App Name:** Forgejo Auto-Snapshot Dashboard
**Technology:** Python (Flask), running on Windows.
**Core Goal:** To provide a simple desktop dashboard for developers on Windows to automatically create version-controlled snapshots of their projects. Users can select a folder to add it as a "Project," and the tool will manage background snapshots (git commits/pushes) and allow UI-based configuration for each project.

**Forgejo Instance URL:** `https://forgejo.iticareer.com/`

---

## 2. Core Features & Workflow

### 2.1. Project Management

*   **Add Project:** Users can click an "Add Project" button which opens the native Windows file picker to select a project folder.
*   **Automatic Git Initialization:** If the selected folder is not a git repository, the tool will automatically run `git init` and create a default `.gitignore` file.
*   **Project Naming:**
    *   The project name will be automatically set from the selected folder's name.
    *   Users must have the ability to edit and customize the project name at any time through the UI.
*   **Project Card Display:** Each project will be represented by a card on the dashboard showing:
    *   Name
    *   File Path
    *   Status (e.g., RUNNING, PAUSED, ERROR)
    *   Last Snapshot Time
    *   Pending Changes Count
    *   Current Git Branch
    *   Remote Badges (e.g., Forgejo, GitHub)
*   **Multi-Project Support:** The dashboard will support managing an unlimited number of projects.
*   **Bulk Actions:** A "Gaming Mode" or similar feature to pause all active projects at once.
*   **Import/Export:** Functionality to import and export the application's configuration (list of projects and their settings) as a JSON file.

### 2.2. Auto-Snapshot Engine

*   **File System Monitoring:** Uses `watchdog` to monitor file system events for changes within project directories.
*   **Debounced Commits:** A debounce mechanism will be used to trigger snapshots. After a change is detected, the tool will wait for a calm period before creating a snapshot.
*   **Snapshot Command:** Automatically executes `git add -A && git commit -m "auto: {timestamp}"`. The tool will avoid creating empty commits if there are no changes.
*   **Interval Control:**
    *   A global default snapshot interval (e.g., 15 seconds).
    *   Each project can override the global default with its own specific interval.
    *   Intervals have configurable minimum and maximum limits (e.g., 5s to 300s).
    *   Changes to the interval via the UI will take effect immediately.

### 2.3. Branching & Push Strategy

*   **Default Branch:** The default branch for new projects is `main`.
*   **Autosnap Branch:** The UI will allow users to select a specific branch for auto-snapshots (e.g., `autosnap`). This keeps the `main` branch clean for manual, curated commits.
*   **Manual Merge:** A button in the UI to manually merge the `autosnap` branch into the `main` branch.
*   **Push Modes:**
    *   **Forgejo-Only (Recommended):** Automatically pushes snapshots to the configured Forgejo remote.
    *   **No Push (Local History):** Snapshots are only committed locally.
    *   **Dual Remote (Advanced):** An advanced, hidden option to push to two remotes.

### 2.4. History, Restore & Manual Actions

*   **History Timeline:** The UI will feature a log timeline for each project, showing the history of snapshots.
*   **Preview & Restore:** Users can select any commit/file from the history to either preview it or restore it. Restoring a file will create a *new* commit with the restored content to maintain a linear and non-destructive history.
*   **Manual Snapshot:** A button to trigger a manual snapshot at any time, with an option to provide a custom commit message.

### 2.5. Exclusions & Retention

*   **Custom Ignores:** The UI will allow users to add custom glob patterns to ignore specific files or folders.
*   **Ignore Templates:** One-click buttons to apply pre-defined `.gitignore` templates for common project types (e.g., Node.js, Python, Laravel, Android).
*   **Default Excludes:** Heavy, common folders like `node_modules`, `dist`, `build`, `.venv`, and `__pycache__` will be excluded by default.
*   **Pruning Policy (Retention):** An optional background job to prune old snapshots:
    *   Keep the last 'N' snapshots.
    *   And/or a time-based policy (e.g., keep hourly snapshots for 7 days, daily for 30 days).

### 2.6. Health, Safety & Error Handling

*   **Commit Throttling:** Limits the rate of commits during periods of very rapid file changes.
*   **Repo Lock Detection:** Detects if a git operation is already in progress to prevent conflicts.
*   **Large File Warning:** Warns the user if very large files are added to the repository.
*   **LFS Helper:** An optional feature to help manage large files using Git LFS.
*   **Disk Space Guard:** Monitors disk space and pauses snapshots if it falls below a critical threshold.
*   **Path Access Checks:** Verifies that the application has the necessary permissions to access project paths.
*   **System Folder Protection:** Denies adding common system folders as projects by default.
*   **Least Privileges:** The application should be designed to run with the least privileges necessary.

### 2.7. Authentication & Security

*   **Credential Storage:** Forgejo Personal Access Tokens (PAT) or other credentials will be stored securely in the Windows Credential Manager.
*   **Configuration File:** Application-level configuration (like the Forgejo base URL) will be stored in a `.env` file.
*   **No Plain Text Passwords:** Raw passwords will never be stored in plain text configuration files.

### 2.8. System Integration & Notifications

*   **Startup Task:** A one-click button to "Install as Startup Task" which uses the Windows Task Scheduler to launch the application on system startup.
*   **Tray Icon:** When running as a service, an optional tray icon will be available.
*   **Graceful Shutdown:** The application will handle system shutdown/restart signals gracefully to finish any ongoing operations.
*   **Toast Notifications:** UI toasts/badges for events like:
    *   Successful snapshot/push.
    *   Push failures.
    *   Authentication expiry warnings.
    *   Merge conflicts.
*   **Windows Notifications:** Optional use of native Windows notifications for important events.

### 2.9. Forgejo & Remote Integration

*   **Remote URL:** Users can add a Forgejo remote URL to their projects.
*   **Connection Test:** A button to test the connection to the Forgejo instance's base URL (ping/health check).
*   **Latency Indicator:** A visual indicator for the latency to the Forgejo server.
*   **Conflict Handling:** If the remote branch has changed, the tool will attempt an automatic `git fetch` followed by a safe `rebase`. If this fails, it will prompt the user that a "manual pull is required."
*   **Optional Features:**
    *   Create a new repository on Forgejo directly from the dashboard.
    *   A "Copy remote URL" helper button.

### 2.10. Logging & Telemetry

*   **Per-Project Logs:** A dedicated activity log for each project showing commits, pushes, and errors.
*   **Global Log Viewer:** A central log viewer in the UI with options to filter, download, and toggle a debug mode.
*   **Telemetry (Optional):** Opt-in, local-only telemetry to track metrics like snapshot counts and durations for performance tuning. No data is uploaded externally.

### 2.11. User Experience (UX)

*   **First-Run Wizard:** A setup wizard on the first launch to configure:
    *   Forgejo URL.
    *   Default snapshot interval.
    *   Default ignore patterns.
    *   Default branching mode.
    *   Guide to add the first project.
*   **Help Page:** A simple "How it works" page explaining the core concepts and safe defaults.
*   **Context Menu:** Right-clicking on a project card provides shortcuts:
    *   Open in Explorer
    *   Open Git Log
    *   Open Terminal
*   **Quick Filters:** UI controls to quickly filter the project list (e.g., RUNNING, PAUSED, ERROR).

### 2.12. Backup & Recovery

*   **Disaster Recovery:** An optional feature to "mirror the snapshots folder to a NAS" by creating non-git, rotated ZIP archives.

---

## 3. User Flow (Simplified Explanation)

1.  **Open the Dashboard:** The user opens the web dashboard in their browser.
2.  **Add a New Project:** Click "Add Project," select a folder from the Windows file manager. The project appears on the dashboard.
3.  **Auto-Snapshot Begins:** The tool automatically initializes a git repository (if needed) and starts taking snapshots every X seconds (e.g., 15s) in the background. A snapshot is a saved, safe version of the code.
4.  **Configure Settings:** Each project card has settings to change the snapshot interval, decide whether to push to Forgejo, and manage the ignore list.
5.  **View History / Restore:** A "History" button for each project shows a complete timeline of snapshots. The user can select any snapshot to restore that version.
6.  **Manage Multiple Projects:** All projects are visible in one place. Each can be paused or resumed independently and have its own settings.
7.  **Always Running:** The tool starts automatically with Windows.
8.  **Forgejo Integration:** If a Forgejo URL is set, snapshots can be automatically pushed. If not, the history is kept purely local.

---
