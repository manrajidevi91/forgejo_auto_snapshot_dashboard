# 📄 Final PRD — Forgejo Auto-Snapshot Dashboard

## 0) Product Summary

* **Name:** Forgejo Auto-Snapshot Dashboard
* **Goal:** Select any local folder → auto-version via Git commits at intervals (debounced by FS events) → optional push to Forgejo → show history, restore, retention pruning, and upstream sync via webhooks.
* **Primary Server:** `https://forgejo.iticareer.com/`
* **Audience:** Solo devs & small teams on Windows (Linux/macOS later).

---

## 1) Core User Stories

1. **Add Project:** As a user, I can pick a local folder from a native OS dialog. If not a repo, the app initializes Git (+ `.gitignore` template).
2. **Autosnapshot:** The app snapshots file changes automatically every X seconds (debounced) and optionally pushes to Forgejo.
3. **Configure:** I can set per-project intervals, excludes, branch strategy, and push mode.
4. **History & Restore:** I can browse commit timeline, preview diffs/files, and restore any commit (as a new commit).
5. **Upstream Sync:** If someone else pushed, a webhook triggers an upstream check (fetch/rebase or manual prompt).
6. **Reliability:** The app runs on Windows startup in the background with clean shutdown; logs and notifications explain what happened.

---

## 2) Platforms & Dependencies

### 2.1 Runtime & Core Libraries

* **Python 3.11+**
* **Flask 3.x** (Web UI & API)
* **SQLAlchemy 2.x** (ORM) + **SQLite** (local DB)
* **alembic** (DB migrations)
* **watchdog** (file system events)
* **APScheduler** (interval scheduler; background jobs)
* **Git tooling:**

  * Use **Git CLI** via `subprocess.run` (preferred for parity with user’s Git install)
  * Optional **GitPython** 3.x for read-only convenience (status/log parsing) — not required for write ops
* **Requests / httpx** (Forgejo REST API calls)
* **keyring** (store PAT/credentials; Windows Credential Manager, macOS Keychain, SecretService on Linux)
* **python-dotenv** (app config)
* **pywin32** (Windows integration; optional)
* **plyer** or **win10toast** (Windows notifications)
* **pystray** (optional tray icon)
* **jsonschema** (validate project/app config)
* **WTForms / Flask-WTF** (forms; CSRF)

### 2.2 Frontend

* **Bootstrap 5** (UI)
* **HTMX** + **Alpine.js** (snappy interactions without SPA complexity)
* **Highlight.js** (log/diff code blocks)
* **Toast/Modal:** Bootstrap toasts + modals

### 2.3 OS Integrations

* **Open folder in Explorer/Finder/Files:**

  * Windows: `os.startfile(path)` or `subprocess.run(["explorer", path])`
  * macOS: `subprocess.run(["open", path])`
  * Linux: `subprocess.run(["xdg-open", path])`
* **Native Folder Picker (server-side):**

  * Windows/macOS/Linux: **tkinter.filedialog.askdirectory()** (launched by Flask handler; returns to UI)
  * Linux (headless fallback): **zenity** (`subprocess.run(["zenity","--file-selection","--directory"])`) if tkinter unavailable
  * Note: Because this is a *local* dashboard, invoking a native dialog on the same machine is acceptable.

### 2.4 Windows Autostart (Service Mode)

* **Task Scheduler** via `schtasks`
* Scripts: `scripts/install_startup_task.bat`, `scripts/uninstall_startup_task.bat`
* Optional: **NSSM** alternative (not required)

---

## 3) Architecture

### 3.1 High Level

* **Flask App** (Web UI + REST API)
* **Scheduler Service** (APScheduler) managing per-project snapshot jobs
* **Watch Workers** (watchdog observers per project) feeding debounce events
* **Snapshot Engine** (git add/commit/push)
* **Webhook Receiver** (`/hooks/forgejo`) verifying HMAC → enqueue upstream check
* **Retention Worker** (prune policy)
* **Log & Notification Service**

### 3.2 Process Model

* Single Python process with:

  * Flask server thread
  * APScheduler background scheduler
  * One watchdog observer per RUNNING project
* Clean shutdown hooks stop observers & scheduler gracefully.

---

## 4) Data Model (SQLite via SQLAlchemy)

### 4.1 Tables

**app\_settings**

* id (PK)
* forgejo\_base\_url (text) — default `https://forgejo.iticareer.com/`
* default\_interval\_sec (int; default 15)
* default\_branch (text; default `main`)
* default\_autosnap\_branch\_enabled (bool; default true)
* default\_push\_mode (enum: FORGEJO\_ONLY | NO\_PUSH | DUAL)
* standard\_ignores\_enabled (bool; default true)
* telemetry\_enabled (bool; default false)
* created\_at, updated\_at

