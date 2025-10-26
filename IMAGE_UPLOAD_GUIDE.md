# Image Upload System Documentation

## Overview

The AgroShield Image Upload System provides a comprehensive solution for uploading and managing images of plants, leaves, soil, and farm photos. The system includes:

- **Backend**: FastAPI-based upload API with categorization and validation
- **Frontend**: Reusable React Native component with camera/gallery support
- **Categories**: plant, leaf, soil, farm, pest, disease, general

---

## Backend API

### Base URL
```
http://localhost:8000/api/upload
```

### Endpoints

#### 1. Upload Single Photo
```http
POST /api/upload/photo
Content-Type: multipart/form-data

Parameters:
- photo: File (required) - Image file
- category: String (optional) - Image category (default: 'general')

Response:
{
  "url": "/uploads/plant/uuid.jpg",
  "filename": "uuid.jpg",
  "category": "plant",
  "size": 1234567,
  "uploaded_at": "2025-10-24T10:30:00"
}
```

#### 2. Upload Plant Image
```http
POST /api/upload/plant
Content-Type: multipart/form-data

Parameters:
- photo: File (required) - Plant image

Response: Same as single photo
```

#### 3. Upload Leaf Image
```http
POST /api/upload/leaf
Content-Type: multipart/form-data

Parameters:
- photo: File (required) - Leaf image

Response: Same as single photo
```

#### 4. Upload Soil Image
```http
POST /api/upload/soil
Content-Type: multipart/form-data

Parameters:
- photo: File (required) - Soil image

Response: Same as single photo
```

#### 5. Upload Farm Image
```http
POST /api/upload/farm
Content-Type: multipart/form-data

Parameters:
- photo: File (required) - Farm/field image

Response: Same as single photo
```

#### 6. Batch Upload
```http
POST /api/upload/photos/batch
Content-Type: multipart/form-data

Parameters:
- photos: File[] (required) - Array of images (max 10)
- category: String (optional) - Category for all images

Response:
{
  "uploaded": [
    {
      "url": "/uploads/plant/uuid1.jpg",
      "filename": "uuid1.jpg",
      "category": "plant",
      "size": 1234567,
      "uploaded_at": "2025-10-24T10:30:00"
    }
  ],
  "failed": [
    {
      "filename": "invalid.txt",
      "error": "Invalid file type"
    }
  ]
}
```

#### 7. Delete Photo
```http
DELETE /api/upload/{category}/{filename}

Response:
{
  "message": "File deleted successfully"
}
```

#### 8. Get Upload Statistics
```http
GET /api/upload/stats

Response:
{
  "categories": {
    "plant": {
      "count": 150,
      "size_bytes": 12345678,
      "size_mb": 11.77
    },
    "leaf": { ... },
    "soil": { ... }
  },
  "total": {
    "files": 450,
    "size_bytes": 37654321,
    "size_mb": 35.9
  }
}
```

### Configuration

#### File Validation
- **Allowed formats**: `.jpg`, `.jpeg`, `.png`, `.webp`
- **Max file size**: 10MB
- **Content type**: Must be `image/*`

#### Storage Structure
```
uploads/
├── plant/
├── leaf/
├── soil/
├── farm/
├── pest/
├── disease/
└── general/
```

---

## Frontend API (React Native)

### Import
```javascript
import { uploadAPI } from '../services/api';
```

### Methods

#### 1. Upload Photo (Generic)
```javascript
const result = await uploadAPI.uploadPhoto(imageUri, 'plant');
// Returns: { url, filename, category, size, uploaded_at }
```

#### 2. Upload Plant Image
```javascript
const result = await uploadAPI.uploadPlantImage(imageUri);
```

#### 3. Upload Leaf Image
```javascript
const result = await uploadAPI.uploadLeafImage(imageUri);
```

#### 4. Upload Soil Image
```javascript
const result = await uploadAPI.uploadSoilImage(imageUri);
```

#### 5. Upload Farm Image
```javascript
const result = await uploadAPI.uploadFarmImage(imageUri);
```

