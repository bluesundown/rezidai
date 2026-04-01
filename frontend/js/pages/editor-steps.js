Pages.Editor = {
    editor: null,

    async init(isNew = true) {
        this.editor = new Editor();
        await this.editor.initialize(isNew);
        this.updateHeader();
    },

    async render(isNew = true) {
        this.showPage('editor');
        await this.init(isNew);
    },

    showPage(pageName) {
        UI.showPage(pageName);
        this.renderEditor();
    },

    updateHeader() {
        UI.updateHeader(true);
    },

    renderEditor() {
        const app = document.getElementById('app');
        if (!app) return;

        app.innerHTML = `
            <div data-page="editor" style="min-height: calc(100vh - var(--header-height));">
                <div class="container" style="padding-top: var(--spacing-3xl);">
                    <div class="flex justify-between items-center mb-2xl">
                        <div>
                            <button class="btn btn-secondary btn-sm mb-lg" id="back-to-dashboard">
                                <i data-feather="arrow-left" style="width: 16px;"></i>
                                Back to Dashboard
                            </button>
                            <h1 style="margin: 0;">Create Listing</h1>
                        </div>
                        <div class="flex gap-base items-center">
                            <span class="text-gray text-sm">Step ${this.editor?.currentStep || 1} of 5</span>
                        </div>
                    </div>

                    <div class="editor-progress-container mb-2xl">
                        <div class="editor-steps-indicators flex justify-between mb-lg">
                            <div class="editor-step-indicator flex flex-col items-center gap-sm">
                                <div class="step-circle" style="width: 40px; height: 40px; border-radius: 50%; background: var(--color-indigo-600); color: white; display: flex; align-items: center; justify-content: center; font-weight: 600;">1</div>
                                <span class="text-sm">Basic Info</span>
                            </div>
                            <div class="editor-step-indicator flex flex-col items-center gap-sm">
                                <div class="step-circle" style="width: 40px; height: 40px; border-radius: 50%; background: var(--color-gray-200); color: var(--color-gray-500); display: flex; align-items: center; justify-content: center; font-weight: 600;">2</div>
                                <span class="text-sm">Details</span>
                            </div>
                            <div class="editor-step-indicator flex flex-col items-center gap-sm">
                                <div class="step-circle" style="width: 40px; height: 40px; border-radius: 50%; background: var(--color-gray-200); color: var(--color-gray-500); display: flex; align-items: center; justify-content: center; font-weight: 600;">3</div>
                                <span class="text-sm">Photos</span>
                            </div>
                            <div class="editor-step-indicator flex flex-col items-center gap-sm">
                                <div class="step-circle" style="width: 40px; height: 40px; border-radius: 50%; background: var(--color-gray-200); color: var(--color-gray-500); display: flex; align-items: center; justify-content: center; font-weight: 600;">4</div>
                                <span class="text-sm">Description</span>
                            </div>
                            <div class="editor-step-indicator flex flex-col items-center gap-sm">
                                <div class="step-circle" style="width: 40px; height: 40px; border-radius: 50%; background: var(--color-gray-200); color: var(--color-gray-500); display: flex; align-items: center; justify-content: center; font-weight: 600;">5</div>
                                <span class="text-sm">Review</span>
                            </div>
                        </div>
                        <div class="progress-bar" style="height: 4px; background: var(--color-gray-200); border-radius: var(--radius-full);">
                            <div class="progress-bar-fill" id="editor-progress" style="height: 100%; background: var(--color-indigo-600); border-radius: var(--radius-full); transition: width var(--transition-slow);"></div>
                        </div>
                    </div>

                    <div class="card" style="max-width: 800px; margin: 0 auto;">
                        <div id="editor-steps-container" style="padding: var(--spacing-2xl);">
                            <div class="spinner" style="margin: var(--spacing-3xl) auto;"></div>
                        </div>

                        <div class="card-footer" style="display: flex; justify-content: space-between;">
                            <button class="btn btn-secondary" id="prev-step">
                                <i data-feather="arrow-left" style="width: 16px;"></i>
                                Previous
                            </button>
                            <button class="btn btn-primary" id="next-step">
                                Next
                                <i data-feather="arrow-right" style="width: 16px;"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.attachEditorEvents();
        feather.replace();
    },

    attachEditorEvents() {
        document.getElementById('back-to-dashboard')?.addEventListener('click', () => {
            if (confirm('Are you sure you want to leave? Unsaved changes will be lost.')) {
                UI.navigate(ROUTES.DASHBOARD);
            }
        });

        document.getElementById('prev-step')?.addEventListener('click', () => {
            this.editor?.previousStep();
        });

        document.getElementById('next-step')?.addEventListener('click', async () => {
            await this.editor?.nextStep();
        });

        const generateBtn = document.getElementById('generate-description');
        generateBtn?.addEventListener('click', async () => {
            await this.editor?.generateDescription();
        });

        const step1Inputs = ['step1-title', 'step1-type', 'step1-transaction', 'step1-price', 'step1-address', 'step1-city', 'step1-state', 'step1-zip'];
        step1Inputs.forEach(id => {
            const el = document.getElementById(id);
            el?.addEventListener('input', (e) => {
                const field = this.getFieldFromId(id);
                this.editor?.data.basic[field] = e.target.value;
            });
        });

        const step2Inputs = ['step2-bedrooms', 'step2-bathrooms', 'step2-sqft', 'step2-year', 'step2-description'];
        step2Inputs.forEach(id => {
            const el = document.getElementById(id);
            el?.addEventListener('input', (e) => {
                const field = this.getFieldFromId(id);
                this.editor?.data.details[field] = e.target.value;
            });
        });

        document.getElementById('step4-tone')?.addEventListener('change', (e) => {
            this.editor?.data.description.tone = e.target.value;
        });

        document.getElementById('step4-focus')?.addEventListener('change', (e) => {
            this.editor?.data.description.focus = e.target.value;
        });

        const descriptionTextarea = document.getElementById('step4-description');
        descriptionTextarea?.addEventListener('input', (e) => {
            this.editor?.data.description.text = e.target.value;
        });
    },

    getFieldFromId(id) {
        const map = {
            'step1-title': 'title',
            'step1-type': 'property_type',
            'step1-transaction': 'transaction_type',
            'step1-price': 'price',
            'step1-address': 'address',
            'step1-city': 'city',
            'step1-state': 'state',
            'step1-zip': 'postal_code',
            'step2-bedrooms': 'bedrooms',
            'step2-bathrooms': 'bathrooms',
            'step2-sqft': 'square_feet',
            'step2-year': 'year_built',
            'step2-description': 'description'
        };
        return map[id];
    }
};