**secrets**

* id (PK)
* key (text, unique)  e.g., `FORGEJO_PAT:vishwas0developers`
* stored\_via (enum: KEYRING | ENV | PLAINTEXT\_DISABLED)
* created\_at, updated\_at

> Note: PAT value is **never** stored in DB. Only a pointer (`key`) to **keyring**.

**projects**

* id (PK)
* name (text)
* path (text, absolute, unique)
* status (enum: RUNNING | PAUSED | ERROR | UPSTREAM\_CHANGED)
* branch (text; default from app\_settings)
* autosnap\_branch (text; default `autosnap` if enabled)
* use\_autosnap\_branch (bool)
* push\_mode (enum)
* interval\_sec (int; NULL = use global)
* remote\_primary (text; HTTPS URL)
* remote\_secondary (text; optional)
* last\_snapshot\_at (datetime; nullable)
* pending\_count (int; cached from `git status --porcelain`)
* created\_at, updated\_at

**project\_ignores**

* id (PK), project\_id (FK)
* pattern (text) — glob pattern

**events** (activity feed)

* id (PK), project\_id (FK; nullable for global)
* type (enum: SNAPSHOT | PUSH | ERROR | HOOK\_DELIVERY | UPSTREAM\_SYNC | RESTORE | MERGE)
* message (text)
* meta\_json (text)
* created\_at

**commits**

* id (PK), project\_id (FK)
* commit\_hash (text)
* message (text)
* author (text), authored\_at (datetime)
* pushed (bool)
* branch (text)

**webhook\_deliveries**

* id (PK), project\_id (FK; best-effort match by remote)
* event (text)
* delivery\_id (text)
* status\_code (int)
* latency\_ms (int)
* signature\_valid (bool)
* created\_at

**retention\_policies**

* id (PK), project\_id (FK; NULL=global)
* keep\_last\_n (int; nullable)
* keep\_hourly\_days (int; default 7)
* keep\_daily\_days (int; default 30)
* enabled (bool)

---

## 5) Git Operations (authoritative commands)

### 5.1 Initialization

* `git init -b main` (if repo missing)
* Write `.gitignore` from templates + user patterns
* `git config user.name "<USER>"` (project-local or global)
* `git config user.email "<EMAIL>"`

### 5.2 Status & Counts

* `git status --porcelain` → pending changes count

### 5.3 Snapshot

* `git add -A`
* **Skip empty commit**: run `git diff --cached --quiet` to detect staged changes
* `git commit -m "auto: YYYY-MM-DD HH:mm:ss"`

### 5.4 Push

* `git remote add origin <https://...>` (PAT via credential helper)
* `git push -u origin <branch>`
* Dual remote: add `origin2` → `git push origin2 <branch>`

### 5.5 Branch Strategy

* Default work on `main`
* If **use\_autosnap\_branch**:

  * `git checkout -B autosnap` (off main)
  * push autosnap upstream; keep main clean
  * Manual “Merge autosnap → main”:

    * `git checkout main && git fetch && git merge --no-ff autosnap && git push`

### 5.6 Upstream Sync

* On webhook or manual check:

  * `git fetch --all --prune`
  * **Safe mode**: attempt `git rebase origin/<current>`; on conflict → mark `UPSTREAM_CHANGED` and prompt manual resolve
  * Alternative: disallow autosnap on `main` if upstream moves; recommend autosnap branch

### 5.7 LFS (optional)

* Detect large files (>50MB) and prompt enabling LFS:

  * `git lfs install`
  * Track patterns: `git lfs track "*.bin"`
  * Commit updated `.gitattributes`

---

## 6) Webhooks (Forgejo)

### 6.1 Setup

* **Where:** Repo Settings → Webhooks (or Org/System defaults)
* **Target:** `http://127.0.0.1:<port>/hooks/forgejo` (or via Cloudflare Tunnel if remote)
* **Content-Type:** `application/json`
* **Secret:** random strong string (stored as app setting, not in DB plaintext)
* **Events:** at least `push`, `create` (branch/tag)

### 6.2 Verification & Headers

* Validate `X-Gitea-Signature` HMAC-SHA256 on raw body
* Read `X-Gitea-Event` for routing (push/create)
* Store delivery diagnostics to `webhook_deliveries`

### 6.3 Action on Push Event

* Map webhook repo URL to project remote (heuristic by `clone_url`)
* Enqueue job: upstream sync → `git fetch` → try rebase → update project badge/status → write `events` log

---

## 7) Background Jobs & Scheduling

### 7.1 APScheduler