#### 6. Batch Upload
```javascript
const result = await uploadAPI.uploadPhotoBatch([uri1, uri2, uri3], 'plant');
// Returns: { uploaded: [...], failed: [...] }
```

#### 7. Delete Photo
```javascript
await uploadAPI.deletePhoto('plant', 'uuid.jpg');
```

#### 8. Get Statistics
```javascript
const stats = await uploadAPI.getUploadStats();
```

---

## ImageUploader Component

### Overview
A reusable React Native component for uploading images with camera/gallery support.

### Import
```javascript
import ImageUploader from '../components/ImageUploader';
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `category` | string | 'general' | Image category (plant, leaf, soil, farm, general) |
| `multiple` | boolean | false | Allow multiple image selection |
| `maxImages` | number | 5 | Maximum number of images |
| `onUploadComplete` | function | - | Callback with uploaded image data |
| `onUploadError` | function | - | Callback with error message |
| `previewSize` | number | 150 | Size of image preview in pixels |
| `showPreview` | boolean | true | Show image previews |
| `style` | object | - | Custom container style |

### Usage Examples

#### Single Plant Image Upload
```javascript
<ImageUploader
  category="plant"
  onUploadComplete={(data) => console.log('Uploaded:', data)}
  onUploadError={(error) => Alert.alert('Error', error)}
/>
```

#### Multiple Leaf Images
```javascript
<ImageUploader
  category="leaf"
  multiple={true}
  maxImages={5}
  previewSize={120}
  onUploadComplete={(data) => {
    console.log(`Uploaded ${data.length} images`);
  }}
/>
```

#### Soil Analysis (Single Image)
```javascript
<ImageUploader
  category="soil"
  multiple={false}
  previewSize={200}
  onUploadComplete={(data) => {
    setSoilImageUrl(data[0].url);
  }}
/>
```

#### Custom Styling
```javascript
<ImageUploader
  category="farm"
  multiple={true}
  maxImages={10}
  style={{ backgroundColor: '#f5f5f5', padding: 20 }}
  onUploadComplete={handleUpload}
/>
```

### Features

1. **Camera Integration**
   - Take photos directly from camera
   - Auto-adjusts quality to 0.8
   - 4:3 aspect ratio with editing

2. **Gallery Selection**
   - Pick from photo library
   - Multiple selection support
   - Respects max image limits

3. **Image Previews**
   - Scrollable horizontal preview
   - Remove individual images
   - Upload status indicators
   - Uploaded badge (checkmark)

4. **Upload Management**
   - Individual or batch upload
   - Progress indication
   - Success/failure notifications
   - Prevents duplicate uploads

5. **Validation**
   - Max file size enforcement
   - Format validation
   - Image count limits
   - Permission handling

6. **User Experience**
   - Category-specific icons and colors
   - Helpful tips for each category
   - Clear button to remove all
   - Disabled states during upload

---

## Integration Examples

### 1. Pest Scan Screen
```javascript
import ImageUploader from '../components/ImageUploader';

const PestScanScreen = () => {
  const [plantImages, setPlantImages] = useState([]);

  const handleUpload = async (uploadedData) => {
    setPlantImages(uploadedData);
    
    // Use uploaded images for pest detection
    const imageUrls = uploadedData.map(img => img.url);
    const result = await pestAPI.scanPlant({
      image_urls: imageUrls,
      symptoms: symptoms,
    });
  };

  return (
    <View>
      <ImageUploader
        category="leaf"
        multiple={true}
        maxImages={3}
        onUploadComplete={handleUpload}
      />
    </View>
  );
};
```

### 2. Soil Analysis Screen
```javascript
const SoilAnalysisScreen = () => {
  const [wetSoilImage, setWetSoilImage] = useState(null);
  const [drySoilImage, setDrySoilImage] = useState(null);

  return (
    <View>
      <Text>Wet Soil Sample</Text>
      <ImageUploader
        category="soil"
        onUploadComplete={(data) => setWetSoilImage(data[0])}
      />

      <Text>Dry Soil Sample</Text>
      <ImageUploader
        category="soil"
        onUploadComplete={(data) => setDrySoilImage(data[0])}
      />

      <Button
        onPress={() => analyzeSoil(wetSoilImage, drySoilImage)}
        disabled={!wetSoilImage || !drySoilImage}
      >
        Analyze Soil
      </Button>
    </View>
  );
};
```

### 3. Farm Registration
```javascript
const AddFarmScreen = () => {
  const [farmImages, setFarmImages] = useState([]);

  const handleRegister = async () => {
    const result = await farmAPI.registerFarm({
      name: farmName,
      location: location,
      images: farmImages.map(img => img.url),
    });
  };

  return (
    <View>
      <ImageUploader
        category="farm"
        multiple={true}
        maxImages={10}
        onUploadComplete={setFarmImages}
      />

      <Button onPress={handleRegister}>
        Register Farm
      </Button>
    </View>
  );
};
```

---

## Error Handling

### Backend Errors
```python
# Invalid file type
{"detail": "Invalid file type. Allowed: .jpg, .jpeg, .png, .webp"}

