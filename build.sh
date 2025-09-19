#!/bin/bash

# Netlify 환경 변수에서 API 키를 가져와서 config.js 파일 생성
cat > config.js << EOF
// Auto-generated config file from Netlify environment variables
const AIRTABLE_CONFIG = {
    API_KEY: '${AIRTABLE_API_KEY}',
    BASE_ID: '${AIRTABLE_BASE_ID}',
    TABLE_ID: '${AIRTABLE_TABLE_ID}',
    ADMIN_TABLE_ID: '${AIRTABLE_ADMIN_TABLE_ID}'
};
EOF

echo "config.js file created with environment variables"