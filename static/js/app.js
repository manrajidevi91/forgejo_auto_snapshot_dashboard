document.addEventListener('DOMContentLoaded', () => {
    const addProjectBtn = document.getElementById('add-project-btn');
    const projectsList = document.getElementById('projects-list');
    const folderPicker = document.getElementById('folder-picker');
    let projectCardTemplate = '';

    // Pre-fetch the template for rendering cards
    fetch('/api/project_card_template')
        .then(response => response.text())
        .then(template => {
            projectCardTemplate = template;
        });

    // Listener for the main "Add Project" button
    addProjectBtn.addEventListener('click', () => {
        folderPicker.click();
    });

    folderPicker.addEventListener('change', async (event) => {
        const files = event.target.files;
        if (files.length > 0) {
            // The path of the first file will represent the directory
            // Note: webkitRelativePath is non-standard but widely supported for directory uploads.
            const firstFile = files[0];
            const relativePath = firstFile.webkitRelativePath;
            const folderPath = firstFile.path.substring(0, firstFile.path.length - relativePath.length - 1);

            if (folderPath) {
                try {
                    console.log('Selected folder:', folderPath);
                    const response = await fetch('/api/add_project', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: folderPath }),
                    });
                    const result = await response.json();

                    if (response.ok && result.success) {
                        console.log('Project added successfully:', result.project);
                        appendProjectCard(result.project);
                    } else {
                        console.error('Failed to add project:', result.message);
                        alert('Failed to add project: ' + result.message);
                    }
                } catch (error) {
                    console.error('Error during project addition:', error);
                    alert('An error occurred: ' + error.message);
                }
            } else {
                console.warn('Could not determine folder path.');
            }
        }
    });

    function appendProjectCard(project) {
        if (!projectsList) return;
        const renderedCard = Mustache.render(projectCardTemplate, { project: project });
        projectsList.insertAdjacentHTML('beforeend', renderedCard);
    }

    async function loadProjects() {
        if (!projectsList) return;
        try {
            const response = await fetch('/api/projects');
            const projects = await response.json();
            projectsList.innerHTML = '';

            if (!projectCardTemplate) {
                const templateResponse = await fetch('/api/project_card_template');
                projectCardTemplate = await templateResponse.text();
            }

            projects.forEach(project => {
                appendProjectCard(project);
            });

        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }



    // Initial load of projects
    loadProjects();
});