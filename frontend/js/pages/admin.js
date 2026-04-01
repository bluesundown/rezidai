Pages.Admin = {
    async init() {
        this.bindEvents();
        await this.loadConfig();
        this.updateHeader();
    },

    async render() {
        this.showPage('admin');
        await this.init();
    },

    showPage(pageName) {
        UI.showPage(pageName);
        this.renderAdmin();
    },

    updateHeader() {
        UI.updateHeader(true);
    },

    bindEvents() {
        document.getElementById('back-to-dashboard')?.addEventListener('click', () => {
            UI.navigate(ROUTES.DASHBOARD);
        });

        document.getElementById('logout-btn')?.addEventListener('click', () => {
            Auth.logout();
        });
    },

    async loadConfig() {
        try {
            const config = await api.getAdminConfig();
            this.renderConfig(config);
        } catch (error) {
            UI.showError('Failed to load config: ' + error.message);
        }
    },

    renderAdmin() {
        const app = document.getElementById('app');
        if (!app) return;

        app.innerHTML = `
            <div data-page="admin" style="padding: var(--spacing-3xl) 0;">
                <div class="container">
                    <div class="flex justify-between items-center mb-2xl">
                        <div>
                            <button class="btn btn-secondary btn-sm mb-lg" id="back-to-dashboard">
                                <i data-feather="arrow-left" style="width: 16px;"></i>
                                Back to Dashboard
                            </button>
                            <h1 style="margin: 0;">Admin Panel</h1>
                        </div>
                        <div class="flex gap-base">
                            <button class="btn btn-primary" id="save-config">
                                <i data-feather="save"></i>
                                Save Changes
                            </button>
                        </div>
                    </div>

                    <div class="grid grid-cols-2" style="gap: var(--spacing-2xl);">
                        <div>
                            <h2 class="mb-lg">API Configuration</h2>
                            <div id="config-container" class="space-y-lg">
                            </div>
                        </div>

                        <div>
                            <h2 class="mb-lg">AI Filters</h2>
                            <div class="card mb-lg">
                                <div class="flex justify-between items-center mb-lg">
                                    <h3 class="m-0">Available Filters</h3>
                                    <button class="btn btn-secondary btn-sm" id="add-filter">
                                        <i data-feather="plus" style="width: 16px;"></i>
                                        Add Filter
                                    </button>
                                </div>
                                <div id="filters-list">
                                    <div class="spinner" style="margin: var(--spacing-xl) auto;"></div>
                                </div>
                            </div>

                            <h3 class="mb-lg">Mock Services</h3>
                            <div class="card">
                                <div class="form-group">
                                    <label>
                                        <input type="checkbox" id="mock-enabled">
                                        Enable Mock Services
                                    </label>
                                    <p class="help-text">When enabled, external APIs are replaced with mock responses for testing.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.attachAdminEvents();
        feather.replace();
    },

    attachAdminEvents() {
        document.getElementById('save-config')?.addEventListener('click', async () => {
            await this.saveConfig();
        });

        document.getElementById('add-filter')?.addEventListener('click', () => {
            this.addFilter();
        });
    },

    renderConfig(config) {
        const container = document.getElementById('config-container');
        if (!container) return;

        container.innerHTML = Object.entries(config.config_keys || {}).map(([key, value]) => `
            <div class="card">
                <h3 class="mb-lg">${value.name}</h3>
                <div class="form-group">
                    <label>API Key</label>
                    <input type="password" class="input" id="api-key-${key}" value="${value.configured ? '••••••••' : ''}" placeholder="Enter API key">
                </div>
                <div class="form-group">
                    <label>Endpoint</label>
                    <input type="text" class="input" value="${value.endpoint || 'N/A'}" disabled>
                </div>
                <div class="flex items-center gap-base">
                    <i data-feather="${value.configured ? 'check-circle' : 'x-circle'}" style="color: ${value.configured ? 'var(--color-green-500)' : 'var(--color-red-500)'};"></i>
                    <span class="text-sm">${value.configured ? 'Configured' : 'Not configured'}</span>
                </div>
            </div>
        `).join('');

        feather.replace();
    },

    async saveConfig() {
        const keys = ['qwen', 'google_maps', 'stripe'];
        
        for (const key of keys) {
            const input = document.getElementById(`api-key-${key}`);
            if (input && input.value) {
                try {
                    await api.updateAPIKey(key, input.value);
                } catch (error) {
                    UI.showError(`Failed to update ${key}: ${error.message}`);
                    return;
                }
            }
        }

        const mockEnabled = document.getElementById('mock-enabled')?.checked;
        if (mockEnabled !== undefined) {
            try {
                await api.toggleMockServices(mockEnabled);
            } catch (error) {
                UI.showError(`Failed to update mock services: ${error.message}`);
                return;
            }
        }

        UI.showSuccess('Configuration saved successfully!');
    },

    async addFilter() {
        const name = prompt('Filter name:');
        if (!name) return;

        const slug = name.toLowerCase().replace(/[^a-z0-9]/g, '-');
        const tone = prompt('Tone (professional, friendly, luxury, modern):', 'professional');
        const focus = prompt('Focus:', 'general');

        try {
            await api.createFilter({
                name,
                slug,
                tone: tone || 'professional',
                focus: focus || 'general',
                is_active: true
            });

            UI.showSuccess('Filter created successfully!');
        } catch (error) {
            UI.showError('Failed to create filter: ' + error.message);
        }
    }
};
