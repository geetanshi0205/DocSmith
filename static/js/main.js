// Utility functions
function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    if (loadingText) {
        loadingText.textContent = text;
    }
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showAlert(message, type = 'info') {
    const alertsContainer = document.querySelector('.flash-messages') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-content">${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

function createAlertsContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// Tab functionality
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanels.forEach(panel => panel.classList.remove('active'));
            
            // Add active class to clicked button and corresponding panel
            button.classList.add('active');
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// File upload functionality
function initializeFileUpload() {
    const fileUploadAreas = document.querySelectorAll('.file-upload');
    
    fileUploadAreas.forEach(area => {
        // Make file upload areas clickable
        area.addEventListener('click', () => {
            const fileInput = area.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.click();
            }
        });
        
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            const fileInput = area.querySelector('input[type="file"]');
            if (fileInput && files.length > 0) {
                fileInput.files = files;
                // Show file selection immediately
                displayFileSelection(files, fileInput);
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        });
        
        // Add file input change listener for immediate display (without duplicating)
        const fileInput = area.querySelector('input[type="file"]');
        if (fileInput && !fileInput.hasAttribute('data-listener-added')) {
            fileInput.setAttribute('data-listener-added', 'true');
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    displayFileSelection(e.target.files, e.target);
                }
            });
        }
    });
}

// Form submission with AJAX
function submitFormAjax(form, options = {}) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    const method = form.method || 'POST';
    
    const defaultOptions = {
        onStart: () => showLoading(),
        onSuccess: (data) => {
            hideLoading();
            if (data.message) {
                showAlert(data.message, 'success');
            }
        },
        onError: (error) => {
            hideLoading();
            showAlert(error.message || 'An error occurred', 'error');
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    finalOptions.onStart();
    
    fetch(url, {
        method: method,
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            finalOptions.onSuccess(data);
        } else {
            finalOptions.onError(data);
        }
    })
    .catch(error => {
        finalOptions.onError({ message: error.message });
    });
}

// GitHub repository handling
function handleGitHubSubmit() {
    const form = document.getElementById('github-form');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        submitFormAjax(form, {
            onSuccess: (data) => {
                hideLoading();
                showAlert(data.message, 'success');
                
                if (data.repo_info) {
                    displayRepoInfo(data.repo_info);
                }
                
                displayUploadSuccess(data);
                enableDocumentationGeneration();
            }
        });
    });
}

// ZIP file handling
function handleZipUpload() {
    const form = document.getElementById('zip-form');
    if (!form) return;
    
    const fileInput = form.querySelector('input[type="file"]');
    if (fileInput && !fileInput.hasAttribute('data-submit-listener')) {
        fileInput.setAttribute('data-submit-listener', 'true');
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                // Auto-submit after file selection
                setTimeout(() => {
                    submitFormAjax(form, {
                        onSuccess: (data) => {
                            hideLoading();
                            showAlert(data.message, 'success');
                            displayUploadSuccess(data);
                            enableDocumentationGeneration();
                        }
                    });
                }, 500); // Small delay to show file selection first
            }
        });
    }
}

// Individual files handling
function handleFilesUpload() {
    const form = document.getElementById('files-form');
    if (!form) return;
    
    const fileInput = form.querySelector('input[type="file"]');
    if (fileInput && !fileInput.hasAttribute('data-submit-listener')) {
        fileInput.setAttribute('data-submit-listener', 'true');
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                // Auto-submit after file selection
                setTimeout(() => {
                    submitFormAjax(form, {
                        onSuccess: (data) => {
                            hideLoading();
                            showAlert(data.message, 'success');
                            displayUploadSuccess(data);
                            enableDocumentationGeneration();
                        }
                    });
                }, 500); // Small delay to show file selection first
            }
        });
    }
}

// Local path handling
function handleLocalPath() {
    const form = document.getElementById('local-path-form');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        submitFormAjax(form, {
            onSuccess: (data) => {
                hideLoading();
                showAlert(data.message, 'success');
                enableDocumentationGeneration();
            }
        });
    });
}

