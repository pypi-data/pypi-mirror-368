/**
 * Configuration management JavaScript for Stata-MCP web UI
 * Provides client-side validation, AJAX interactions, and user feedback
 */

class ConfigManager {
    constructor() {
        this.form = document.getElementById('configForm');
        this.stataCliInput = document.getElementById('stata_cli');
        this.outputPathInput = document.getElementById('output_base_path');
        this.llmTypeSelect = document.getElementById('llm_type');
        this.ollamaModelInput = document.getElementById('ollama_model');
        this.ollamaUrlInput = document.getElementById('ollama_url');
        this.openaiModelInput = document.getElementById('openai_model');
        this.openaiUrlInput = document.getElementById('openai_url');
        this.openaiKeyInput = document.getElementById('openai_key');
        this.importFileInput = document.getElementById('importFile');
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupValidation();
    }

    bindEvents() {
        // Form submission
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Real-time validation
        this.stataCliInput.addEventListener('blur', () => this.validateField('stata.stata_cli'));
        this.stataCliInput.addEventListener('input', () => this.clearValidation('stata.stata_cli'));
        
        this.outputPathInput.addEventListener('blur', () => this.validateField('stata-mcp.output_base_path'));
        this.outputPathInput.addEventListener('input', () => this.clearValidation('stata-mcp.output_base_path'));
        
        // LLM validation
        this.llmTypeSelect.addEventListener('change', () => this.validateField('llm.LLM_TYPE'));
        this.ollamaModelInput.addEventListener('blur', () => this.validateField('llm.ollama.MODEL'));
        this.ollamaModelInput.addEventListener('input', () => this.clearValidation('llm.ollama.MODEL'));
        this.ollamaUrlInput.addEventListener('blur', () => this.validateField('llm.ollama.BASE_URL'));
        this.ollamaUrlInput.addEventListener('input', () => this.clearValidation('llm.ollama.BASE_URL'));
        this.openaiModelInput.addEventListener('blur', () => this.validateField('llm.openai.MODEL'));
        this.openaiModelInput.addEventListener('input', () => this.clearValidation('llm.openai.MODEL'));
        this.openaiUrlInput.addEventListener('blur', () => this.validateField('llm.openai.BASE_URL'));
        this.openaiUrlInput.addEventListener('input', () => this.clearValidation('llm.openai.BASE_URL'));
        this.openaiKeyInput.addEventListener('blur', () => this.validateField('llm.openai.API_KEY'));
        this.openaiKeyInput.addEventListener('input', () => this.clearValidation('llm.openai.API_KEY'));
        
        // Help buttons
        document.querySelectorAll('.help-btn').forEach(btn => {
            btn.addEventListener('click', this.toggleHelp.bind(this));
        });
        
        // Import file
        this.importFileInput.addEventListener('change', this.handleImport.bind(this));
    }

    setupValidation() {
        // Add loading states
        this.addLoadingStyles();
    }

    async validateField(fieldName) {
        const input = document.getElementById(fieldName.replace(/\./g, '_'));
        let value = '';
        
        if (input) {
            value = input.value.trim();
        }
        
        // Skip validation for hidden LLM sections
        if (fieldName.startsWith('llm.ollama') && this.llmTypeSelect.value !== 'ollama') {
            return;
        }
        if (fieldName.startsWith('llm.openai') && this.llmTypeSelect.value !== 'openai') {
            return;
        }
        
        this.showLoading(fieldName);

        try {
            const payload = this.buildValidationPayload();
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            const sections = fieldName.split('.');
            let result = data;
            
            // Navigate nested structure
            for (let section of sections) {
                if (result && result[section]) {
                    result = result[section];
                } else {
                    result = null;
                    break;
                }
            }
            
            if (result && result.valid !== undefined) {
                if (result.valid) {
                    this.showValidation(fieldName, true, 'Valid');
                } else {
                    this.showValidation(fieldName, false, result.error, result.suggestion);
                }
            } else {
                this.showValidation(fieldName, false, 'Validation error');
            }
        } catch (error) {
            this.showValidation(fieldName, false, 'Validation failed: ' + error.message);
        } finally {
            this.hideLoading(fieldName);
        }
    }

    buildValidationPayload() {
        return {
            stata: {
                stata_cli: this.stataCliInput.value.trim()
            },
            'stata-mcp': {
                output_base_path: this.outputPathInput.value.trim()
            },
            llm: {
                LLM_TYPE: this.llmTypeSelect.value,
                ollama: {
                    MODEL: this.ollamaModelInput.value.trim(),
                    BASE_URL: this.ollamaUrlInput.value.trim()
                },
                openai: {
                    MODEL: this.openaiModelInput.value.trim(),
                    BASE_URL: this.openaiUrlInput.value.trim(),
                    API_KEY: this.openaiKeyInput.value.trim()
                }
            }
        };
    }

    showValidation(fieldName, isValid, message, suggestion = null) {
        const container = document.getElementById(`${fieldName}_validation`);
        const input = document.getElementById(fieldName.replace(/\./g, '_'));
        
        container.className = `validation-message ${isValid ? 'success' : 'error'}`;
        
        let html = message;
        if (suggestion) {
            html += ` <br><strong>Suggestion:</strong> ${suggestion}`;
        }
        
        container.innerHTML = html;
        
        // Add visual feedback to input
        if (isValid) {
            input.style.borderColor = '#4caf50';
            input.classList.add('valid');
            input.classList.remove('invalid');
        } else {
            input.style.borderColor = '#f44336';
            input.classList.add('invalid');
            input.classList.remove('valid');
        }
    }

