document.addEventListener('DOMContentLoaded', () => {
    feather.replace();

    UI.updateHeader(Auth.isAuthenticated());
    UI.handleRoute(window.location.pathname || ROUTES.LANDING);

    if (window.location.pathname === ROUTES.LANDING) {
        Pages.Landing.init();
    }
});

window.Pages = Pages || {};
