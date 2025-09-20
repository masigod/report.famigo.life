# Netlify ATTENDANCE Table Setup Guide

## Quick Setup Steps

### 1. Create ATTENDANCE Table in Airtable
1. Go to your Airtable base: https://airtable.com/appZcPs57spwdoKQH/
2. Click "Add or import" → "Create blank table"
3. Name it: **AttendanceImages**
4. Copy the table ID from the URL (format: tblXXXXXXXXXXXX)

### 2. Add Environment Variable in Netlify
1. Go to Netlify dashboard: https://app.netlify.com/
2. Select your site: **report-famigo-cosine**
3. Go to: Site settings → Environment variables
4. Add new variable:
   - **Key**: `AIRTABLE_ATTENDANCE_TABLE_ID`
   - **Value**: [Your table ID from step 1]
5. Click "Save"

### 3. Trigger Rebuild
1. Go to Deploys tab
2. Click "Trigger deploy" → "Clear cache and deploy site"
3. Wait for deployment to complete

## Environment Variables Checklist

Verify all these are set in Netlify:

- ✅ `AIRTABLE_API_KEY` - patXSiZG4pLiTrRHb...
- ✅ `AIRTABLE_BASE_ID` - appZcPs57spwdoKQH
- ✅ `AIRTABLE_TABLE_ID` - tblxMzwX1wWJKIOhY
- ✅ `AIRTABLE_ADMIN_TABLE_ID` - 등록 완료
- ⏳ `AIRTABLE_ATTENDANCE_TABLE_ID` - [AttendanceImages 테이블 생성 후 추가 필요]

## Testing After Setup

1. Login as staff user (username contains "staff")
2. Should redirect to mobile-attendance.html
3. Check browser console for:
   ```
   Attendance Table ID: tblXXXXXXXXXXXX (Loaded)
   ```

## Troubleshooting

### If "Missing" appears in console:
- Check Netlify environment variables
- Trigger a new deploy
- Clear browser cache

### If API errors occur:
- Verify table ID is correct
- Check Airtable permissions for the table
- Ensure all required fields exist in table

## Table Schema Reminder

The AttendanceImages table should have these fields:
- participantID (Number)
- participantName (Single line text)
- checkinTime (Date and time)
- attendanceStatus (Single select: Pending/Attended/No-show)
- rewardType (Single select: MobileVoucher/Cash/None)
- idCardImage (Attachment)
- bankbookImage (Attachment)
- staffName (Single line text)
- staffID (Single line text)
- checkDate (Date)
- checkTime (Single line text)
- notes (Long text)

## Contact for Issues
Report any deployment issues at: https://github.com/anthropics/claude-code/issues