// Documentation generation
function handleDocumentationGeneration() {
    const form = document.getElementById('generate-docs-form');
    const generateButton = document.getElementById('generate-docs-button');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const checkedTypes = form.querySelectorAll('input[name="doc_types"]:checked');
        if (checkedTypes.length === 0) {
            showAlert('Please select at least one documentation type', 'warning');
            return;
        }
        
        submitFormAjax(form, {
            onStart: () => {
                showLoading('Generating documentation...');
                if (generateButton) {
                    generateButton.disabled = true;
                    generateButton.textContent = 'Generating...';
                }
            },
            onSuccess: (data) => {
                hideLoading();
                if (generateButton) {
                    generateButton.disabled = false;
                    generateButton.textContent = '🚀 Generate Documentation';
                }
                
                if (data.demo_mode) {
                    showAlert('Demo documentation generated! Set ANTHROPIC_API_KEY for AI-powered docs.', 'info');
                } else {
                    showAlert('Documentation generated successfully!', 'success');
                }
                
                if (data.project_summary) {
                    displayProjectSummary(data.project_summary);
                }
                
                if (data.documentation) {
                    displayDocumentation(data.documentation);
                }
            },
            onError: (error) => {
                hideLoading();
                if (generateButton) {
                    generateButton.disabled = false;
                    generateButton.textContent = '🚀 Generate Documentation';
                }
                showAlert(error.error || 'An error occurred', 'error');
            }
        });
    });
}

// Code explanation
function handleCodeExplanation() {
    const form = document.getElementById('explain-code-form');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const codeInput = form.querySelector('textarea[name="code"]');
        if (!codeInput || !codeInput.value.trim()) {
            showAlert('Please enter some code to explain', 'warning');
            return;
        }
        
        submitFormAjax(form, {
            onStart: () => showLoading('Analyzing code...'),
            onSuccess: (data) => {
                hideLoading();
                if (data.explanation) {
                    displayCodeExplanation(data.explanation);
                }
            }
        });
    });
}