    clearValidation(fieldName) {
        const container = document.getElementById(`${fieldName}_validation`);
        const input = document.getElementById(fieldName.replace(/\./g, '_'));
        
        container.innerHTML = '';
        container.className = 'validation-message';
        if (input) {
            input.style.borderColor = '#e0e0e0';
            input.classList.remove('valid', 'invalid');
        }
    }

    showLoading(fieldName) {
        const container = document.getElementById(`${fieldName}_validation`);
        container.innerHTML = 'Validating...';
        container.className = 'validation-message';
    }

    hideLoading(fieldName) {
        // Loading is replaced by validation result
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        // Validate all fields before submission
        const validations = [
            this.validateField('stata.stata_cli'),
            this.validateField('stata-mcp.output_base_path'),
            this.validateField('llm.LLM_TYPE'),
            this.validateField('llm.ollama.MODEL'),
            this.validateField('llm.ollama.BASE_URL'),
            this.validateField('llm.openai.MODEL'),
            this.validateField('llm.openai.BASE_URL'),
            this.validateField('llm.openai.API_KEY')
        ];
        
        await Promise.all(validations);

        // Check if all validations passed
        const validationMessages = document.querySelectorAll('.validation-message');
        const hasErrors = Array.from(validationMessages).some(v => v.classList.contains('error'));
        
        if (hasErrors) {
            this.showToast('Please fix all validation errors', 'error');
            return;
        }

        // If no errors, submit the form
        this.form.submit();
    }

    toggleHelp(event) {
        const button = event.target;
        const formGroup = button.closest('.form-group');
        const helpDiv = formGroup.querySelector('.field-help');
        
        if (helpDiv) {
            helpDiv.classList.toggle('active');
        }
    }

    showStataHelp() {
        const helpDiv = document.querySelector('#stata_cli').closest('.form-group').querySelector('.field-help');
        helpDiv.classList.toggle('active');
    }

    async browseDirectory() {
        // This would ideally open a directory picker, but for now we'll just focus the input
        this.outputPathInput.focus();
        this.showToast('Please enter the full path to your desired output directory', 'info');
    }

    async exportConfig() {
        try {
            const response = await fetch('/api/export');
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'stata-mcp-config.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                this.showToast('Configuration exported successfully', 'success');
            }
        } catch (error) {
            this.showToast('Failed to export configuration', 'error');
        }
    }

    async importConfig() {
        this.importFileInput.click();
    }

    async handleImport(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.json')) {
            this.showToast('Please select a JSON file', 'error');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/import', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Configuration imported successfully', 'success');
                // Reload page to show new configuration
                setTimeout(() => window.location.reload(), 1000);
            } else {
                if (data.errors) {
                    const errorMessages = Object.values(data.errors).join('\n');
                    this.showToast(`Import failed:\n${errorMessages}`, 'error');
                } else {
                    this.showToast(data.error || 'Import failed', 'error');
                }
            }
        } catch (error) {
            this.showToast('Failed to import configuration', 'error');
        }
    }

    async resetConfig() {
        if (!confirm('Are you sure you want to reset to default configuration? This will create a backup of your current settings.')) {
            return;
        }

        try {
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Configuration reset to defaults', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showToast(data.error || 'Failed to reset configuration', 'error');
            }
        } catch (error) {
            this.showToast('Failed to reset configuration', 'error');
        }
    }

    showToast(message, type = 'info') {
        // Remove existing toasts
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${this.getIconForType(type)}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close">×</button>
        `;

        document.body.appendChild(toast);

        // Add styles
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            ...this.getStylesForType(type)
        });

        // Auto-close after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
    }

    getIconForType(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    getStylesForType(type) {
        const styles = {
            success: { backgroundColor: '#28a745' },
            error: { backgroundColor: '#dc3545' },
            warning: { backgroundColor: '#ffc107', color: '#212529' },
            info: { backgroundColor: '#17a2b8' }
        };
        return styles[type] || styles.info;
    }

    addLoadingStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .input-loading {
                position: relative;
            }
            .input-loading::after {
                content: '';
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                width: 16px;
                height: 16px;
                border: 2px solid #e0e0e0;
                border-top: 2px solid #007bff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: translateY(-50%) rotate(0deg); }
                100% { transform: translateY(-50%) rotate(360deg); }
            }
            .toast-close {
                background: none;
                border: none;
                color: inherit;
                font-size: 18px;
                cursor: pointer;
                margin-left: 10px;
            }
        `;
        document.head.appendChild(style);
    }
}

function toggleLLMSections() {
    const llmType = document.getElementById('llm_type').value;
    const ollamaSection = document.getElementById('ollama-section');
    const openaiSection = document.getElementById('openai-section');
    
    if (llmType === 'ollama') {
        ollamaSection.style.display = 'block';
        openaiSection.style.display = 'none';
    } else {
        ollamaSection.style.display = 'none';
        openaiSection.style.display = 'block';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ConfigManager();
    toggleLLMSections(); // Initialize LLM sections
});

// Utility functions
function showStataHelp() {
    const configManager = new ConfigManager();
    configManager.showStataHelp();
}

function browseDirectory() {
    const configManager = new ConfigManager();
    configManager.browseDirectory();
}

function exportConfig() {
    const configManager = new ConfigManager();
    configManager.exportConfig();
}

function importConfig() {
    const configManager = new ConfigManager();
    configManager.importConfig();
}

function resetConfig() {
    const configManager = new ConfigManager();
    configManager.resetConfig();
}