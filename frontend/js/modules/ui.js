class UI {
    static showPage(pageName) {
        document.querySelectorAll('[data-page]').forEach(el => {
            el.classList.add('hidden');
            el.style.display = 'none';
        });
        
        const page = document.querySelector(`[data-page="${pageName}"]`);
        if (page) {
            page.classList.remove('hidden');
            page.style.display = 'block';
        }
        
        window.scrollTo(0, 0);
    }

    static showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    static closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    static closeAllModals() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }

    static showLoading(elementId) {
        const el = document.getElementById(elementId);
        if (el) {
            el.dataset.originalContent = el.innerHTML;
            el.innerHTML = '<div class="spinner"></div>';
            el.disabled = true;
        }
    }

    static hideLoading(elementId) {
        const el = document.getElementById(elementId);
        if (el && el.dataset.originalContent) {
            el.innerHTML = el.dataset.originalContent;
            el.disabled = false;
        }
    }

    static showError(message, duration = 5000) {
        console.error(message);
        this.showToast(message, 'error', duration);
    }

    static showSuccess(message, duration = 3000) {
        console.log(message);
        this.showToast(message, 'success', duration);
    }

    static showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
            animation: slideIn 0.3s ease;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    static navigate(route) {
        window.history.pushState({}, '', route);
        this.handleRoute(route);
    }

    static handleRoute(route) {
        const path = route.split('?')[0];
        
        switch (path) {
            case ROUTES.LANDING:
                Pages.Landing.render();
                break;
            case ROUTES.LOGIN:
                Pages.Landing.showLogin();
                break;
            case ROUTES.SIGNUP:
                Pages.Landing.showSignup();
                break;
            case ROUTES.DASHBOARD:
                if (!Auth.requireAuth()) return;
                Pages.Dashboard.render();
                break;
            case ROUTES.EDITOR:
            case ROUTES.EDITOR_NEW:
                if (!Auth.requireAuth()) return;
                Pages.Editor.render(path === ROUTES.EDITOR_NEW);
                break;
            case ROUTES.ADMIN:
                if (!Auth.requireAdmin()) return;
                Pages.Admin.render();
                break;
            default:
                this.navigate(ROUTES.LANDING);
        }
    }

    static updateHeader(isAuthenticated) {
        const navActions = document.getElementById('nav-actions');
        if (navActions) {
            if (isAuthenticated) {
                const user = Auth.getCurrentUser();
                navActions.innerHTML = `
                    <button class="btn btn-secondary btn-sm" id="dashboard-btn">Dashboard</button>
                    <div class="avatar avatar-sm" id="user-avatar">
                        ${user?.first_name?.charAt(0) || 'U'}
                    </div>
                    <button class="btn btn-secondary btn-sm" id="logout-btn" style="display: none;">Logout</button>
                `;
                
                document.getElementById('dashboard-btn')?.addEventListener('click', () => {
                    UI.navigate(ROUTES.DASHBOARD);
                });
                
                document.getElementById('logout-btn')?.addEventListener('click', () => {
                    Auth.logout();
                });
            } else {
                navActions.innerHTML = `
                    <button class="btn btn-secondary btn-sm" id="login-btn">Log In</button>
                    <button class="btn btn-primary btn-sm" id="signup-btn">Get Started</button>
                `;
                
                document.getElementById('login-btn')?.addEventListener('click', () => {
                    UI.navigate(ROUTES.LOGIN);
                });
                
                document.getElementById('signup-btn')?.addEventListener('click', () => {
                    UI.navigate(ROUTES.SIGNUP);
                });
            }
        }
    }

    static formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0
        }).format(amount);
    }

    static formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

window.addEventListener('popstate', () => {
    UI.handleRoute(window.location.pathname);
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) {
                UI.closeModal(modal.id);
            }
        });
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                UI.closeModal(modal.id);
            }
        });
    });
});
