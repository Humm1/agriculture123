# 📸 AgroShield Image Upload System

A comprehensive image upload solution for plants, leaves, and soil analysis with AI integration.

## 🌟 Features

### Backend
- ✅ FastAPI-based upload API with 8 endpoints
- ✅ 7 image categories (plant, leaf, soil, farm, pest, disease, general)
- ✅ File validation (type, size, content)
- ✅ Batch upload (up to 10 files)
- ✅ Upload statistics
- ✅ Image deletion
- ✅ Automatic directory organization

### Frontend
- ✅ Reusable React Native component
- ✅ Camera & gallery integration
- ✅ Single & multiple image upload
- ✅ Image previews with thumbnails
- ✅ Upload progress tracking
- ✅ Category-specific styling
- ✅ Error handling & validation

---

## 🚀 Quick Start

### Backend

```bash
# Start the server
cd backend
uvicorn app.main:app --reload

# The upload API is now available at:
# http://localhost:8000/api/upload
```

### Frontend

```javascript
import ImageUploader from '../components/ImageUploader';

function MyScreen() {
  return (
    <ImageUploader
      category="plant"
      multiple={true}
      maxImages={5}
      onUploadComplete={(data) => console.log('Uploaded:', data)}
      onUploadError={(error) => alert(error)}
    />
  );
}
```

---

## 📚 Documentation

- **[IMAGE_UPLOAD_GUIDE.md](./IMAGE_UPLOAD_GUIDE.md)** - Complete API reference and usage guide
- **[IMAGE_UPLOAD_QUICKSTART.md](./IMAGE_UPLOAD_QUICKSTART.md)** - Quick reference for common patterns
- **[IMAGE_UPLOAD_SUMMARY.md](./IMAGE_UPLOAD_SUMMARY.md)** - Implementation overview

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/photo` | POST | Upload with custom category |
| `/api/upload/plant` | POST | Upload plant images |
| `/api/upload/leaf` | POST | Upload leaf images |
| `/api/upload/soil` | POST | Upload soil images |
| `/api/upload/farm` | POST | Upload farm images |
| `/api/upload/photos/batch` | POST | Upload multiple images |
| `/api/upload/{category}/{filename}` | DELETE | Delete image |
| `/api/upload/stats` | GET | Get upload statistics |

---

## 📱 Component Usage

### Basic Usage

```javascript
<ImageUploader
  category="plant"
  onUploadComplete={(data) => console.log(data)}
/>
```

### Multiple Images

```javascript
<ImageUploader
  category="leaf"
  multiple={true}
  maxImages={5}
  onUploadComplete={(data) => handleUpload(data)}
/>
```

### Custom Styling

```javascript
<ImageUploader
  category="soil"
  previewSize={200}
  style={{ padding: 20, backgroundColor: '#f5f5f5' }}
  onUploadComplete={(data) => analyzeSoil(data)}
/>
```

---

## 🎨 Image Categories

| Category | Icon | Use Case |
|----------|------|----------|
| `plant` | 🌱 | Full plant photos for health assessment |
| `leaf` | 🍃 | Leaf close-ups for disease detection |
| `soil` | 🌍 | Soil samples for texture analysis |
| `farm` | 🌾 | Field photos and landscapes |
| `pest` | 🐛 | Pest identification images |
| `disease` | 🦠 | Disease symptom photos |
| `general` | 📷 | Miscellaneous images |

---

## 💡 Integration Examples

### Soil Analysis (Wet & Dry Samples)

```javascript
function SoilAnalysis() {
  const [wetSoil, setWetSoil] = useState(null);
  const [drySoil, setDrySoil] = useState(null);

  return (
    <View>
      <Text>Wet Soil Sample</Text>
      <ImageUploader
        category="soil"
        onUploadComplete={(data) => setWetSoil(data[0])}
      />

      <Text>Dry Soil Sample</Text>
      <ImageUploader
        category="soil"
        onUploadComplete={(data) => setDrySoil(data[0])}
      />

      <Button
        disabled={!wetSoil || !drySoil}
        onPress={() => analyzeSoil(wetSoil.url, drySoil.url)}
      >
        Analyze Soil
      </Button>
    </View>
  );
}
```

### Pest Detection

```javascript
<ImageUploader
  category="leaf"
  multiple={true}
  maxImages={3}
  onUploadComplete={async (data) => {
    const result = await pestAPI.scanPlant({
      image_urls: data.map(img => img.url)
    });
    showResults(result);
  }}
