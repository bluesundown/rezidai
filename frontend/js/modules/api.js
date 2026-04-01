class API {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = localStorage.getItem('access_token');
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                window.location.href = ROUTES.LOGIN;
                return;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || data.error || 'API Error');
            }

            return data;
        } catch (error) {
            console.error(`API Error: ${endpoint}`, error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    async login(email, password) {
        return this.post('/auth/login', { email, password });
    }

    async register(email, password, firstName, lastName) {
        return this.post('/auth/register', { 
            email, 
            password, 
            first_name: firstName,
            last_name: lastName 
        });
    }

    async googleOAuth(token) {
        return this.post('/oauth/google/callback', { token });
    }

    async appleOAuth(token) {
        return this.post('/oauth/apple/callback', { token });
    }

    async getCurrentUser() {
        return this.get('/users/me');
    }

    async updateProfile(data) {
        return this.put('/users/me', data);
    }

    async deleteAccount() {
        return this.delete('/users/me');
    }

    async getListings(skip = 0, limit = 20) {
        return this.get(`/listings?skip=${skip}&limit=${limit}`);
    }

    async getListing(id) {
        return this.get(`/listings/${id}`);
    }

    async createListing(data) {
        return this.post('/listings', data);
    }

    async updateListing(id, data) {
        return this.put(`/listings/${id}`, data);
    }

    async deleteListing(id) {
        return this.delete(`/listings/${id}`);
    }

    async uploadImage(file, listingId) {
        const formData = new FormData();
        formData.append('file', file);
        
        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`${this.baseURL}/images/upload?listing_id=${listingId}`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = ROUTES.LOGIN;
            return;
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        return data;
    }

    async getListingImages(listingId) {
        return this.get(`/images/listing/${listingId}`);
    }

    async deleteImage(imageId) {
        return this.delete(`/images/${imageId}`);
    }

    async generateDescription(listingId, tone, focus) {
        return this.post('/descriptions/generate', { 
            listing_id: listingId, 
            tone, 
            focus 
        });
    }

    async getDescriptionFilters() {
        return this.get('/descriptions/filters');
    }

    async getPOI(address) {
        return this.get(`/maps/poi?address=${encodeURIComponent(address)}`);
    }

    async savePOI(listingId, address) {
        return this.post(`/maps/listing/${listingId}/poi`, { address });
    }

    async getAdminConfig() {
        return this.get('/admin/config/api-keys');
    }

    async updateAPIKey(keyName, keyValue) {
        return this.put('/admin/config/api-keys', { key_name: keyName, key_value: keyValue });
    }

    async getFilters() {
        return this.get('/admin/filters');
    }

    async createFilter(data) {
        return this.post('/admin/filters', data);
    }

    async updateFilter(id, data) {
        return this.put(`/admin/filters/${id}`, data);
    }

    async deleteFilter(id) {
        return this.delete(`/admin/filters/${id}`);
    }
}

const api = new API(API_CONFIG.API_BASE_URL);
