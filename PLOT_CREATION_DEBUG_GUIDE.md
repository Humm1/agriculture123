# Plot Creation Debugging Guide

## What I Fixed

### 1. **Content-Type Header Issue** ✅
- **Problem**: Frontend was manually setting `Content-Type: multipart/form-data` without boundary
- **Fix**: Removed manual header, let fetch set it automatically

### 2. **RLS Authentication Issue** ✅
- **Problem**: Backend using anon key subject to Row Level Security
- **Fix**: Changed to `supabase_admin` (service role key) to bypass RLS

### 3. **Added Comprehensive Logging** ✅
- Frontend: Button click, validation, request data, response
- Backend: Request received, database insert, image saves, final result

### 4. **Try-Catch Structure Fix** ✅
- **Problem**: Nested try blocks causing syntax errors
- **Fix**: Flattened structure with proper error handling

## Testing Steps

### Step 1: Check Button Click Detection
When you tap "Create Plot" button, you should see:

**In Expo Console:**
```
===================================
CREATE PLOT BUTTON CLICKED!
===================================
=== CREATE PLOT SUBMIT STARTED ===
Current timestamp: 2025-10-26T...
Form data: {...}
User: {...}
```

**AND** you should see an Alert popup saying "Button clicked! Check console for details."

**If you DON'T see this:**
- Button click is not registering
- Check if ScrollView is blocking touches
- Try restarting the Expo app

### Step 2: Check Validation
After button click logs, check for validation:

**Success:**
```
All validations passed, proceeding with submission...
Sending request to backend...
```

**Failure Examples:**
```
Validation failed: Missing plot name or crop name
```
OR
```
Validation failed: Missing location
```
OR
```
Validation failed: User not authenticated
```

### Step 3: Check Network Request
If validation passes, you should see:

```
Sending request to backend...
Response status: 200
Response text: {"success": true, ...}
Response data: {...}
```

**If you see status 500:**
- Backend error, check DigitalOcean logs
- Run `doctl apps logs YOUR_APP_ID` or check dashboard

**If you see status 422:**
- Form data validation error
- Missing required fields in request

### Step 4: Backend Logs
On DigitalOcean, you should see:

```
============================================================
CREATE PLOT MANUAL - REQUEST RECEIVED
============================================================
User ID: abc-123
Plot Name: My Plot
Crop Name: Maize
...
============================================================
Inserting plot into database: {...}
Plot insert SUCCESS - result: [...]
Images inserted successfully: 2 images
============================================================
CREATE PLOT MANUAL - SUCCESS
============================================================
```

## Common Issues & Solutions

### Issue 1: "User not authenticated"
**Symptom:** Validation fails with "User not authenticated"
**Solution:**
1. Check if you're logged in
2. Restart the app
3. Check AuthContext is providing user object
4. Log out and log back in

### Issue 2: "Missing location"
**Symptom:** Validation fails with "Location Required"
**Solution:**
1. Tap "Capture Location" button first
2. Grant location permissions
3. Wait for GPS to acquire position
4. You should see "Location captured successfully!" alert

### Issue 3: Button doesn't respond
**Symptom:** No console logs when tapping button
**Solution:**
1. Check if `loading` state is true (button disabled)
2. Restart Expo dev server with `r` key
3. Clear cache: `npx expo start --clear`
4. Check for JavaScript errors in console

### Issue 4: Backend RLS error
**Symptom:** Backend logs show "new row violates row-level security policy"
**Solution:**
1. Verify `supabase_admin` is being used (already fixed)
2. Check SUPABASE_SERVICE_ROLE_KEY is set in environment variables
3. Run this in Supabase SQL editor:
```sql
-- Temporarily disable RLS for testing
ALTER TABLE digital_plots DISABLE ROW LEVEL SECURITY;
```

### Issue 5: Images not uploading
**Symptom:** Plot created but images missing
**Solution:**
1. Check if images are selected (tap image buttons first)
2. Check file permissions
3. Look for upload errors in backend logs
4. Verify uploads/plots directory exists and is writable

## Quick Test Checklist

- [ ] Can tap "Create Plot" button
- [ ] See debug alert popup
- [ ] See console logs
- [ ] Fill in Plot Name
- [ ] Fill in Crop Name  
- [ ] Tap "Capture Location"
- [ ] See "Location captured successfully!"
- [ ] Tap "Tap to add photo" for initial image
- [ ] Select an image
- [ ] See image preview
- [ ] Tap "Create Plot" again
- [ ] See "All validations passed..." in console
- [ ] See network request logs
- [ ] See success alert OR error message

## Environment Variables Check

Make sure DigitalOcean has these set:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # CRITICAL - must be service role key!
```

## Next Steps

1. **Deploy backend:**
```bash
cd backend
git add .
git commit -m "Fix plot creation with RLS and logging"
git push
```

2. **Test in app:**
- Open CreatePlotScreen
- Tap Create Plot button
- Watch Expo console
- Check for logs and alerts

3. **If still failing:**
- Share the exact console output
- Share any error alerts you see
- Share DigitalOcean backend logs