* **Job types:**

  * per-project snapshot job (interval)
  * retention prune job (daily/nightly)
  * upstream check job (enqueued by webhook)
* **Constraints:** min interval 5s; max 300s
* **Live changes:** update APScheduler for that project immediately

### 7.2 Debounce Model

* **watchdog** per project (recursive observer)
* If FS event → set `dirty` flag + note `last_change_time`
* Snapshot job only commits when **dirty & quiet-period elapsed** (e.g., no FS events in last 3–5s)

---

## 8) Exclusions & .gitignore

### 8.1 Defaults

* `node_modules`, `dist`, `build`, `.venv`, `__pycache__`, `.idea`, `.vscode`, `*.log`, `*.tmp`
* Language templates (Python, Node, Laravel, Android) selectable one-click

### 8.2 User Patterns

* Add glob patterns via UI → persist in `project_ignores` and project `.gitignore` sync helper

---

## 9) Security & Secrets

* **keyring** is mandatory for PAT storage; DB only stores a reference key.
* Flask sessions: secure cookies, **Flask-WTF CSRF** enabled.
* Optional simple admin login for dashboard (username/password in `.env` or Windows auth).
* Avoid watching system dirs; permission checks on `path`.
* Log redaction for secrets.

---

## 10) Notifications

* In-app Bootstrap toasts (success/failure).
* Optional Windows notifications via **win10toast** or **plyer** (user toggle).
* Rate-limit identical notifications.

---

## 11) Logging & Telemetry

* **Python logging** to `logs/app.log` and per-project files `logs/projects/<id>.log`
* Log levels: INFO default, DEBUG via toggle
* Telemetry (local only; off by default): per-project snapshot count, avg durations; show in settings.

---

## 12) UI / UX (Pages & Controls)

1. **Dashboard (/):**

   * Global status bar (Forgejo health, latency ping)
   * **Add Project** button
   * Filters: RUNNING / PAUSED / ERROR / UPSTREAM\_CHANGED
   * **Project Card:**

     * Name (editable), Path, Status badge
     * Interval, Branch, Pending changes, Last snapshot time
     * Remote badges (Forgejo/GitHub)
     * Buttons: Run/Pause, Settings, History, Manual Snapshot, **⋮** (Explorer, Git Log, Terminal)

2. **Settings (Per Project):**

   * Interval (5–300s)
   * Branch strategy (main/autosnap)
   * Push mode (Forgejo only / No push / Dual)
   * Remotes (add/edit)
   * Ignores (patterns + template presets)
   * LFS toggle (with pattern list)
   * Danger: Remove project (keep repo), Remove + delete `.git` (confirm)

3. **History:**

   * Commit list (hash, time, message, pushed)
   * View changed files (name/size), inline diff (for text)
   * **Restore** (creates new commit)

4. **Global Settings:**

   * Forgejo URL (default pre-filled)
   * PAT user binding (stores via keyring)
   * Default interval, defaults for new projects
   * Webhook secret (display masked), test receiver
   * Install/Uninstall Startup Task
   * Export/Import config JSON

5. **Logs:**

   * App log + per-project logs
   * Download button

6. **Help:**

   * “How Auto-Snapshot works” + safe defaults

---

## 13) API (Internal REST)

### 13.1 Projects

* `POST /api/projects/add` → triggers native folder picker, returns project record
* `GET /api/projects` → list
* `PATCH /api/projects/<id>` → update config (interval, push mode, etc.)
* `POST /api/projects/<id>/run` / `pause`
* `POST /api/projects/<id>/snapshot`
* `DELETE /api/projects/<id>` (options: keep repo vs purge .git)

### 13.2 History

* `GET /api/projects/<id>/commits`
* `GET /api/projects/<id>/commit/<hash>` (files, diff)
* `POST /api/projects/<id>/restore/<hash>`

### 13.3 Webhooks

* `POST /hooks/forgejo` (verify HMAC, enqueue upstream check)

### 13.4 Settings

* `GET/POST /api/settings/app`
* `POST /api/settings/forgejo/test` (ping + `/api/v1/version`)
* `POST /api/settings/startup/install` / `startup/uninstall`

---

## 14) Retention & Pruning

* Policy strategy options per project or global:

  1. **Keep last N** commits (e.g., 500)
  2. **Tiered:** retain hourly snapshots for **7 days**, daily snapshots for **30 days**, prune older (keep weekly/monthly anchors to avoid data loss)
* Execution: nightly job; **never** remove merge bases required for history integrity; always ensure there is a recent good commit; log all prunes.

---

## 15) Error Handling & Health