# File too large
{"detail": "File too large. Max size: 10MB"}

# Invalid category
{"detail": "Invalid category. Allowed: plant, leaf, soil, farm, pest, disease, general"}

# File not found
{"detail": "File not found"}
```

### Frontend Error Handling
```javascript
<ImageUploader
  category="plant"
  onUploadError={(error) => {
    console.error('Upload error:', error);
    Alert.alert('Upload Failed', error);
  }}
  onUploadComplete={(data) => {
    console.log('Success:', data);
  }}
/>
```

---

## Permissions Required

### iOS (Info.plist)
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to take photos of plants and soil</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>We need photo library access to select images</string>
```

### Android (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

---

## Best Practices

### 1. Image Quality
- Use camera for fresh images (higher quality)
- Take photos in good lighting
- Keep images focused and clear
- For leaves: capture affected areas up close
- For soil: capture representative samples

### 2. Performance
- Use batch upload for multiple images
- Compress images before upload (quality: 0.8)
- Limit max images per upload
- Clear uploaded images after processing

### 3. User Experience
- Show upload progress
- Display success/failure feedback
- Allow image preview before upload
- Provide category-specific tips
- Handle permission requests gracefully

### 4. Security
- Validate file types on both client and server
- Enforce file size limits
- Sanitize filenames
- Use unique filenames (UUID)
- Implement authentication for uploads

---

## Testing

### Backend Testing
```bash
# Test single upload
curl -X POST http://localhost:8000/api/upload/plant \
  -F "photo=@test_plant.jpg"

# Test batch upload
curl -X POST http://localhost:8000/api/upload/photos/batch \
  -F "photos=@plant1.jpg" \
  -F "photos=@plant2.jpg" \
  -F "category=plant"

# Get stats
curl http://localhost:8000/api/upload/stats
```

### Frontend Testing
```javascript
// Test component rendering
import { render } from '@testing-library/react-native';

test('renders ImageUploader', () => {
  const { getByText } = render(
    <ImageUploader category="plant" />
  );
  expect(getByText('Plant Photos')).toBeTruthy();
});
```

---

## Troubleshooting

### Common Issues

1. **Upload fails with "Network Error"**
   - Check API_BASE_URL in api.js
   - Ensure backend server is running
   - Verify CORS settings

2. **Permission denied**
   - Request permissions before using camera
   - Check Info.plist/AndroidManifest.xml
   - Guide users to settings if denied

3. **Images not displaying**
   - Verify upload directory exists
   - Check file permissions
   - Ensure static file serving is configured

4. **Large file uploads timeout**
   - Increase axios timeout (default: 30s)
   - Compress images before upload
   - Use batch upload for multiple files

---

## Future Enhancements

1. **Image Compression**: Add client-side compression before upload
2. **Progress Tracking**: Show upload progress percentage
3. **Cloud Storage**: Integrate with AWS S3 or Google Cloud Storage
4. **Image Editing**: Add filters, crop, rotate before upload
5. **Metadata**: Capture GPS, timestamp, device info
6. **Caching**: Cache uploaded images for offline viewing
7. **Analytics**: Track upload success rates by category

---

## License

MIT License - AgroShield 2025