// Display functions
function displayRepoInfo(repoInfo) {
    const container = document.getElementById('repo-info-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📍 Repository Information</h3>
            </div>
            <p><strong>${repoInfo.owner}/${repoInfo.repo_name}</strong></p>
            <p>Branch: <code>${repoInfo.branch}</code></p>
            ${repoInfo.last_commit ? `
                <p class="text-muted">
                    Last commit: <code>${repoInfo.last_commit.hash}</code> 
                    by ${repoInfo.last_commit.author} on ${repoInfo.last_commit.date}
                </p>
            ` : ''}
        </div>
    `;
}

function displayProjectSummary(summary) {
    const container = document.getElementById('project-summary-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Project Summary</h3>
            </div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">Files</div>
                    <div class="metric-value">${summary.total_files}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Lines</div>
                    <div class="metric-value">${summary.total_lines.toLocaleString()}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Complexity</div>
                    <div class="metric-value">${summary.estimated_complexity}</div>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">🛠️ Technologies:</label>
                <div class="tech-badges">
                    ${summary.technologies.slice(0, 6).map(tech => 
                        `<span class="tech-badge">${tech}</span>`
                    ).join('')}
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">💻 Languages:</label>
                <ul>
                    ${summary.main_languages.slice(0, 5).map(lang => 
                        `<li>${lang}</li>`
                    ).join('')}
                </ul>
            </div>
        </div>
    `;
}

function displayDocumentation(documentation) {
    const container = document.getElementById('documentation-container');
    if (!container) return;
    
    const tabIcons = {
        'architecture_overview': '🏗️ Architecture',
        'developer_guide': '👨‍💻 Developer Guide',
        'api_documentation': '🔌 API Docs'
    };
    
    const tabButtons = Object.keys(documentation).map(docType => 
        `<button class="tab-button" data-tab="${docType}">${tabIcons[docType] || docType}</button>`
    ).join('');
    
    const tabPanels = Object.entries(documentation).map(([docType, content]) => `
        <div id="${docType}" class="tab-panel">
            <div class="documentation-content">
                ${renderMarkdown(content)}
            </div>
            <div class="mt-3">
                <a href="/download/${docType}" class="btn btn-secondary">📥 Download MD</a>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📚 Generated Documentation</h3>
            </div>
            <div class="tabs">
                <div class="tab-list">
                    ${tabButtons}
                </div>
                <div class="tab-content">
                    ${tabPanels}
                </div>
            </div>
            ${Object.keys(documentation).length > 1 ? `
                <div class="text-center mt-3">
                    <a href="/download-all" class="btn btn-success">📦 Download All as ZIP</a>
                </div>
            ` : ''}
        </div>
    `;
    
    // Initialize tabs and make first one active
    initializeTabs();
    const firstButton = container.querySelector('.tab-button');
    const firstPanel = container.querySelector('.tab-panel');
    if (firstButton && firstPanel) {
        firstButton.classList.add('active');
        firstPanel.classList.add('active');
    }
}

function displayCodeExplanation(explanation) {
    const container = document.getElementById('code-explanation-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">💡 Code Explanation</h3>
            </div>
            <div class="explanation-content">
                ${renderMarkdown(explanation)}
            </div>
        </div>
    `;
}

function displayFileSelection(files, fileInput) {
    const container = document.getElementById('repo-info-container');
    if (!container) return;
    
    const isZip = fileInput.accept === '.zip';
    const isMultiple = fileInput.hasAttribute('multiple');
    
    let fileInfo = '';
    
    if (isZip && files.length > 0) {
        const file = files[0];
        fileInfo = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📦 ZIP File Selected</h3>
                </div>
                <p><strong>File:</strong> ${file.name}</p>
                <p><strong>Size:</strong> ${formatFileSize(file.size)}</p>
                <p><strong>Status:</strong> Ready to upload</p>
                <div class="mt-2">
                    <small class="text-muted">File will be uploaded automatically...</small>
                </div>
            </div>
        `;
    } else if (isMultiple && files.length > 0) {
        const fileList = Array.from(files).slice(0, 5).map(file => 
            `<li>${file.name} (${formatFileSize(file.size)})</li>`
        ).join('');
        
        const remainingCount = files.length > 5 ? files.length - 5 : 0;
        
        fileInfo = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📄 Files Selected</h3>
                </div>
                <p><strong>Count:</strong> ${files.length} files</p>
                <p><strong>Total Size:</strong> ${formatFileSize(Array.from(files).reduce((total, file) => total + file.size, 0))}</p>
                <div class="mt-2">
                    <strong>Files:</strong>
                    <ul style="margin-top: 8px; padding-left: 20px;">
                        ${fileList}
                        ${remainingCount > 0 ? `<li><em>... and ${remainingCount} more files</em></li>` : ''}
                    </ul>
                </div>
                <div class="mt-2">
                    <small class="text-muted">Files will be uploaded automatically...</small>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = fileInfo;
    
    // Enable generate button (it will be properly enabled after upload)
    const generateButton = document.getElementById('generate-docs-button');
    if (generateButton) {
        generateButton.disabled = false;
        generateButton.textContent = 'Uploading...';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function displayUploadSuccess(data) {
    const container = document.getElementById('repo-info-container');
    if (!container) return;
    
    let uploadInfo = '';
    
    if (data.upload_type === 'github') {
        uploadInfo = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">✅ Repository Uploaded</h3>
                </div>
                <p><strong>Type:</strong> GitHub Repository</p>
                <p><strong>Repository:</strong> ${data.repo_info.owner}/${data.repo_info.repo_name}</p>
                <p><strong>Branch:</strong> ${data.repo_info.branch}</p>
            </div>
        `;
    } else if (data.upload_type === 'zip') {
        uploadInfo = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">✅ ZIP File Uploaded</h3>
                </div>
                <p><strong>Type:</strong> ZIP Archive</p>
                <p><strong>File:</strong> ${data.filename}</p>
                <p><strong>Status:</strong> Extracted successfully</p>
            </div>
        `;
    } else if (data.upload_type === 'files') {
        uploadInfo = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">✅ Files Uploaded</h3>
                </div>
                <p><strong>Type:</strong> Individual Files</p>
                <p><strong>Count:</strong> ${data.files_count} files</p>
                <p><strong>Status:</strong> Upload successful</p>
            </div>
        `;
    }
    
    container.innerHTML = uploadInfo;
}

function renderMarkdown(text) {
    if (!text) return '';
    
    // Basic markdown rendering (simple implementation)
    return text
        // Headers
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        // Bold and italic
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Code blocks
        .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Lists
        .replace(/^\- (.*$)/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
        // Line breaks
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function enableDocumentationGeneration() {
    const generateButton = document.getElementById('generate-docs-button');
    if (generateButton) {
        generateButton.disabled = false;
        generateButton.textContent = '🚀 Generate Documentation';
    }
}

// Radio button handling with upload form switching
function initializeRadioGroups() {
    const radioGroups = document.querySelectorAll('.radio-group');
    
    radioGroups.forEach(group => {
        const items = group.querySelectorAll('.radio-item');
        const inputs = group.querySelectorAll('input[type="radio"]');
        
        items.forEach((item, index) => {
            item.addEventListener('click', () => {
                // Remove selected class from all items
                items.forEach(i => i.classList.remove('selected'));
                
                // Add selected class to clicked item
                item.classList.add('selected');
                
                // Check the corresponding radio button
                inputs[index].checked = true;
                
                // Trigger change event to show/hide upload forms
                const changeEvent = new Event('change', { bubbles: true });
                inputs[index].dispatchEvent(changeEvent);
            });
        });
        
        // Handle direct input changes and form switching
        inputs.forEach((input, index) => {
            input.addEventListener('change', () => {
                items.forEach(i => i.classList.remove('selected'));
                if (input.checked) {
                    items[index].classList.add('selected');
                    // Show/hide upload forms based on selection
                    switchUploadForm(input.value);
                }
            });
        });
    });
}

// Switch upload forms based on radio selection
function switchUploadForm(method) {
    const uploadForms = document.querySelectorAll('.upload-form');
    
    // Hide all forms
    uploadForms.forEach(form => form.classList.add('hidden'));
    
    // Show selected form
    const targetForm = document.getElementById(`${method}-upload`);
    if (targetForm) {
        targetForm.classList.remove('hidden');
    }
    
    // Clear result UI when switching methods
    clearResultUI();
    
    // Disable generate button when switching
    disableDocumentationGeneration();
}

// Clear all result containers
function clearResultUI() {
    const containers = [
        'repo-info-container',
        'project-summary-container', 
        'documentation-container'
    ];
    
    containers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    });
    
    // Reset documentation container to initial state
    const docContainer = document.getElementById('documentation-container');
    if (docContainer) {
        docContainer.innerHTML = `
            <div class="text-center" style="padding: 60px 24px;">
                <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.6;">🤖</div>
                <h3>Ready to Generate Documentation</h3>
                <p class="text-muted">Upload your codebase to get started</p>
            </div>
        `;
    }
}

// Disable generate documentation button
function disableDocumentationGeneration() {
    const generateButton = document.getElementById('generate-docs-button');
    if (generateButton) {
        generateButton.disabled = true;
        generateButton.textContent = 'Upload Codebase First';
    }
}

// Checkbox handling
function initializeCheckboxGroups() {
    const checkboxItems = document.querySelectorAll('.checkbox-item');
    
    checkboxItems.forEach(item => {
        const input = item.querySelector('input[type="checkbox"]');
        
        item.addEventListener('click', (e) => {
            if (e.target !== input) {
                input.checked = !input.checked;
            }
            
            if (input.checked) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
        
        input.addEventListener('change', () => {
            if (input.checked) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeFileUpload();
    initializeRadioGroups();
    initializeCheckboxGroups();
    
    // Initialize form handlers
    handleGitHubSubmit();
    handleZipUpload();
    handleFilesUpload();
    handleLocalPath();
    handleDocumentationGeneration();
    handleCodeExplanation();
});