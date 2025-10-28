# 🔐 Free Public API Keys Setup Guide

This guide shows you how to get **FREE** API keys from public agricultural and environmental data sources.

## 📋 Quick Summary

| Service | Cost | Signup Time | Data Available | Required? |
|---------|------|-------------|----------------|-----------|
| **FAO SoilGrids** | FREE | No signup | Soil properties globally | ❌ No key needed! |
| **iNaturalist** | FREE | No signup | 100M+ species observations | ❌ No key needed! |
| **GBIF** | FREE | No signup | 2B+ biodiversity records | ❌ No key needed! |
| **OpenWeatherMap** | FREE tier | 2 minutes | Weather/climate data | ✅ Recommended |
| **Kaggle** | FREE | 2 minutes | PlantVillage dataset | ✅ For disease images |

---

## 1️⃣ OpenWeatherMap API (Weather & Climate Data)

### **Free Tier**: 1,000 calls/day, current weather, 5-day forecast

### Steps:
1. Go to: https://openweathermap.org/api
2. Click **"Get API Key"** or **"Sign Up"**
3. Create free account (email + password)
4. Go to **API Keys** tab
5. Copy your API key

### Add to `.env`:
```env
OPENWEATHER_API_KEY=your_key_here
```

**Example**: `OPENWEATHER_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

---

## 2️⃣ Kaggle API (PlantVillage Dataset - 54,000 plant disease images)

### **Free Tier**: Unlimited downloads of public datasets

### Steps:
1. Go to: https://www.kaggle.com/
2. Click **"Register"** (free account)
3. Go to **Account Settings**: https://www.kaggle.com/settings
4. Scroll to **API** section
5. Click **"Create New API Token"**
6. Download `kaggle.json` file

### Setup:
**Windows:**
```cmd
mkdir %USERPROFILE%\.kaggle
move kaggle.json %USERPROFILE%\.kaggle\
```

**Linux/Mac:**
```bash
mkdir ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Install Kaggle CLI:
```bash
pip install kaggle
```

### Test:
```bash
kaggle datasets list
```

---

## 3️⃣ FAO SoilGrids (NO API KEY REQUIRED!)

### **Free Tier**: Unlimited public access to global soil data

### Direct Use:
No signup or API key needed! The script uses it directly:

```python
https://rest.isric.org/soilgrids/v2.0/properties/query
```

**Data includes**: pH, nitrogen, organic carbon, clay, sand, silt, bulk density

**Coverage**: Entire world at 250m resolution

---

## 4️⃣ iNaturalist (NO API KEY REQUIRED!)

### **Free Tier**: Unlimited access to 100M+ observations

### Direct Use:
No API key needed! Public API:

```python
https://api.inaturalist.org/v1/observations
```

**Data includes**: 
- Insect/pest observations with photos
- Geographic coordinates
- Quality-graded identifications
- Expert community validation

**Perfect for**: Pest detection training data

---

## 5️⃣ GBIF - Global Biodiversity Information Facility (NO API KEY REQUIRED!)

### **Free Tier**: Unlimited access to 2 billion records

### Direct Use:
No signup needed! Public API:

```python
https://api.gbif.org/v1/occurrence/search
```

**Data includes**:
- Species occurrences worldwide
- Geographic distribution
- Temporal data
- Scientific classifications

**Perfect for**: Pest species distribution mapping

---

## 🚀 Quick Start (No API Keys)

You can start collecting data **immediately** without any API keys:

```bash
cd backend
python collect_public_api_data.py --soil --pests
```

This will collect:
- ✅ Soil data from FAO SoilGrids
- ✅ Pest observations from iNaturalist  
- ✅ Species data from GBIF

**All without API keys!**

---

## 🔧 Optional APIs (Enhance Your Dataset)

### OpenWeatherMap (Recommended)
- Adds historical climate data
- Improves climate prediction model
- **Free tier**: 1,000 calls/day

### Kaggle (Recommended for Disease Detection)
- 54,000 labeled plant disease images
- 38 disease classes
- Industry-standard dataset

---

## 📊 Complete Data Collection Command

```bash
# Install dependencies
pip install aiohttp kaggle pandas numpy pillow requests

# With API keys (recommended)
export OPENWEATHER_API_KEY=your_key_here  # Linux/Mac
set OPENWEATHER_API_KEY=your_key_here     # Windows

# Run collection
python collect_public_api_data.py --all
```

---

## 🎯 What Data You'll Get

### Without Any API Keys:
- **Soil data**: 8+ locations in Kenya (pH, NPK, organic matter)
- **Pest observations**: 500+ images from iNaturalist
- **Species data**: 200+ pest occurrences from GBIF

### With OpenWeatherMap Key:
- **Current weather**: Temperature, humidity, wind, clouds
- **8+ locations** across Kenya

### With Kaggle Setup:
- **PlantVillage**: 54,000 disease images
- **38 disease classes**
- **14 crop types**

---

## 🔍 Verify Your Setup

```bash
# Test Python
python --version

# Test API collection (no keys needed)
python collect_public_api_data.py --soil

# Check output
dir training_data_public
```

---

## ⚠️ Troubleshooting

### "Kaggle API not found"
```bash
pip install kaggle
```

### "Permission denied on kaggle.json"
```bash
chmod 600 ~/.kaggle/kaggle.json  # Linux/Mac
```

### "Module not found: aiohttp"
```bash
pip install aiohttp pandas numpy pillow requests
```

---

## 📚 API Documentation Links

- **OpenWeatherMap**: https://openweathermap.org/api/one-call-api
- **FAO SoilGrids**: https://www.isric.org/explore/soilgrids/faq-soilgrids
- **iNaturalist**: https://api.inaturalist.org/v1/docs/
- **GBIF**: https://www.gbif.org/developer/summary
- **Kaggle**: https://github.com/Kaggle/kaggle-api

---

## 🎓 Next Steps

1. **Get API keys** (optional but recommended):
   - OpenWeatherMap (2 min signup)
   - Kaggle (2 min signup)

2. **Run data collection**:
   ```bash
   python collect_public_api_data.py --all
   ```

3. **Train models**:
   ```bash
   python train_models_example.py
   ```

4. **Check results**:
   - Training data in `training_data_public/`
   - Models in `trained_models/`
   - Logs in `training_logs/`

---

✅ **All APIs listed here are FREE for educational/research use!**
