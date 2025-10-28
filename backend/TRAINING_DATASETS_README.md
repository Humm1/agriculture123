# AgroShield Training Datasets

Comprehensive pretrained datasets for all AgroShield AI models.

## 📦 Generated Datasets

### 1. **Pest Detection** (Image Classification)
- **Classes**: 7 (aphids, whiteflies, armyworms, leaf_miners, thrips, cutworms, healthy)
- **Images**: 1,050
- **Resolution**: 224x224
- **Use Case**: CNN-based pest identification
- **Model**: MobileNet V3 / EfficientNet

### 2. **Disease Detection** (Image Classification)
- **Classes**: 7 (early_blight, late_blight, leaf_curl, powdery_mildew, rust, bacterial_spot, healthy)
- **Images**: 1,050
- **Resolution**: 224x224
- **Use Case**: Plant disease diagnosis
- **Model**: MobileNet V3 / ResNet

### 3. **Storage Assessment** (Image Classification)
- **Classes**: 5 (excellent, good, fair, poor, spoiled)
- **Images**: 750
- **Resolution**: 224x224
- **Additional Data**: Temperature, humidity, storage duration
- **Use Case**: Post-harvest quality control
- **Model**: EfficientNet B0

### 4. **Soil Diagnostics** (Image Classification + Regression)
- **Classes**: 6 (sandy, loamy, clay, silty, peaty, chalky)
- **Images**: 720
- **Resolution**: 224x224
- **Soil Properties**: pH, NPK, organic matter, moisture
- **Use Case**: Soil type identification and nutrient analysis
- **Model**: EfficientNet B0

### 5. **Plant Health** (Multi-class Classification)
- **Classes**: 7 (seedling, vegetative, flowering, fruiting, mature, stressed, diseased)
- **Images**: 700
- **Resolution**: 224x224
- **Metrics**: Health score, growth stage, leaf count
- **Use Case**: Growth tracking and health monitoring
- **Model**: MobileNet V3

### 6. **Climate Prediction** (Time Series Forecasting)
- **Records**: 730 (2 years daily data)
- **Features**: 10 (temperature, humidity, rainfall, wind, pressure, cloud cover, UV, soil temp, ET)
- **Sequence Length**: 30 days
- **Prediction Horizon**: 7 days
- **Use Case**: Weather forecasting for farm planning
- **Model**: LSTM / GRU

### 7. **Yield Prediction** (Regression)
- **Records**: 1,000
- **Crops**: 7 (maize, wheat, rice, tomatoes, potatoes, beans, cassava)
- **Features**: 14 (area, soil quality, irrigation, fertilizer, climate factors, pest/disease pressure)
- **Target**: Yield per hectare (tons)
- **Use Case**: Harvest prediction and planning
- **Model**: Random Forest / XGBoost

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install pillow pandas numpy

# Or use the provided requirements
cd backend
pip install -r requirements-datasets.txt
```

### Generate Datasets

```bash
cd backend
python generate_training_datasets.py
```

This will create:
```
backend/training_data/
├── pest_detection/
│   ├── aphids/
│   ├── whiteflies/
│   ├── armyworms/
│   ├── ...
│   └── metadata.json
├── disease_detection/
│   ├── early_blight/
│   ├── late_blight/
│   ├── ...
│   └── metadata.json
├── storage_assessment/
├── soil_diagnostics/
├── plant_health/
├── climate_prediction/
│   ├── climate_timeseries.csv
│   └── metadata.json
├── yield_prediction/
│   ├── yield_prediction.csv
│   └── metadata.json
└── dataset_summary.json
```

## 📊 Dataset Statistics

| Dataset | Type | Images/Records | Classes | Size |
|---------|------|----------------|---------|------|
| Pest Detection | Image | 1,050 | 7 | ~30 MB |
| Disease Detection | Image | 1,050 | 7 | ~30 MB |
| Storage Assessment | Image | 750 | 5 | ~20 MB |
| Soil Diagnostics | Image | 720 | 6 | ~20 MB |
| Plant Health | Image | 700 | 7 | ~20 MB |
| Climate Prediction | CSV | 730 | - | ~100 KB |
| Yield Prediction | CSV | 1,000 | - | ~150 KB |
| **TOTAL** | | **5,270** | **39** | **~120 MB** |

## 🎯 Training Models

### Image Classification Models

```python
# Example: Train pest detection model
from app.services.model_training import ModelTrainingService

service = ModelTrainingService()

# Train with generated data
result = service.train_pest_detection_model(
    data_dir="training_data/pest_detection",
    epochs=50,
    batch_size=32
)

