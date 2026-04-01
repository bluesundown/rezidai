class Auth {
    static async login(email, password) {
        try {
            const response = await api.login(email, password);
            this.setAuth(response.access_token, response.user);
            return response;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    static async register(email, password, firstName, lastName) {
        try {
            const response = await api.register(email, password, firstName, lastName);
            this.setAuth(response.access_token, response.user);
            return response;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    static setAuth(token, user) {
        localStorage.setItem('access_token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    static logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = ROUTES.LANDING;
    }

    static isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }

    static isAdmin() {
        const user = this.getCurrentUser();
        return user && user.is_admin;
    }

    static getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    static requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = ROUTES.LOGIN;
            return false;
        }
        return true;
    }

    static requireAdmin() {
        if (!this.isAdmin()) {
            window.location.href = ROUTES.LANDING;
            return false;
        }
        return true;
    }
}
