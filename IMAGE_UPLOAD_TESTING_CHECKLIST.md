# ✅ Image Upload System - Testing Checklist

## 📋 Pre-Testing Setup

- [ ] Backend server is installed and configured
- [ ] Mobile app dependencies are installed (`npm install`)
- [ ] Test image file available (jpg, png, or webp)
- [ ] Camera permissions configured in app.json
- [ ] API_BASE_URL updated in `mobile/src/services/api.js`

---

## 🔧 Backend Testing

### 1. Server Startup
- [ ] Navigate to backend directory
- [ ] Run `uvicorn app.main:app --reload`
- [ ] Server starts without errors
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Upload endpoints visible in API docs

### 2. Upload Directory
- [ ] `uploads/` directory created automatically
- [ ] Subdirectories exist (plant, leaf, soil, farm, pest, disease, general)
- [ ] Directories have write permissions

### 3. Generic Upload Endpoint
- [ ] POST to `/api/upload/photo` works
- [ ] File uploads successfully
- [ ] Response includes url, filename, category, size, uploaded_at
- [ ] File saved in correct category directory
- [ ] Filename is UUID format

### 4. Category-Specific Endpoints
- [ ] POST to `/api/upload/plant` works
- [ ] POST to `/api/upload/leaf` works
- [ ] POST to `/api/upload/soil` works
- [ ] POST to `/api/upload/farm` works
- [ ] Files saved in correct category folders

### 5. Batch Upload
- [ ] POST to `/api/upload/photos/batch` works with multiple files
- [ ] Response includes `uploaded` and `failed` arrays
- [ ] All valid files uploaded successfully
- [ ] Invalid files properly rejected

### 6. Validation
- [ ] Files >10MB rejected with error
- [ ] Invalid file types (.txt, .pdf, etc.) rejected
- [ ] Invalid category rejected
- [ ] Empty upload rejected

### 7. Statistics
- [ ] GET `/api/upload/stats` returns data
- [ ] Shows count per category
- [ ] Shows total files and size
- [ ] Statistics update after uploads

### 8. Delete
- [ ] DELETE `/api/upload/{category}/{filename}` works
- [ ] File removed from disk
- [ ] 404 returned for non-existent files

### 9. Static File Serving
- [ ] Uploaded files accessible via browser
- [ ] URL format: `http://localhost:8000/uploads/{category}/{filename}`
- [ ] Images display correctly

---

## 📱 Frontend Testing

### 1. Component Rendering
- [ ] ImageUploader component imports without errors
- [ ] Component renders on screen
- [ ] Category icon and label display
- [ ] "Add Photo" button visible

### 2. Permissions
- [ ] Camera permission requested on first camera access
- [ ] Photo library permission requested on first gallery access
- [ ] Permissions persist after granted
- [ ] Proper error shown if permissions denied

### 3. Camera Integration
- [ ] "Take Photo" option opens camera
- [ ] Camera preview displays
- [ ] Photo captured successfully
- [ ] Preview shows captured image
- [ ] "Retake" button works

### 4. Gallery Integration
- [ ] "Choose from Gallery" opens photo picker
- [ ] Can select single image (when multiple=false)
- [ ] Can select multiple images (when multiple=true)
- [ ] Selected images show in preview
- [ ] Max images limit enforced

### 5. Image Preview
- [ ] Thumbnails display correctly
- [ ] Horizontal scroll works with multiple images
- [ ] Remove button (X) visible on each image
- [ ] Remove button deletes specific image
- [ ] Image counter shows (e.g., "3/5")

### 6. Upload Functionality
- [ ] "Upload" button enabled when images selected
- [ ] Upload starts on button press
- [ ] Loading indicator shows during upload
- [ ] Success notification shows after upload
- [ ] Uploaded badge (checkmark) appears on images
- [ ] Upload button disabled for already uploaded images

### 7. Error Handling
- [ ] Network error shown if backend offline
- [ ] File too large error shown
- [ ] Upload failure handled gracefully
- [ ] onUploadError callback triggered

### 8. Multiple Image Support
- [ ] Can add multiple images
- [ ] "Add More" button works
- [ ] Max images limit prevents adding beyond max
- [ ] Batch upload works for multiple images

### 9. Category-Specific Features
- [ ] Plant category shows plant icon and green color
- [ ] Leaf category shows leaf icon and green color
- [ ] Soil category shows terrain icon and brown color
- [ ] Farm category shows barn icon and blue color
- [ ] Category-specific tips display

### 10. Clear All
- [ ] "Clear All" icon button visible
- [ ] Confirmation dialog appears
- [ ] All images removed when confirmed
- [ ] Component resets to initial state

---

## 🎬 Integration Testing

### 1. Soil Analysis Screen
- [ ] Wet soil uploader works
- [ ] Dry soil uploader works
- [ ] Both uploads required before analysis
- [ ] Analysis button enabled when both uploaded
- [ ] Uploaded URLs passed to API correctly
- [ ] Results display after analysis

### 2. Pest Scan Screen
- [ ] Leaf image uploader works
- [ ] Multiple leaves can be uploaded
- [ ] Scan works with uploaded images
- [ ] Detection results display correctly

