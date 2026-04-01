const Pages = Pages || {};

Pages.Landing = {
    init() {
        this.bindEvents();
        this.renderFeatures();
        this.renderPricing();
        this.updateHeader();
    },

    render() {
        this.showPage('landing');
        this.init();
    },

    showLogin() {
        this.showPage('login');
        this.updateHeader();
    },

    showSignup() {
        this.showPage('signup');
        this.updateHeader();
    },

    showPage(pageName) {
        UI.showPage(pageName);
    },

    updateHeader() {
        UI.updateHeader(Auth.isAuthenticated());
    },

    bindEvents() {
        document.getElementById('hero-cta')?.addEventListener('click', () => {
            if (Auth.isAuthenticated()) {
                UI.navigate(ROUTES.EDITOR_NEW);
            } else {
                UI.navigate(ROUTES.SIGNUP);
            }
        });

        document.getElementById('hero-demo')?.addEventListener('click', () => {
            UI.showModal('demo-modal');
        });

        document.getElementById('login-btn')?.addEventListener('click', () => {
            UI.navigate(ROUTES.LOGIN);
        });

        document.getElementById('signup-btn')?.addEventListener('click', () => {
            UI.navigate(ROUTES.SIGNUP);
        });

        document.getElementById('login-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            UI.navigate(ROUTES.LOGIN);
        });

        document.getElementById('signup-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            UI.navigate(ROUTES.SIGNUP);
        });

        document.getElementById('login-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            try {
                await Auth.login(email, password);
                UI.showSuccess('Welcome back!');
                setTimeout(() => UI.navigate(ROUTES.DASHBOARD), 500);
            } catch (error) {
                UI.showError(error.detail || error.message || 'Login failed');
            }
        });

        document.getElementById('signup-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const firstName = document.getElementById('signup-firstname').value;
            const lastName = document.getElementById('signup-lastname').value;
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;

            try {
                await Auth.register(email, password, firstName, lastName);
                UI.showSuccess('Account created!');
                setTimeout(() => UI.navigate(ROUTES.DASHBOARD), 500);
            } catch (error) {
                UI.showError(error.detail || error.message || 'Registration failed');
            }
        });

        document.getElementById('google-login')?.addEventListener('click', () => {
            this.handleOAuthLogin('google');
        });

        document.getElementById('apple-login')?.addEventListener('click', () => {
            this.handleOAuthLogin('apple');
        });

        document.getElementById('signup-google')?.addEventListener('click', () => {
            this.handleOAuthLogin('google');
        });

        document.getElementById('signup-apple')?.addEventListener('click', () => {
            this.handleOAuthLogin('apple');
        });

        document.getElementById('cta-btn')?.addEventListener('click', () => {
            if (Auth.isAuthenticated()) {
                UI.navigate(ROUTES.DASHBOARD);
            } else {
                UI.navigate(ROUTES.SIGNUP);
            }
        });

        window.addEventListener('hashchange', () => {
            const hash = window.location.hash;
            if (hash) {
                const element = document.querySelector(hash);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    },

    handleOAuthLogin(provider) {
        if (Auth.isAuthenticated()) {
            UI.navigate(ROUTES.DASHBOARD);
            return;
        }

        UI.showSuccess(`${provider.charAt(0).toUpperCase() + provider.slice(1)} login coming soon!`);
    },

    renderFeatures() {
        const container = document.getElementById('features-grid');
        if (!container) return;

        const features = [
            {
                icon: 'zap',
                title: 'AI-Powered Descriptions',
                description: 'Generate compelling property descriptions in seconds with our advanced AI technology.'
            },
            {
                icon: 'image',
                title: 'Auto Image Enhancement',
                description: 'Automatically enhance your property photos with professional-grade editing.'
            },
            {
                icon: 'map',
                title: 'Location Intelligence',
                description: 'Discover nearby amenities and include them in your listings automatically.'
            },
            {
                icon: 'layout',
                title: 'Easy Editor',
                description: 'Simple, intuitive interface makes creating listings a breeze.'
            },
            {
                icon: 'share-2',
                title: 'Multi-Channel Publishing',
                description: 'Publish to multiple platforms with a single click.'
            },
            {
                icon: 'bar-chart-2',
                title: 'Analytics Dashboard',
                description: 'Track views, engagement, and conversion rates in real-time.'
            }
        ];

        container.innerHTML = features.map(feature => `
            <div class="card">
                <div style="width: 48px; height: 48px; background: var(--color-indigo-100); border-radius: var(--radius-base); display: flex; align-items: center; justify-content: center; margin-bottom: var(--spacing-lg);">
                    <i data-feather="${feature.icon}" style="width: 24px; color: var(--color-indigo-600);"></i>
                </div>
                <h3 style="margin-bottom: var(--spacing-base);">${feature.title}</h3>
                <p class="text-gray">${feature.description}</p>
            </div>
        `).join('');

        feather.replace();
    },

    renderPricing() {
        const container = document.getElementById('pricing-grid');
        if (!container) return;

        const plans = [
            {
                name: 'Free',
                price: 0,
                description: 'Perfect for getting started',
                features: [
                    '3 listings per month',
                    'Basic AI descriptions',
                    'Standard image enhancement',
                    'Email support'
                ],
                cta: 'Get Started',
                highlighted: false
            },
            {
                name: 'Pro',
                price: 29,
                description: 'For serious real estate agents',
                features: [
                    'Unlimited listings',
                    'Premium AI descriptions',
                    'Advanced image enhancement',
                    'Priority support',
                    'Custom branding',
                    'Analytics dashboard'
                ],
                cta: 'Start Free Trial',
                highlighted: true
            },
            {
                name: 'Enterprise',
                price: 99,
                description: 'For teams and brokerages',
                features: [
                    'Everything in Pro',
                    'Team collaboration',
                    'API access',
                    'Dedicated support',
                    'Custom integrations',
                    'White-label option'
                ],
                cta: 'Contact Sales',
                highlighted: false
            }
        ];

        container.innerHTML = plans.map(plan => `
            <div class="card" style="${plan.highlighted ? 'border: 2px solid var(--color-indigo-500); position: relative;' : ''}">
                ${plan.highlighted ? '<div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--color-indigo-600); color: white; padding: 4px 16px; border-radius: var(--radius-full); font-size: 12px; font-weight: 600;">MOST POPULAR</div>' : ''}
                <div style="margin-bottom: var(--spacing-xl); ${plan.highlighted ? 'padding-top: var(--spacing-lg);' : ''}">
                    <h3 style="margin-bottom: var(--spacing-sm);">${plan.name}</h3>
                    <p class="text-gray text-sm mb-lg">${plan.description}</p>
                    <div style="font-size: 2rem; font-weight: 700;">
                        $${plan.price}<span style="font-size: 1rem; font-weight: 400; color: var(--color-gray-500);">/mo</span>
                    </div>
                </div>
                <ul style="list-style: none; margin-bottom: var(--spacing-xl);">
                    ${plan.features.map(feature => `
                        <li style="padding: var(--spacing-sm) 0; display: flex; align-items: center; gap: var(--spacing-base);">
                            <i data-feather="check" style="width: 20px; color: var(--color-green-500); flex-shrink: 0;"></i>
                            <span>${feature}</span>
                        </li>
                    `).join('')}
                </ul>
                <button class="btn ${plan.highlighted ? 'btn-primary' : 'btn-secondary'} btn-block" onclick="UI.navigate('${ROUTES.SIGNUP}')">
                    ${plan.cta}
                </button>
            </div>
        `).join('');

        feather.replace();
    }
};
