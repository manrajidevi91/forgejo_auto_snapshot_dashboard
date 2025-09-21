document.addEventListener('DOMContentLoaded', () => {
    const projectsList = document.getElementById('projects-list');
    
    // Modals
    const projectActionsModalEl = document.getElementById('projectActionsModal');
    const projectSettingsModalEl = document.getElementById('projectSettingsModal');

    if (!projectActionsModalEl || !projectSettingsModalEl) {
        console.error('Required modals not found!');
        return;
    }

    const projectActionsModal = new bootstrap.Modal(projectActionsModalEl);
    const projectSettingsModal = new bootstrap.Modal(projectSettingsModalEl);

    // Action Modal Elements
    const actionsProjectName = document.getElementById('actions-project-name');
    const actionsProjectIdInput = document.getElementById('actions-project-id');

    // Settings Modal Elements
    const settingsProjectIdInput = document.getElementById('settings-project-id');
    const settingsProjectNameTitle = document.getElementById('settings-project-name-title');
    const settingsProjectNameInput = document.getElementById('settings-project-name');
    const settingsSnapshotIntervalInput = document.getElementById('settings-snapshot-interval');
    const settingsSnapshotBranchInput = document.getElementById('settings-snapshot-branch');
    const settingsPushModeSelect = document.getElementById('settings-push-mode');
    const settingsForgejoUsernameContainer = document.getElementById('forgejo-username-container');
    const settingsForgejoUsernameInput = document.getElementById('settings-forgejo-username');
    const saveSettingsBtn = document.getElementById('save-project-settings-btn');
    const remotesListDiv = document.getElementById('remotes-list');
    const addRemoteBtn = document.getElementById('add-remote-btn');
    const newRemoteNameInput = document.getElementById('new-remote-name');
    const newRemoteUrlInput = document.getElementById('new-remote-url');

    let tempRemotes = [];

    // --- Event Listeners ---

    if (projectsList) {
        projectsList.addEventListener('click', (event) => {
            if (event.target.closest('.edit-project-btn')) handleEditButtonClick(event.target.closest('.edit-project-btn'));
            if (event.target.closest('.delete-project-btn')) handleDeleteButtonClick(event.target.closest('.delete-project-btn'));
        });
    }

    projectActionsModalEl.addEventListener('click', (event) => {
        const projectId = actionsProjectIdInput.value;
        if (!projectId) return;
        if (event.target.classList.contains('toggle-status-btn')) handleToggleStatus(projectId);
        if (event.target.classList.contains('settings-btn')) handleSettingsClick(projectId);
    });

    if (saveSettingsBtn) saveSettingsBtn.addEventListener('click', handleSaveSettings);
    if (addRemoteBtn) addRemoteBtn.addEventListener('click', handleAddRemote);
    if (remotesListDiv) remotesListDiv.addEventListener('click', handleRemoveRemote);
    if (settingsPushModeSelect) settingsPushModeSelect.addEventListener('change', toggleForgejoUsernameVisibility);


    // --- Handler Functions ---

    function handleEditButtonClick(button) {
        const card = button.closest('.project-card');
        actionsProjectIdInput.value = card.dataset.projectId;
        actionsProjectName.textContent = card.querySelector('.project-name-display').textContent;
        projectActionsModal.show();
    }

    function handleDeleteButtonClick(button) {
        const card = button.closest('.project-card');
        const projectId = card.dataset.projectId;
        const projectName = card.querySelector('.project-name-display').textContent;
        if (confirm(`Are you sure you want to delete project "${projectName}"?`)) {
            fetch(`/api/projects/${projectId}`, { method: 'DELETE' })
                .then(res => res.json()).then(data => data.success ? card.remove() : alert('Failed to delete: ' + data.message));
        }
    }

    async function handleToggleStatus(projectId) {
        const res = await fetch(`/api/projects/${projectId}/toggle_status`, { method: 'POST' });
        const result = await res.json();
        if (result.success) {
            const card = document.querySelector(`.project-card[data-project-id="${projectId}"]`);
            if (card) card.querySelector('.project-status').textContent = result.new_status;
            projectActionsModal.hide();
        } else {
            alert('Failed to toggle status: ' + result.message);
        }
    }

    async function handleSettingsClick(projectId) {
        projectActionsModal.hide();
        const res = await fetch('/api/projects');
        const projects = await res.json();
        const project = projects.find(p => p.id === projectId);
        if (project) {
            settingsProjectIdInput.value = project.id;
            settingsProjectNameTitle.textContent = project.name;
            settingsProjectNameInput.value = project.name;
            settingsSnapshotIntervalInput.value = project.snapshot_interval || 15;
            settingsSnapshotBranchInput.value = project.snapshot_branch || 'autosnap';
            settingsPushModeSelect.value = project.push_mode || 'no_push';
            settingsForgejoUsernameInput.value = project.forgejo_username || '';
            tempRemotes = project.remotes || [];
            renderRemotes();
            toggleForgejoUsernameVisibility();
            projectSettingsModal.show();
        } else {
            alert('Could not find project details.');
        }
    }
    
    function toggleForgejoUsernameVisibility() {
        if (settingsPushModeSelect.value === 'forgejo') {
            settingsForgejoUsernameContainer.style.display = 'block';
        } else {
            settingsForgejoUsernameContainer.style.display = 'none';
        }
    }

    function renderRemotes() {
        remotesListDiv.innerHTML = '';
        tempRemotes.forEach(remote => {
            const div = document.createElement('div');
            div.className = 'd-flex justify-content-between align-items-center mb-2';
            div.innerHTML = `
                <span><strong>${remote.name}</strong>: ${remote.url}</span>
                <button type="button" class="btn btn-danger btn-sm remove-remote-btn" data-name="${remote.name}">Remove</button>
            `;
            remotesListDiv.appendChild(div);
        });
    }

    function handleAddRemote() {
        const name = newRemoteNameInput.value.trim();
        const url = newRemoteUrlInput.value.trim();
        if (name && url && !tempRemotes.some(r => r.name === name)) {
            tempRemotes.push({ name, url });
            renderRemotes();
            newRemoteNameInput.value = '';
            newRemoteUrlInput.value = '';
        } else {
            alert('Invalid or duplicate remote name.');
        }
    }

    function handleRemoveRemote(event) {
        if (event.target.classList.contains('remove-remote-btn')) {
            const nameToRemove = event.target.dataset.name;
            tempRemotes = tempRemotes.filter(r => r.name !== nameToRemove);
            renderRemotes();
        }
    }

    async function handleSaveSettings() {
        const projectId = settingsProjectIdInput.value;
        const updateData = {
            name: settingsProjectNameInput.value,
            snapshot_interval: parseInt(settingsSnapshotIntervalInput.value, 10),
            snapshot_branch: settingsSnapshotBranchInput.value,
            push_mode: settingsPushModeSelect.value,
            forgejo_username: settingsForgejoUsernameInput.value,
            remotes: tempRemotes
        };

        const res = await fetch(`/api/projects/${projectId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData),
        });
        const result = await res.json();
        if (result.success) {
            const card = document.querySelector(`.project-card[data-project-id="${projectId}"]`);
            if (card) card.querySelector('.project-name-display').textContent = updateData.name;
            projectSettingsModal.hide();
        } else {
            alert('Failed to save settings: ' + result.message);
        }
    }

    async function updatePendingChanges() {
        document.querySelectorAll('.project-card').forEach(async (card) => {
            const projectId = card.dataset.projectId;
            if (!projectId) return;
            try {
                const res = await fetch(`/api/projects/${projectId}/pending_changes`);
                const result = await res.json();
                if (result.success) {
                    const countSpan = card.querySelector('.pending-changes-count');
                    if (countSpan) countSpan.textContent = result.pending_changes;
                }
            } catch (error) {}
        });
    }

    setInterval(updatePendingChanges, 5000);
    updatePendingChanges();
});