print(f"Model accuracy: {result['accuracy']}")
```

### Time Series Models

```python
# Example: Train climate prediction LSTM
import pandas as pd
from app.ml.train_climate_prediction_model import train_climate_model

# Load climate data
df = pd.read_csv('training_data/climate_prediction/climate_timeseries.csv')

# Train LSTM model
model = train_climate_model(
    data=df,
    sequence_length=30,
    prediction_horizon=7
)
```

### Regression Models

```python
# Example: Train yield prediction model
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Load yield data
df = pd.read_csv('training_data/yield_prediction/yield_prediction.csv')

# Prepare features
X = df.drop(['total_yield_tons', 'quality_grade'], axis=1)
y = df['yield_per_hectare_tons']

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)
```

## 📁 Metadata Structure

Each dataset includes a `metadata.json` file with:

```json
{
  "description": "Dataset description",
  "features": ["list", "of", "features"],
  "records": 1000,
  "use_case": "Model use case",
  "model_type": "Recommended model architecture",
  "timestamp": "2025-10-28T..."
}
```

For image datasets, each image has:

```json
{
  "image_path": "relative/path/to/image.jpg",
  "label": "class_name",
  "severity": "low|medium|high",
  "confidence": 0.95,
  "timestamp": "2025-10-28T..."
}
```

## 🔧 Customization

### Modify Dataset Size

Edit `generate_training_datasets.py`:

```python
pests = {
    'aphids': {'count': 500},  # Change from 150 to 500
    # ...
}
```

### Add New Classes

```python
pests = {
    # Existing classes...
    'new_pest': {'count': 150, 'color': (R, G, B), 'size': 25}
}
```

### Change Image Resolution

```python
img = Image.new('RGB', (384, 384), ...)  # Change from 224x224
```

## 🎨 Dataset Quality

All synthetic datasets are designed to:
- ✅ Mimic real-world variations
- ✅ Include class imbalance (healthy vs diseased)
- ✅ Have realistic feature distributions
- ✅ Support data augmentation
- ✅ Enable transfer learning

## 🧪 Validation Split

Recommended splits for training:
- **Training**: 70% (use for model fitting)
- **Validation**: 15% (use for hyperparameter tuning)
- **Testing**: 15% (use for final evaluation)

```python
from sklearn.model_selection import train_test_split

# Split data
train_data, test_data = train_test_split(data, test_size=0.15, random_state=42)
train_data, val_data = train_test_split(train_data, test_size=0.176, random_state=42)  # 0.176 * 0.85 ≈ 0.15
```

## 📈 Performance Baselines

Expected accuracy on synthetic data:

| Model | Expected Accuracy | Notes |
|-------|------------------|-------|
| Pest Detection | 85-95% | Higher for healthy vs pests |
| Disease Detection | 80-92% | Some diseases look similar |
| Storage Assessment | 88-95% | Clear visual differences |
| Soil Diagnostics | 82-90% | Texture analysis challenging |
| Plant Health | 85-93% | Stage transitions gradual |
| Climate Prediction | RMSE < 2°C | Temperature forecasting |
| Yield Prediction | R² > 0.75 | Multi-factor regression |

## 🔄 Data Augmentation

Enhance training with augmentation:

```python
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2,
    brightness_range=[0.8, 1.2]
)
```

## 📚 Real-World Data Integration

To replace synthetic data with real images:

1. **Organize real images** in same folder structure
2. **Update metadata.json** with real labels
3. **Keep same class names** for compatibility
4. **Mix synthetic + real** for better generalization

```python
# Mixing synthetic and real data
synthetic_dir = "training_data/pest_detection"
real_dir = "real_data/pest_detection"

# Combine both in training pipeline
train_generator = flow_from_directory([synthetic_dir, real_dir])
```

## 🌐 Pre-trained Model Integration

Use transfer learning with:

- **MobileNet V3** (pest, disease, plant health)
- **EfficientNet B0** (soil, storage)
- **LSTM** (climate prediction)
- **Random Forest/XGBoost** (yield prediction)

## 🐛 Troubleshooting

### Memory Issues
```python
# Reduce batch size
batch_size = 16  # Instead of 32
```

### Image Quality
```python
# Increase image quality
img.save(img_path, quality=95)  # Instead of 85
```

### Class Imbalance
```python
# Use class weights
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight('balanced', 
                                     classes=np.unique(labels), 
                                     y=labels)
```

## 📞 Support

For issues or improvements:
1. Check `dataset_summary.json` for generation statistics
2. Review `metadata.json` in each dataset folder
3. Validate image counts match expected values

## 📄 License

This dataset generator is part of the AgroShield project. Generated datasets are for training purposes only.

---

**Generated with ❤️ for AgroShield AI Models**