* **Throttle** commits if FS events flood (max 1 commit per 2s per project).
* **Repo lock detection:** abort Git ops if `.git/index.lock` present; warn user.
* **Disk space guard:** alert if free < 1 GB; pause autosnap for affected projects.
* **Conflict handling:** on rebase conflict → mark `UPSTREAM_CHANGED`, add “Resolve” CTA.
* **Push failures:** exponential backoff; show toast; keep local commits safe.

---

## 16) Performance Targets

* Start 15+ projects without UI lag.
* Single snapshot (small change set) < 2s.
* Webhook reaction → UI badge within 3s.
* DB ops optimized via indexes on `projects.path`, `commits.project_id`.

---

## 17) Security

* HSTS on localhost optional; CSRF enabled; session cookies HttpOnly/SameSite Lax.
* PAT stored only in **keyring**; never in logs.
* Admin PIN (optional) to open settings.
* CORS disabled (local use); if remote, allowlist.

---

## 18) Installation & Environment

### 18.1 .env Keys

```
FLASK_ENV=production
FLASK_SECRET=<random>
FORGEJO_BASE_URL=https://forgejo.iticareer.com
WEBHOOK_SECRET=<random>
DEFAULT_INTERVAL_SEC=15
DEFAULT_BRANCH=main
AUTOSNAP_ENABLED=true
PUSH_MODE=FORGEJO_ONLY
```

### 18.2 Requirements (pin)

```
Flask==3.0.3
SQLAlchemy==2.0.35
alembic==1.13.2
watchdog==4.0.2
APScheduler==3.10.4
python-dotenv==1.0.1
requests==2.32.3
keyring==25.3.0
pywin32==306; platform_system=="Windows"
plyer==2.1.0
win10toast==0.9; platform_system=="Windows"
gitpython==3.1.43
jsonschema==4.23.0
WTForms==3.1.2
Flask-WTF==1.2.1
```

### 18.3 System Prereqs

* **Git** installed and on PATH
* **Windows 10+**
* Optional Linux/macOS later (swap pywin32, use systemd instead of Task Scheduler)

---

## 19) Forgejo REST API Usage (built-in)

* **Create PAT (if needed):** `POST /api/v1/users/{user}/tokens` (basic auth)
* **Create repo:** `POST /api/v1/user/repos`
* **Get repo info:** `GET /api/v1/repos/{owner}/{repo}`
* **Health/version check:** `GET /api/v1/version`
* PAT always sent as: `Authorization: token <PAT>`

---

## 20) QA & Testing

### 20.1 Unit

* `utils.git_ops`: init/status/commit/push; diff parse
* `services.snapshot_engine`: debounce, empty commit guard
* `hooks`: signature verification
* DB migrations

### 20.2 Integration

* Add project → init → commit → push → webhook → rebase path
* Retention prune simulation
* Windows startup task create/remove

### 20.3 Manual

* Conflicts (two writers)
* Large files (prompt LFS)
* Disk full scenario
* Dual remote behavior

---

## 21) Milestones

1. **M1 — Core CRUD + Snapshot (Local):**

   * Add Project (native picker), init Git, interval commit, ignores, history view

2. **M2 — Push + Webhooks:**

   * Remote config, HTTPS push (PAT in keyring), webhook receiver & upstream check

3. **M3 — Retention + Restore:**

   * Restore as new commit, pruning policy, logs viewer, notifications

4. **M4 — Windows Service + Polish:**

   * Startup task scripts, tray icon (optional), help page, import/export JSON

---

## 22) Done Criteria

* Add/Run projects with interval commits & debounced FS events
* Push succeeds with PAT stored in keyring
* Webhook sets **UPSTREAM\_CHANGED** on remote push, safe rebase attempted
* History/Restore usable; retention active; logs readable
* Starts on Windows boot; graceful shutdown; no secrets in logs

---

## 23) Risks & Mitigations

* **Browser can’t read local paths** → use server-side native picker (tkinter/zenity).
* **Credential prompts** → require keyring + Git credential manager where needed.
* **File locks/AV delays** → add retries with backoff.
* **Webhook exposure** → bind to localhost by default; if remote, use tunnel with ACL.

---

## 24) Developer Notes (Quick How)

* Open folder in OS: platform-switch with `os.startfile` / `open` / `xdg-open`.
* Open terminal at path:

  * Windows: `subprocess.run(["cmd","/K","start","cmd","/K", f"cd /d {path}"])`
  * macOS: `open -a Terminal {path}`
  * Linux: try `gnome-terminal --working-directory=...` (best-effort).
* Manual merge button: run `git merge autosnap` on `main` with confirmation/toast.
* Debounce: maintain `last_event_ts`; commit only if `(now - last_event_ts) >= quiet_secs`.