### 3. Farm Registration
- [ ] Farm image uploader works
- [ ] Multiple farm photos supported
- [ ] Photos included in registration data
- [ ] Registration succeeds with images

### 4. Expert Help
- [ ] Problem photo uploader works
- [ ] Multiple photos supported
- [ ] Photos included in help request
- [ ] Request submitted successfully

### 5. Village Groups Posts
- [ ] Post photo uploader works
- [ ] Photo displayed in post preview
- [ ] Photo included when post created
- [ ] Photo visible in post feed

---

## 🔄 End-to-End Testing

### Scenario 1: Complete Soil Analysis
1. [ ] Open Soil Analysis screen
2. [ ] Upload wet soil photo from camera
3. [ ] Upload dry soil photo from gallery
4. [ ] Click "Analyze Soil with AI"
5. [ ] Verify both photos uploaded to backend
6. [ ] Verify analysis results returned
7. [ ] Verify photos accessible via URLs

### Scenario 2: Multi-Image Pest Scan
1. [ ] Open Pest Scan screen
2. [ ] Take 3 leaf photos using camera
3. [ ] Upload all 3 photos in batch
4. [ ] Verify all uploaded successfully
5. [ ] Run pest scan with uploaded images
6. [ ] Verify scan results with multiple images

### Scenario 3: Farm Registration with Photos
1. [ ] Open Add Farm screen
2. [ ] Fill in farm details
3. [ ] Add 5 farm photos from gallery
4. [ ] Upload all photos
5. [ ] Submit farm registration
6. [ ] Verify farm created with photos
7. [ ] Check farm detail shows photos

---

## 🧪 Edge Case Testing

### Backend Edge Cases
- [ ] Upload with missing file
- [ ] Upload with empty file
- [ ] Upload very large file (>10MB)
- [ ] Upload with invalid extension
- [ ] Upload with no extension
- [ ] Batch upload with mixed valid/invalid files
- [ ] Delete non-existent file
- [ ] Access file in wrong category
- [ ] Concurrent uploads from multiple users

### Frontend Edge Cases
- [ ] Deny camera permission
- [ ] Deny photo library permission
- [ ] Network disconnected during upload
- [ ] Upload interrupted mid-way
- [ ] Add images beyond max limit
- [ ] Upload same image twice
- [ ] Clear images during upload
- [ ] Navigate away during upload
- [ ] Low memory situation
- [ ] Slow network connection

---

## 📊 Performance Testing

### Backend Performance
- [ ] Single 5MB image upload < 3 seconds
- [ ] Batch 10 images upload < 10 seconds
- [ ] Statistics query < 100ms
- [ ] File deletion < 50ms
- [ ] Concurrent uploads (5 users) handled

### Frontend Performance
- [ ] Camera opens < 1 second
- [ ] Gallery opens < 1 second
- [ ] Image preview renders < 500ms
- [ ] Upload progress responsive
- [ ] No memory leaks after multiple uploads

---

## 🔒 Security Testing

- [ ] JWT token required for authenticated endpoints
- [ ] Unauthorized requests rejected
- [ ] SQL injection attempts blocked
- [ ] Path traversal attempts blocked
- [ ] File type spoofing detected
- [ ] CORS configured correctly
- [ ] File size limits enforced
- [ ] Category validation enforced

---

## 📱 Device Testing

### Android
- [ ] Pixel/Samsung phone (tested)
- [ ] Camera works
- [ ] Gallery picker works
- [ ] Permissions work
- [ ] Uploads succeed

### iOS
- [ ] iPhone (tested)
- [ ] Camera works
- [ ] Photo picker works
- [ ] Permissions work
- [ ] Uploads succeed

### Tablets
- [ ] Android tablet (if available)
- [ ] iPad (if available)
- [ ] Layout responsive
- [ ] All features work

---

## 📝 Documentation Review

- [ ] IMAGE_UPLOAD_GUIDE.md complete and accurate
- [ ] IMAGE_UPLOAD_QUICKSTART.md helpful
- [ ] IMAGE_UPLOAD_SUMMARY.md up to date
- [ ] IMAGE_UPLOAD_README.md clear
- [ ] Code comments adequate
- [ ] API endpoints documented
- [ ] Component props documented

---

## 🐛 Bug Tracking

### Issues Found
| Issue | Severity | Status | Notes |
|-------|----------|--------|-------|
|       |          |        |       |
|       |          |        |       |

---

## ✅ Sign-Off

### Backend Testing
- Tested by: _______________
- Date: _______________
- Status: ☐ Pass ☐ Fail ☐ Needs Work
- Notes: _______________

### Frontend Testing
- Tested by: _______________
- Date: _______________
- Status: ☐ Pass ☐ Fail ☐ Needs Work
- Notes: _______________

### Integration Testing
- Tested by: _______________
- Date: _______________
- Status: ☐ Pass ☐ Fail ☐ Needs Work
- Notes: _______________

---

## 🚀 Production Readiness

- [ ] All tests passed
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Backend deployed
- [ ] Mobile app updated
- [ ] API_BASE_URL configured for production
- [ ] Monitoring configured

---

**Ready for Production?** ☐ Yes ☐ No

**Date Ready:** _______________

**Approved By:** _______________
