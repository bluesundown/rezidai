Pages.Dashboard = {
    listings: [],

    async init() {
        this.bindEvents();
        await this.loadListings();
        this.updateHeader();
    },

    async render() {
        this.showPage('dashboard');
        await this.init();
    },

    showPage(pageName) {
        UI.showPage(pageName);
        this.renderDashboard();
    },

    updateHeader() {
        UI.updateHeader(true);
    },

    bindEvents() {
        document.getElementById('new-listing-btn')?.addEventListener('click', () => {
            UI.navigate(ROUTES.EDITOR_NEW);
        });

        document.getElementById('logout-btn')?.addEventListener('click', () => {
            Auth.logout();
        });
    },

    async loadListings() {
        try {
            this.listings = await api.getListings();
            this.renderListings();
        } catch (error) {
            UI.showError('Failed to load listings: ' + error.message);
        }
    },

    async loadUser() {
        try {
            const user = await api.getCurrentUser();
            localStorage.setItem('user', JSON.stringify(user));
            this.updateUserDisplay(user);
        } catch (error) {
            console.error('Failed to load user:', error);
        }
    },

    updateUserDisplay(user) {
        const avatar = document.getElementById('user-avatar');
        if (avatar && user.first_name) {
            avatar.textContent = user.first_name.charAt(0);
        }
    },

    renderDashboard() {
        const app = document.getElementById('app');
        if (!app) return;

        const user = Auth.getCurrentUser();
        
        app.innerHTML = `
            <div data-page="dashboard" style="padding: var(--spacing-3xl) 0;">
                <div class="container">
                    <div class="flex justify-between items-center mb-2xl">
                        <div>
                            <h1 style="margin-bottom: var(--spacing-sm);">Dashboard</h1>
                            <p class="text-gray">Welcome back, ${user?.first_name || 'User'}!</p>
                        </div>
                        <button class="btn btn-primary" id="new-listing-btn">
                            <i data-feather="plus"></i>
                            New Listing
                        </button>
                    </div>

                    <div class="grid grid-cols-3 mb-2xl">
                        <div class="card">
                            <div class="flex items-center gap-lg">
                                <div style="width: 48px; height: 48px; background: var(--color-indigo-100); border-radius: var(--radius-base); display: flex; align-items: center; justify-content: center;">
                                    <i data-feather="home" style="width: 24px; color: var(--color-indigo-600);"></i>
                                </div>
                                <div>
                                    <div class="text-gray text-sm">Total Listings</div>
                                    <div class="text-xl font-bold" id="total-listings">0</div>
                                </div>
                            </div>
                        </div>
                        <div class="card">
                            <div class="flex items-center gap-lg">
                                <div style="width: 48px; height: 48px; background: var(--color-green-100); border-radius: var(--radius-base); display: flex; align-items: center; justify-content: center;">
                                    <i data-feather="check-circle" style="width: 24px; color: var(--color-green-600);"></i>
                                </div>
                                <div>
                                    <div class="text-gray text-sm">Published</div>
                                    <div class="text-xl font-bold" id="published-listings">0</div>
                                </div>
                            </div>
                        </div>
                        <div class="card">
                            <div class="flex items-center gap-lg">
                                <div style="width: 48px; height: 48px; background: var(--color-yellow-100); border-radius: var(--radius-base); display: flex; align-items: center; justify-content: center;">
                                    <i data-feather="clock" style="width: 24px; color: var(--color-yellow-600);"></i>
                                </div>
                                <div>
                                    <div class="text-gray text-sm">Drafts</div>
                                    <div class="text-xl font-bold" id="draft-listings">0</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <h2 class="mb-lg">Your Listings</h2>
                    
                    <div id="listings-container">
                        <div class="card" style="text-align: center; padding: var(--spacing-3xl);">
                            <i data-feather="inbox" style="width: 48px; height: 48px; color: var(--color-gray-400); margin: 0 auto var(--spacing-lg);"></i>
                            <p class="text-gray mb-lg">No listings yet</p>
                            <button class="btn btn-primary" id="first-listing-btn">Create Your First Listing</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.attachDashboardEvents();
        feather.replace();
    },

    attachDashboardEvents() {
        document.getElementById('new-listing-btn')?.addEventListener('click', () => {
            UI.navigate(ROUTES.EDITOR_NEW);
        });

        document.getElementById('first-listing-btn')?.addEventListener('click', () => {
            UI.navigate(ROUTES.EDITOR_NEW);
        });
    },

    renderListings() {
        const container = document.getElementById('listings-container');
        if (!container) return;

        const total = this.listings.length;
        const published = this.listings.filter(l => l.is_published).length;
        const drafts = total - published;

        document.getElementById('total-listings').textContent = total;
        document.getElementById('published-listings').textContent = published;
        document.getElementById('draft-listings').textContent = drafts;

        if (total === 0) {
            return;
        }

        container.innerHTML = `
            <div class="grid grid-cols-3">
                ${this.listings.map(listing => `
                    <div class="card" style="padding: 0; overflow: hidden;">
                        <div style="height: 200px; background: var(--color-gray-200); display: flex; align-items: center; justify-content: center;">
                            <i data-feather="image" style="width: 48px; color: var(--color-gray-400);"></i>
                        </div>
                        <div style="padding: var(--spacing-lg);">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: var(--spacing-sm);">
                                <h3 style="margin: 0; font-size: 1rem;">${listing.title}</h3>
                                <span class="badge ${listing.is_published ? 'badge-success' : 'badge-warning'}">
                                    ${listing.is_published ? 'Published' : 'Draft'}
                                </span>
                            </div>
                            <p class="text-gray text-sm mb-lg">${listing.city}, ${listing.state}</p>
                            <div class="flex justify-between items-center">
                                <div class="font-semibold">${UI.formatCurrency(listing.price)}</div>
                                <div class="flex gap-sm">
                                    <button class="edit-listing-btn btn btn-secondary btn-sm" data-id="${listing.id}">
                                        <i data-feather="edit" style="width: 16px;"></i>
                                    </button>
                                    <button class="delete-listing-btn btn btn-secondary btn-sm" data-id="${listing.id}">
                                        <i data-feather="trash-2" style="width: 16px;"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        this.attachListingEvents();
        feather.replace();
    },

    attachListingEvents() {
        document.querySelectorAll('.edit-listing-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                const listing = this.listings.find(l => l.id === id);
                if (listing) {
                    await this.editListing(listing);
                }
            });
        });

        document.querySelectorAll('.delete-listing-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                if (confirm('Are you sure you want to delete this listing?')) {
                    await this.deleteListing(id);
                }
            });
        });
    },

    async editListing(listing) {
        const editorData = {
            basic: {
                title: listing.title,
                property_type: listing.property_type,
                transaction_type: listing.transaction_type,
                address: listing.address,
                city: listing.city,
                state: listing.state,
                postal_code: listing.postal_code,
                price: listing.price
            },
            details: {
                bedrooms: listing.bedrooms,
                bathrooms: listing.bathrooms,
                square_feet: listing.square_feet,
                description: listing.description,
                amenities: listing.amenities || []
            },
            images: [],
            description: {
                text: listing.ai_generated_description || listing.description || ''
            }
        };

        Storage.setEditorListingId(listing.id);
        Storage.saveDraft(listing.id, editorData);
        UI.navigate(ROUTES.EDITOR);
    },

    async deleteListing(id) {
        try {
            await api.deleteListing(id);
            UI.showSuccess('Listing deleted');
            this.listings = this.listings.filter(l => l.id !== id);
            this.renderListings();
        } catch (error) {
            UI.showError('Failed to delete: ' + error.message);
        }
    }
};
