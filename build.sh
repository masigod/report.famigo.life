#!/bin/bash

# Create environment variables injection script for Netlify deployment
cat > env-config.js << EOF
// Auto-generated environment configuration from Netlify
window.AIRTABLE_API_KEY = '${AIRTABLE_API_KEY}';
window.AIRTABLE_BASE_ID = '${AIRTABLE_BASE_ID}';
window.AIRTABLE_TABLE_ID = '${AIRTABLE_TABLE_ID}';
window.AIRTABLE_ADMIN_TABLE_ID = '${AIRTABLE_ADMIN_TABLE_ID}';
window.AIRTABLE_ATTENDANCE_TABLE_ID = '${AIRTABLE_ATTENDANCE_TABLE_ID}';
EOF

# Also ensure config.js exists with the updated secure version
cat > config.js << EOF
// Configuration with environment variable support for security
const AIRTABLE_CONFIG = {
    // API Key should be set via environment variable for production
    API_KEY: window.AIRTABLE_API_KEY || localStorage.getItem('AIRTABLE_API_KEY') || '',
    BASE_ID: window.AIRTABLE_BASE_ID || 'appZcPs57spwdoKQH',
    TABLE_ID: window.AIRTABLE_TABLE_ID || 'tblxMzwX1wWJKIOhY',
    ADMIN_TABLE_ID: window.AIRTABLE_ADMIN_TABLE_ID || 'tblFQ7ofZ9CXZcydm',
    ATTENDANCE_TABLE_ID: window.AIRTABLE_ATTENDANCE_TABLE_ID || ''
};

// Security check - warn if API key is not properly configured
if (!AIRTABLE_CONFIG.API_KEY) {
    console.warn('Airtable API key not configured. Please set environment variables.');
}
EOF

echo "Environment configuration files created successfully"