/>
```

### Farm Registration

```javascript
<ImageUploader
  category="farm"
  multiple={true}
  maxImages={10}
  onUploadComplete={(data) => {
    setFarmImages(data.map(img => img.url));
  }}
/>
```

---

## 🧪 Testing

### Backend Testing

```bash
# Using the test script
python test_upload.py

# Or manually with curl
curl -X POST http://localhost:8000/api/upload/plant \
  -F "photo=@test.jpg"

# Get statistics
curl http://localhost:8000/api/upload/stats
```

### Frontend Testing

```bash
cd mobile
npm start

# Navigate to ImageUploadDemoScreen to test all features
```

---

## ⚙️ Configuration

### Backend

```python
# backend/app/routes/upload.py
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### Frontend

```javascript
// mobile/src/services/api.js
const API_BASE_URL = 'http://localhost:8000/api';
```

---

## 📂 File Structure

```
agroshield/
├── backend/
│   ├── app/
│   │   ├── main.py (upload router added)
│   │   └── routes/
│   │       └── upload.py (NEW - 330 lines)
│   └── uploads/ (auto-created)
│       ├── plant/
│       ├── leaf/
│       ├── soil/
│       ├── farm/
│       ├── pest/
│       ├── disease/
│       └── general/
│
└── mobile/
    └── src/
        ├── services/
        │   └── api.js (uploadAPI added)
        └── components/
            └── ImageUploader.js (NEW - 450 lines)
```

---

## 🔐 Security

- ✅ File type validation (server-side)
- ✅ File size limits (10MB)
- ✅ Content type validation
- ✅ Unique filenames (UUID)
- ✅ Category-based isolation
- ✅ JWT authentication (existing)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Network Error | Check API_BASE_URL, ensure backend is running |
| Permission Denied | Grant camera/photo access in device settings |
| File Too Large | Images must be <10MB |
| Invalid File Type | Only jpg, png, webp supported |
| Upload Timeout | Check network connection |

---

## 📊 Performance

- Max file size: **10MB**
- Max batch size: **10 files**
- Image quality: **0.8 (80%)**
- Supported formats: **jpg, jpeg, png, webp**
- Categories: **7**
- Average upload time: **2-5 seconds per image**

---

## 🎯 Use Cases

### 1. Plant Health Assessment
Upload full plant photos for AI-powered health analysis.

### 2. Disease Detection
Upload close-up leaf photos to identify diseases and pests.

### 3. Soil Analysis
Upload wet and dry soil samples for texture and nutrient analysis.

### 4. Farm Management
Document your fields with landscape photos.

### 5. Expert Consultation
Share problem photos with agricultural experts.

### 6. Community Sharing
Post photos in village groups to share knowledge.

---

## 🚀 Future Enhancements

- [ ] Image compression before upload
- [ ] Progress percentage tracking
- [ ] Cloud storage (AWS S3, Google Cloud)
- [ ] Image editing (crop, rotate, filters)
- [ ] EXIF metadata (GPS, timestamp)
- [ ] Offline upload queue
- [ ] Image caching
- [ ] Upload analytics

---

## 📝 Files Included

1. **Backend**
   - `backend/app/routes/upload.py` - Upload API (330 lines)
   - `backend/app/main.py` - Updated with upload router

2. **Frontend**
   - `mobile/src/services/api.js` - Updated with uploadAPI
   - `mobile/src/components/ImageUploader.js` - Reusable component (450 lines)
   - `mobile/src/screens/ImageUploadDemoScreen.js` - Demo screen

3. **Documentation**
   - `IMAGE_UPLOAD_GUIDE.md` - Complete guide (500+ lines)
   - `IMAGE_UPLOAD_QUICKSTART.md` - Quick reference
   - `IMAGE_UPLOAD_SUMMARY.md` - Implementation summary
   - `IMAGE_UPLOAD_README.md` - This file

4. **Testing**
   - `test_upload.py` - Backend test script

---

## 🤝 Contributing

To extend the image upload system:

1. Add new categories in `backend/app/routes/upload.py`
2. Update category info in `ImageUploader.js`
3. Create category-specific endpoints if needed
4. Update documentation

---

## 📄 License

MIT License - AgroShield 2025

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section in `IMAGE_UPLOAD_GUIDE.md`
2. Review example implementations in demo screens
3. Test with `test_upload.py` script
4. Check console logs for detailed error messages

---

**Happy Uploading! 📸🌱**
