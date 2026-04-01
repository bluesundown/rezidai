class Storage {
    static getDraft(listingId) {
        return JSON.parse(localStorage.getItem(`draft_${listingId}`) || '{}');
    }

    static saveDraft(listingId, data) {
        localStorage.setItem(`draft_${listingId}`, JSON.stringify(data));
    }

    static deleteDraft(listingId) {
        localStorage.removeItem(`draft_${listingId}`);
    }

    static getEditorStep() {
        return parseInt(localStorage.getItem('editor_step') || '1');
    }

    static setEditorStep(step) {
        localStorage.setItem('editor_step', step);
    }

    static getEditorListingId() {
        return localStorage.getItem('editor_listing_id');
    }

    static setEditorListingId(id) {
        localStorage.setItem('editor_listing_id', id);
    }

    static clearEditorState() {
        const listingId = this.getEditorListingId();
        if (listingId) {
            this.deleteDraft(listingId);
        }
        localStorage.removeItem('editor_step');
        localStorage.removeItem('editor_listing_id');
    }

    static getSetting(key, defaultValue = null) {
        const value = localStorage.getItem(`setting_${key}`);
        return value !== null ? JSON.parse(value) : defaultValue;
    }

    static setSetting(key, value) {
        localStorage.setItem(`setting_${key}`, JSON.stringify(value));
    }

    static clearAll() {
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
            if (!key.startsWith('access_') && !key.startsWith('user')) {
                localStorage.removeItem(key);
            }
        });
    }
}
