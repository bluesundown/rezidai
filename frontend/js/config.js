const API_CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/api' 
        : '/api',
    GOOGLE_MAPS_API_KEY: '',
    STRIPE_PUBLIC_KEY: 'pk_test_',
    LANGUAGE: localStorage.getItem('language') || 'en'
};

const ROUTES = {
    LANDING: '/',
    LOGIN: '/login',
    SIGNUP: '/signup',
    DASHBOARD: '/dashboard',
    EDITOR: '/editor',
    EDITOR_NEW: '/editor/new',
    ADMIN: '/admin'
};

const PROPERTY_TYPES = [
    { value: 'house', label: 'House' },
    { value: 'apartment', label: 'Apartment' },
    { value: 'condo', label: 'Condo' },
    { value: 'townhouse', label: 'Townhouse' },
    { value: 'villa', label: 'Villa' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'land', label: 'Land' }
];

const TRANSACTION_TYPES = [
    { value: 'sale', label: 'For Sale' },
    { value: 'rent', label: 'For Rent' }
];

const TONES = [
    { value: 'professional', label: 'Professional' },
    { value: 'friendly', label: 'Friendly' },
    { value: 'luxury', label: 'Luxury' },
    { value: 'modern', label: 'Modern' }
];

const FOCUSES = [
    { value: 'general', label: 'General Appeal' },
    { value: 'investment', label: 'Investment Potential' },
    { value: 'family', label: 'Family-Friendly' },
    { value: 'luxury', label: 'Luxury Features' },
    { value: 'location', label: 'Location Benefits' },
    { value: 'amenities', label: 'Amenities' }
];
