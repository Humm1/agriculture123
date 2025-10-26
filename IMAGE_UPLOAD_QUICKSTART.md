# Image Upload Quick Reference

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
# Install dependencies (if needed)
pip install fastapi python-multipart

# Run server
uvicorn app.main:app --reload
```

### Frontend Usage
```javascript
import ImageUploader from '../components/ImageUploader';

// Single plant image
<ImageUploader
  category="plant"
  onUploadComplete={(data) => console.log(data)}
/>

// Multiple leaf images
<ImageUploader
  category="leaf"
  multiple={true}
  maxImages={5}
  onUploadComplete={(data) => console.log(data)}
/>
```

## 📁 Categories

| Category | Icon | Use Case | Example |
|----------|------|----------|---------|
| `plant` | 🌱 | Full plant photos | Whole plant images for health assessment |
| `leaf` | 🍃 | Leaf close-ups | Disease/pest detection on leaves |
| `soil` | 🌍 | Soil samples | Soil texture and nutrient analysis |
| `farm` | 🌾 | Field photos | Farm landscapes, field boundaries |
| `pest` | 🐛 | Pest images | Specific pest identification |
| `disease` | 🦠 | Disease symptoms | Disease identification |
| `general` | 📷 | Other images | Miscellaneous photos |

## 🔧 API Endpoints

```
POST /api/upload/photo          # Generic upload with category
POST /api/upload/plant          # Plant images
POST /api/upload/leaf           # Leaf images
POST /api/upload/soil           # Soil images
POST /api/upload/farm           # Farm images
POST /api/upload/photos/batch   # Multiple images
DELETE /api/upload/{category}/{filename}  # Delete image
GET /api/upload/stats           # Upload statistics
```

## 💡 Component Props

```javascript
<ImageUploader
  category="plant"        // Image category
  multiple={false}        // Allow multiple images
  maxImages={5}          // Max number of images
  previewSize={150}      // Preview size in pixels
  showPreview={true}     // Show image previews
  onUploadComplete={fn}  // Success callback
  onUploadError={fn}     // Error callback
  style={{}}             // Custom styles
/>
```

## 📝 Common Patterns

### Pattern 1: Single Image for Analysis
```javascript
const [soilImage, setSoilImage] = useState(null);

<ImageUploader
  category="soil"
  onUploadComplete={(data) => setSoilImage(data[0])}
/>

<Button 
  disabled={!soilImage}
  onPress={() => analyzeSoil(soilImage.url)}
>
  Analyze
</Button>
```

### Pattern 2: Multiple Images Collection
```javascript
const [leafImages, setLeafImages] = useState([]);

<ImageUploader
  category="leaf"
  multiple={true}
  maxImages={5}
  onUploadComplete={(data) => {
    setLeafImages(prev => [...prev, ...data]);
  }}
/>

<Text>Collected {leafImages.length} images</Text>
```

### Pattern 3: Sequential Uploads (Wet/Dry Soil)
```javascript
const [wetSoil, setWetSoil] = useState(null);
const [drySoil, setDrySoil] = useState(null);

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
</View>
```

## ⚠️ Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Network Error | Backend not running | Start backend server |
| Permission Denied | No camera access | Request permissions |
| File too large | >10MB | Compress or resize image |
| Invalid file type | Not jpg/png | Use supported formats |
| Upload timeout | Slow network | Check connection |

## 🔐 Permissions Setup

**package.json (Expo)**
```json
{
  "expo": {
    "plugins": [
      [
        "expo-camera",
        {
          "cameraPermission": "Allow AgroShield to take photos of plants"
        }
      ],
      [
        "expo-image-picker",
        {
          "photosPermission": "Allow AgroShield to access your photos"
        }
      ]
    ]
  }
}
```

## 📊 Upload Statistics

Get upload stats:
```javascript
const stats = await uploadAPI.getUploadStats();
// Returns:
{
  categories: {
    plant: { count: 150, size_mb: 11.77 },
    leaf: { count: 230, size_mb: 18.45 },
    soil: { count: 89, size_mb: 7.23 }
  },
  total: { files: 469, size_mb: 37.45 }
}
```

## 🎨 Customization

### Custom Category Colors
```javascript
// In ImageUploader component, modify categoryInfo:
const categoryInfo = {
  custom: { 
    icon: 'star', 
    color: '#FF5722', 
    label: 'Custom Photos' 
  },
};
```

### Custom Styling
```javascript
<ImageUploader
  category="plant"
  style={{
    backgroundColor: '#f0f0f0',
    borderRadius: 12,
    padding: 20,
    margin: 10,
  }}
/>
```

## 🔄 Integration Examples

### With Pest Scan
```javascript
const [pestImages, setPestImages] = useState([]);

<ImageUploader
  category="leaf"
  multiple={true}
  maxImages={3}
  onUploadComplete={async (data) => {
    setPestImages(data);
    const result = await pestAPI.scanPlant({
      image_urls: data.map(img => img.url)
    });
  }}
/>
```

### With Soil Analysis
```javascript
<ImageUploader
  category="soil"
  onUploadComplete={async (data) => {
    const result = await farmAPI.addSoilSnapshot(fieldId, {
      wet: data[0].url,
      dry: data[1]?.url
    });
  }}
/>
```

### With Farm Registration
```javascript
<ImageUploader
  category="farm"
  multiple={true}
  maxImages={10}
  onUploadComplete={(data) => {
    setFarmData(prev => ({
      ...prev,
      images: data.map(img => img.url)
    }));
  }}
/>
```

## 📱 Testing

### Test Backend
```bash
# Upload test
curl -X POST http://localhost:8000/api/upload/plant \
  -F "photo=@test.jpg"

# Get stats
curl http://localhost:8000/api/upload/stats
```

### Test Frontend
```javascript
// Component test
import { render, fireEvent } from '@testing-library/react-native';

test('shows add photo button', () => {
  const { getByText } = render(<ImageUploader category="plant" />);
  expect(getByText('Add Photo')).toBeTruthy();
});
```

## 🚨 Troubleshooting

**Images not uploading?**
1. Check API_BASE_URL in `mobile/src/services/api.js`
2. Verify backend is running on correct port
3. Check network connectivity
4. Look at console logs for errors

**Camera not working?**
1. Request permissions in app
2. Check expo-camera installation
3. Test on physical device (simulator may not work)

**Preview not showing?**
1. Verify URI is valid
2. Check showPreview prop is true
3. Look for console errors

## 📚 Resources

- **Backend Code**: `backend/app/routes/upload.py`
- **Frontend Service**: `mobile/src/services/api.js`
- **Component**: `mobile/src/components/ImageUploader.js`
- **Demo Screen**: `mobile/src/screens/ImageUploadDemoScreen.js`
- **Full Docs**: `IMAGE_UPLOAD_GUIDE.md`

---

**Need Help?** Check the full documentation in `IMAGE_UPLOAD_GUIDE.md`
