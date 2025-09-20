// Configuration loader with environment variable support
// This file handles loading configuration from various sources

(function() {
    // Function to load configuration from environment or fallback sources
    window.loadConfig = async function() {
        // Check if we're in a Netlify environment (has environment variables)
        if (window.location.hostname.includes('netlify.app') || window.location.hostname.includes('netlify.com')) {
            // In production, environment variables should be injected by build process
            return;
        }

        // For local development, try to load from localStorage or prompt user
        if (!window.AIRTABLE_API_KEY && !localStorage.getItem('AIRTABLE_API_KEY')) {
            const apiKey = prompt('Please enter your Airtable API Key (will be stored locally):');
            if (apiKey) {
                localStorage.setItem('AIRTABLE_API_KEY', apiKey);
                window.AIRTABLE_API_KEY = apiKey;
            }
        } else if (localStorage.getItem('AIRTABLE_API_KEY')) {
            window.AIRTABLE_API_KEY = localStorage.getItem('AIRTABLE_API_KEY');
        }

        // Set other config values from localStorage if available
        if (localStorage.getItem('AIRTABLE_BASE_ID')) {
            window.AIRTABLE_BASE_ID = localStorage.getItem('AIRTABLE_BASE_ID');
        }
        if (localStorage.getItem('AIRTABLE_TABLE_ID')) {
            window.AIRTABLE_TABLE_ID = localStorage.getItem('AIRTABLE_TABLE_ID');
        }
        if (localStorage.getItem('AIRTABLE_ADMIN_TABLE_ID')) {
            window.AIRTABLE_ADMIN_TABLE_ID = localStorage.getItem('AIRTABLE_ADMIN_TABLE_ID');
        }
        if (localStorage.getItem('AIRTABLE_ATTENDANCE_TABLE_ID')) {
            window.AIRTABLE_ATTENDANCE_TABLE_ID = localStorage.getItem('AIRTABLE_ATTENDANCE_TABLE_ID');
        }
    };

    // Auto-load config on script load
    window.loadConfig();
})();