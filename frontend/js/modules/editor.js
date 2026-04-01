class Editor {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.listingId = null;
        this.data = {
            basic: {},
            details: {},
            images: [],
            description: {},
            review: {}
        };
    }

    async initialize(isNew = true) {
        if (isNew) {
            this.reset();
        } else {
            const savedId = Storage.getEditorListingId();
            if (savedId) {
                this.listingId = savedId;
                this.data = Storage.getDraft(savedId);
            }
        }
        
        this.currentStep = Storage.getEditorStep();
        this.renderStep(this.currentStep);
    }

    reset() {
        this.currentStep = 1;
        this.listingId = null;
        this.data = {
            basic: {},
            details: {},
            images: [],
            description: {},
            review: {}
        };
        Storage.clearEditorState();
    }

    saveProgress() {
        if (!this.listingId) {
            return;
        }
        Storage.saveDraft(this.listingId, this.data);
        Storage.setEditorStep(this.currentStep);
    }

    async nextStep() {
        if (this.validateCurrentStep()) {
            this.saveProgress();
            if (this.currentStep < this.totalSteps) {
                this.currentStep++;
                this.renderStep(this.currentStep);
            } else {
                await this.publish();
            }
        }
    }

    async previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.renderStep(this.currentStep);
        }
    }

    goToStep(step) {
        if (step >= 1 && step <= this.totalSteps) {
            this.currentStep = step;
            this.renderStep(step);
        }
    }

    validateCurrentStep() {
        const validations = {
            1: this.validateBasicInfo.bind(this),
            2: this.validateDetails.bind(this),
            3: () => this.data.images.length > 0,
            4: () => true,
            5: this.validateReview.bind(this)
        };

        const isValid = validations[this.currentStep]();
        
        if (!isValid) {
            UI.showError('Please fill in all required fields');
        }

        return isValid;
    }

    validateBasicInfo() {
        return this.data.basic.title &&
               this.data.basic.property_type &&
               this.data.basic.transaction_type &&
               this.data.basic.address &&
               this.data.basic.city &&
               this.data.basic.state &&
               this.data.basic.postal_code &&
               this.data.basic.price;
    }

    validateDetails() {
        return this.data.details.bedrooms &&
               this.data.details.bathrooms &&
               this.data.details.square_feet;
    }

    validateReview() {
        return this.validateBasicInfo() && 
               this.validateDetails() &&
               this.data.images.length > 0;
    }

    renderStep(step) {
        Storage.setEditorStep(step);
        const container = document.getElementById('editor-steps-container');
        if (!container) return;

        const steps = [
            this.renderBasicInfoStep.bind(this),
            this.renderDetailsStep.bind(this),
            this.renderImagesStep.bind(this),
            this.renderDescriptionStep.bind(this),
            this.renderReviewStep.bind(this)
        ];

        container.innerHTML = steps[step - 1]();
        this.attachStepEventListeners();
        this.renderProgressIndicator();
    }

    renderProgressIndicator() {
        const indicator = document.getElementById('editor-progress');
        if (!indicator) return;

        const progress = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
        indicator.style.width = `${progress}%`;

        const steps = document.querySelectorAll('.editor-step-indicator');
        steps.forEach((step, index) => {
            step.classList.toggle('active', index + 1 === this.currentStep);
            step.classList.toggle('completed', index + 1 < this.currentStep);
        });
    }

    renderBasicInfoStep() {
        return `
            <div class="editor-step">
                <h2>Basic Information</h2>
                <p class="text-gray mb-xl">Start with the essentials</p>
                
                <div class="form-group">
                    <label>Listing Title *</label>
                    <input type="text" class="input" id="step1-title" placeholder="e.g., Modern Downtown Apartment" value="${this.data.basic.title || ''}">
                </div>

                <div class="grid grid-cols-2 gap-base">
                    <div class="form-group">
                        <label>Property Type *</label>
                        <select class="input select" id="step1-type">
                            <option value="">Select Type</option>
                            ${PROPERTY_TYPES.map(t => `<option value="${t.value}" ${this.data.basic.property_type === t.value ? 'selected' : ''}>${t.label}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Transaction Type *</label>
                        <select class="input select" id="step1-transaction">
                            <option value="">Select Type</option>
                            ${TRANSACTION_TYPES.map(t => `<option value="${t.value}" ${this.data.basic.transaction_type === t.value ? 'selected' : ''}>${t.label}</option>`).join('')}
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>Price *</label>
                    <div class="flex gap-base">
                        <input type="number" class="input" id="step1-price" placeholder="0" value="${this.data.basic.price || ''}">
                    </div>
                </div>

                <div class="form-group">
                    <label>Address *</label>
                    <input type="text" class="input" id="step1-address" placeholder="Street address" value="${this.data.basic.address || ''}">
                </div>

                <div class="grid grid-cols-3 gap-base">
                    <div class="form-group">
                        <label>City *</label>
                        <input type="text" class="input" id="step1-city" placeholder="City" value="${this.data.basic.city || ''}">
                    </div>
                    <div class="form-group">
                        <label>State *</label>
                        <input type="text" class="input" id="step1-state" placeholder="State" value="${this.data.basic.state || ''}">
                    </div>
                    <div class="form-group">
                        <label>Postal Code *</label>
                        <input type="text" class="input" id="step1-zip" placeholder="ZIP" value="${this.data.basic.postal_code || ''}">
                    </div>
                </div>
            </div>
        `;
    }

    renderDetailsStep() {
        return `
            <div class="editor-step">
                <h2>Property Details</h2>
                <p class="text-gray mb-xl">Add the specifics</p>

                <div class="grid grid-cols-3 gap-base">
                    <div class="form-group">
                        <label>Bedrooms *</label>
                        <input type="number" class="input" id="step2-bedrooms" min="0" value="${this.data.details.bedrooms || ''}">
                    </div>
                    <div class="form-group">
                        <label>Bathrooms *</label>
                        <input type="number" class="input" id="step2-bathrooms" min="0" step="0.5" value="${this.data.details.bathrooms || ''}">
                    </div>
                    <div class="form-group">
                        <label>Square Feet *</label>
                        <input type="number" class="input" id="step2-sqft" min="0" value="${this.data.details.square_feet || ''}">
                    </div>
                </div>

                <div class="form-group">
                    <label>Year Built</label>
                    <input type="number" class="input" id="step2-year" min="1800" max="2025" value="${this.data.details.year_built || ''}">
                </div>

                <div class="form-group">
                    <label>Description</label>
                    <textarea class="input textarea" id="step2-description" rows="4" placeholder="Add any additional details about the property...">${this.data.details.description || ''}</textarea>
                </div>

                <div class="form-group">
                    <label>Amenities</label>
                    <div class="amenities-checklist" id="step2-amenities">
                        ${['Air Conditioning', 'Heating', 'Parking', 'Elevator', 'Doorman', 'Gym', 'Pool', 'Balcony', 'Dishwasher', 'Washer/Dryer']
                            .map(amenity => `
                                <label class="flex items-center gap-base" style="margin-bottom: 8px;">
                                    <input type="checkbox" value="${amenity}" ${this.data.details.amenities?.includes(amenity) ? 'checked' : ''}>
                                    <span>${amenity}</span>
                                </label>
                            `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderImagesStep() {
        return `
            <div class="editor-step">
                <h2>Upload Photos</h2>
                <p class="text-gray mb-xl">Show off your property (up to 10 images)</p>

                <div class="upload-area" id="upload-area" style="border: 2px dashed var(--color-gray-300); border-radius: var(--radius-lg); padding: var(--spacing-3xl); text-align: center; cursor: pointer; transition: all var(--transition-default);">
                    <i data-feather="upload-cloud" style="width: 48px; height: 48px; color: var(--color-gray-400); margin-bottom: var(--spacing-lg);"></i>
                    <p><strong>Click to upload</strong> or drag and drop</p>
                    <p class="text-gray text-sm">JPG, PNG, WEBP up to 20MB</p>
                    <input type="file" id="file-input" multiple accept="image/*" style="display: none;">
                </div>

                <div class="grid grid-auto gap-base mt-xl" id="images-grid">
                    ${this.data.images.map((img, index) => `
                        <div class="image-preview" style="position: relative;">
                            <img src="${img.thumbnail_path || img.file_path}" style="width: 100%; border-radius: var(--radius-base);">
                            <button class="remove-image" data-index="${index}" style="position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.5); color: white; border: none; border-radius: 50%; width: 32px; height: 32px; cursor: pointer;">&times;</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderDescriptionStep() {
        return `
            <div class="editor-step">
                <h2>AI Description</h2>
                <p class="text-gray mb-xl">Let AI craft the perfect description</p>

                <div class="grid grid-cols-2 gap-base mb-xl">
                    <div class="form-group">
                        <label>Tone</label>
                        <select class="input select" id="step4-tone">
                            ${TONES.map(t => `<option value="${t.value}" ${this.data.description.tone === t.value ? 'selected' : ''}>${t.label}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Focus</label>
                        <select class="input select" id="step4-focus">
                            ${FOCUSES.map(f => `<option value="${f.value}" ${this.data.description.focus === f.value ? 'selected' : ''}>${f.label}</option>`).join('')}
                        </select>
                    </div>
                </div>

                <button class="btn btn-primary" id="generate-description">
                    <i data-feather="magic"></i>
                    Generate Description
                </button>

                <div class="form-group mt-xl">
                    <label>Description</label>
                    <textarea class="input textarea" id="step4-description" rows="8">${this.data.description.text || ''}</textarea>
                </div>

                <div id="poi-section" class="hidden mt-xl">
                    <h4>Nearby Points of Interest</h4>
                    <p class="text-gray" id="poi-text"></p>
                </div>
            </div>
        `;
    }

    renderReviewStep() {
        const basic = this.data.basic;
        return `
            <div class="editor-step">
                <h2>Review & Publish</h2>
                <p class="text-gray mb-xl">Double-check everything before publishing</p>

                <div class="card mb-lg">
                    <h3>${basic.title || 'Untitled Listing'}</h3>
                    <p class="text-lg font-semibold mt-base">${UI.formatCurrency(basic.price)}</p>
                    <p class="text-gray">${basic.address}, ${basic.city}, ${basic.state} ${basic.postal_code}</p>
                </div>

                <div class="grid grid-cols-3 gap-base mb-lg">
                    <div class="card">
                        <div class="text-gray text-sm">Bedrooms</div>
                        <div class="text-lg font-semibold">${this.data.details.bedrooms || '-'}</div>
                    </div>
                    <div class="card">
                        <div class="text-gray text-sm">Bathrooms</div>
                        <div class="text-lg font-semibold">${this.data.details.bathrooms || '-'}</div>
                    </div>
                    <div class="card">
                        <div class="text-gray text-sm">Square Feet</div>
                        <div class="text-lg font-semibold">${this.data.details.square_feet || '-'}</div>
                    </div>
                </div>

                <div class="mb-lg">
                    <h4 class="mb-base">Photos (${this.data.images.length})</h4>
                    <div class="grid grid-cols-4 gap-base">
                        ${this.data.images.map(img => `
                            <img src="${img.thumbnail_path}" style="width: 100%; border-radius: var(--radius-base);">
                        `).join('')}
                    </div>
                </div>

                <div class="mb-lg">
                    <h4 class="mb-base">Description</h4>
                    <p class="text-gray">${this.data.description.text || 'No description added'}</p>
                </div>
            </div>
        `;
    }

    attachStepEventListeners() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');

        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => fileInput.click());
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--color-indigo-500)';
                uploadArea.style.backgroundColor = 'var(--color-indigo-50)';
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.borderColor = 'var(--color-gray-300)';
                uploadArea.style.backgroundColor = 'transparent';
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--color-gray-300)';
                uploadArea.style.backgroundColor = 'transparent';
                this.handleFiles(e.dataTransfer.files);
            });

            fileInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
        }

        document.querySelectorAll('.remove-image').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.data.images.splice(index, 1);
                this.renderStep(this.currentStep);
            });
        });
    }

    async handleFiles(files) {
        if (!this.listingId) {
            UI.showError('Please complete the previous steps first');
            return;
        }

        const maxImages = 10;
        const remaining = maxImages - this.data.images.length;
        const toUpload = Array.from(files).slice(0, remaining);

        if (toUpload.length === 0) {
            UI.showError(`Maximum ${maxImages} images allowed`);
            return;
        }

        for (const file of toUpload) {
            try {
                const image = await api.uploadImage(file, this.listingId);
                this.data.images.push(image);
            } catch (error) {
                UI.showError(`Failed to upload ${file.name}: ${error.message}`);
            }
        }

        this.renderStep(this.currentStep);
    }

    async generateDescription() {
        if (!this.listingId) {
            UI.showError('Please complete the previous steps first');
            return;
        }

        const tone = document.getElementById('step4-tone').value;
        const focus = document.getElementById('step4-focus').value;
        const textarea = document.getElementById('step4-description');

        textarea.disabled = true;
        textarea.value = 'Generating description...';

        try {
            const result = await api.generateDescription(this.listingId, tone, focus);
            this.data.description = { tone, focus, text: result.description };
            textarea.value = result.description;
            
            await this.loadPOI();
        } catch (error) {
            UI.showError('Failed to generate description: ' + error.message);
        }

        textarea.disabled = false;
    }

    async loadPOI() {
        const basic = this.data.basic;
        const address = `${basic.address}, ${basic.city}, ${basic.state} ${basic.postal_code}`;
        
        try {
            const poi = await api.getPOI(address);
            document.getElementById('poi-section').classList.remove('hidden');
            document.getElementById('poi-text').textContent = poi.description_text;
        } catch (error) {
            console.error('Failed to load POI:', error);
        }
    }

    async publish() {
        const basic = this.data.basic;
        const details = this.data.details;

        const listingData = {
            title: basic.title,
            property_type: basic.property_type,
            transaction_type: basic.transaction_type,
            address: basic.address,
            city: basic.city,
            state: basic.state,
            postal_code: basic.postal_code,
            country: 'United States',
            price: parseInt(basic.price),
            bedrooms: parseInt(details.bedrooms),
            bathrooms: parseFloat(details.bathrooms),
            square_feet: parseInt(details.square_feet),
            description: this.data.description.text || details.description || '',
            amenities: details.amenities || []
        };

        try {
            if (this.listingId) {
                await api.updateListing(this.listingId, listingData);
            } else {
                const result = await api.createListing(listingData);
                this.listingId = result.id;
                Storage.setEditorListingId(this.listingId);
            }

            UI.showSuccess('Listing published successfully!');
            setTimeout(() => {
                UI.navigate(ROUTES.DASHBOARD);
            }, 1500);
        } catch (error) {
            UI.showError('Failed to publish: ' + error.message);
        }
    }
}
