# Unified Plot Creation System

## Overview

The unified plot creation system integrates demo plots and real plots into a single, flexible API that allows farmers to:

- **Create demo plots** - Editable templates to learn the system
- **Create real plots** - Actual farm plots with full calendar integration
- **Manage multiple crops** - No limit on number of plots or crop types
- **Upload multiple photos** - Initial image, soil photo, and additional progress photos
- **Edit any plot** - Convert demo→real, change crops, update photos
- **Filter plots** - Query by demo/real, crop type, status

---

## Database Schema Changes

### New Column: `is_demo`

Added to `digital_plots` table:

```sql
is_demo BOOLEAN DEFAULT FALSE
```

- `true` = Demo plot (editable template, no auto-calendar)
- `false` = Real plot (actual farm, generates calendar events)

### New Indexes

```sql
CREATE INDEX idx_digital_plots_is_demo ON digital_plots(is_demo);
CREATE INDEX idx_digital_plots_user_crop ON digital_plots(user_id, crop_name);
```

---

## API Endpoints

### 1. Create Plot (Unified)

**`POST /api/advanced-growth/plots`**

Creates a demo or real plot with support for multiple photos.

**Form Data Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User's unique ID |
| `crop_name` | string | Yes | Crop name (e.g., "Maize", "Tomatoes") |
| `plot_name` | string | Yes | Custom plot name |
| `planting_date` | string | Yes | ISO format date |
| `latitude` | float | Yes | Plot latitude |
| `longitude` | float | Yes | Plot longitude |
| `is_demo` | boolean | No | `true` for demo, `false` for real (default: false) |
| `area_size` | float | No | Plot size in square meters |
| `notes` | string | No | Additional notes |
| `soil_type` | string | No | Manual soil type entry |
| `initial_image` | file | No | Main plot photo |
| `soil_image` | file | No | Soil sample photo |
| `additional_images` | file[] | No | Array of extra photos |

**Example Request:**

```python
import requests

data = {
    "user_id": "123-456-789",
    "crop_name": "Maize",
    "plot_name": "North Field",
    "planting_date": "2025-02-01T08:00:00",
    "latitude": -1.2921,
    "longitude": 36.8219,
    "is_demo": "false",
    "area_size": "10.0",
    "soil_type": "Clay Loam"
}

files = {
    "initial_image": open("plot_photo.jpg", "rb"),
    "soil_image": open("soil_sample.jpg", "rb")
}

response = requests.post(
    "https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth/plots",
    data=data,
    files=files
)
```

**Response:**

```json
{
  "success": true,
  "message": "Real plot created successfully!",
  "plot_id": "abc-123-def",
  "is_demo": false,
  "plot": {
    "id": "abc-123-def",
    "user_id": "123-456-789",
    "crop_name": "Maize",
    "plot_name": "North Field",
    "is_demo": false,
    "planting_date": "2025-02-01T08:00:00",
    "location": {"latitude": -1.2921, "longitude": 36.8219}
  },
  "calendar_events": [...],  // Only for real plots
  "images": {
    "initial": "https://.../plot_photo.jpg",
    "soil": "https://.../soil_sample.jpg",
    "additional": []
  },
  "total_images": 2
}
```

---

### 2. Edit Plot

**`PATCH /api/advanced-growth/plots/{plot_id}`**

Update any plot details, including converting demo↔real.

**Form Data Parameters:**

All parameters are optional - only provide what you want to update.

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | User ID (required for verification) |
| `crop_name` | string | Change crop type |
| `plot_name` | string | Change plot name |
| `planting_date` | string | Update planting date |
| `latitude` | float | Update location |
| `longitude` | float | Update location |
| `is_demo` | boolean | Convert demo→real or real→demo |
| `area_size` | float | Update plot size |
| `notes` | string | Update notes |
| `soil_type` | string | Update soil type |
| `status` | string | active, harvested, abandoned |
| `initial_image` | file | Replace initial image |
| `soil_image` | file | Replace soil image |
| `additional_images` | file[] | Add more photos |

**Example: Convert Demo to Real**

```python
data = {
    "user_id": "123-456-789",
    "is_demo": "false",  # Convert to real
    "plot_name": "Real Tomato Garden"
}

response = requests.patch(
    f"https://urchin-app-86rjy.ondigitalocean.app/api/advanced-growth/plots/{plot_id}",
    data=data
)
```

When converting demo→real, calendar events are automatically generated.

**Response:**

```json
{
  "success": true,
  "message": "Plot updated successfully!",
  "plot": {...},
  "updates_applied": ["is_demo", "plot_name"],
  "new_images_count": 0
}
```

---

### 3. Get All Plots

**`GET /api/advanced-growth/plots`**

Retrieve all plots for a user with optional filters.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | Required - User's ID |
| `is_demo` | boolean | Filter by demo/real plots |
| `crop_name` | string | Filter by crop |
| `status` | string | Filter by status |

**Examples:**

```bash
# Get all plots
GET /api/advanced-growth/plots?user_id=123-456-789

# Get only demo plots
GET /api/advanced-growth/plots?user_id=123-456-789&is_demo=true

# Get only real plots
GET /api/advanced-growth/plots?user_id=123-456-789&is_demo=false

# Get all maize plots
GET /api/advanced-growth/plots?user_id=123-456-789&crop_name=Maize

# Get active real plots
GET /api/advanced-growth/plots?user_id=123-456-789&is_demo=false&status=active
```

**Response:**

```json
{
  "success": true,
  "plots": [
    {
      "id": "plot-1",
      "plot_name": "North Field - Maize",
      "crop_name": "Maize",
      "is_demo": false,
      "status": "active"
    },
    {
      "id": "plot-2",
      "plot_name": "Demo Tomato Garden",
      "crop_name": "Tomatoes",
      "is_demo": true,
      "status": "active"
    }
  ],
  "total_plots": 2,
  "demo_plots": 1,
  "real_plots": 1,
  "unique_crops": ["Maize", "Tomatoes"],
  "filters_applied": {
    "is_demo": null,
    "crop_name": null,
    "status": null
  }
}
```

---

### 4. Get Plot Details

**`GET /api/advanced-growth/plots/{plot_id}`**

Get comprehensive information about a specific plot.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | Required - User's ID |

**Response:**

```json
{
  "success": true,
  "plot": {...},
  "is_demo": false,
  "images": [
    {
      "image_url": "https://.../initial.jpg",
      "image_type": "initial",
      "captured_at": "2025-02-01"
    }
  ],
  "recent_logs": [...],
  "upcoming_events": [...],
  "total_images": 5,
  "total_logs": 3
}
```

---

## Legacy Endpoints (Deprecated)

### POST /plots/create-manual

Still functional but redirects to the new unified endpoint. Use `POST /plots` instead.

### POST /seed-demo-data/{user_id}

Still creates demo plots but use `POST /plots` with `is_demo=true` instead.

---

## Use Cases

### 1. New User Onboarding

Create a demo plot to show the farmer how the system works:

```python
data = {
    "user_id": user_id,
    "crop_name": "Maize",
    "plot_name": "Demo Maize Plot",
    "planting_date": "2025-01-15T10:00:00",
    "latitude": -1.2921,
    "longitude": 36.8219,
    "is_demo": "true",  # Demo plot
    "notes": "Try editing this plot or create your own!"
}
```

Farmer can experiment with this plot, then convert it to real when ready.

### 2. Convert Demo to Real

When farmer is ready to use the demo plot:

```python
PATCH /plots/{demo_plot_id}
{
    "user_id": user_id,
    "is_demo": "false",
    "plot_name": "My First Real Maize Plot",
    "planting_date": "2025-02-01T08:00:00"  # Actual planting date
}
```

System automatically generates calendar events.

### 3. Multiple Crops

Farmer can create unlimited plots for different crops:

```python
# Maize plot
POST /plots {"crop_name": "Maize", "is_demo": "false", ...}

# Tomato plot
POST /plots {"crop_name": "Tomatoes", "is_demo": "false", ...}

# Bean plot
POST /plots {"crop_name": "Beans", "is_demo": "false", ...}
```

Query specific crops: `GET /plots?user_id=123&crop_name=Maize`

### 4. Upload Multiple Photos

Document plot progress with multiple photos:

```python
files = {
    "initial_image": open("wide_shot.jpg", "rb"),
    "soil_image": open("soil_sample.jpg", "rb"),
    "additional_images": [
        open("closeup_1.jpg", "rb"),
        open("closeup_2.jpg", "rb"),
        open("pest_damage.jpg", "rb")
    ]
}

POST /plots with files=files
```

### 5. Mark Plot as Harvested

After harvest, update status:

```python
PATCH /plots/{plot_id}
{
    "user_id": user_id,
    "status": "harvested",
    "notes": "Harvested on Feb 15, 2025. Good yield!"
}
```

---

## Key Differences: Demo vs Real

| Feature | Demo Plot | Real Plot |
|---------|-----------|-----------|
| **is_demo** | `true` | `false` |
| **Purpose** | Learning/Templates | Actual farming |
| **Editable** | ✅ Fully editable | ✅ Fully editable |
| **Calendar Events** | ❌ Not auto-generated | ✅ Auto-generated |
| **Can Convert** | ✅ Demo → Real | ✅ Real → Demo |
| **Multiple Allowed** | ✅ Yes | ✅ Yes |
| **Photo Upload** | ✅ Yes | ✅ Yes |

---

## Testing

Run the comprehensive test suite:

```bash
python test_unified_plots.py
```

This tests:
- ✅ Demo plot creation
- ✅ Real plot creation  
- ✅ Multiple crops per farmer
- ✅ Demo → Real conversion
- ✅ Plot editing
- ✅ Photo uploads
- ✅ Filtered plot retrieval

---

## Migration Notes

### For Frontend Developers

1. **Replace old endpoint calls:**
   ```javascript
   // OLD
   POST /api/advanced-growth/plots/create-manual
   
   // NEW
   POST /api/advanced-growth/plots
   ```

2. **Add demo plot support:**
   ```javascript
   // Create demo plot
   const demoData = {..., is_demo: true};
   
   // Create real plot
   const realData = {..., is_demo: false};
   ```

3. **Show demo/real distinction in UI:**
   ```javascript
   {plot.is_demo && <Badge>Demo</Badge>}
   ```

4. **Allow demo → real conversion:**
   ```javascript
   // Convert button
   PATCH /plots/{id} with {is_demo: false}
   ```

### Database Migration

Run the updated schema:

```sql
-- Add is_demo column
ALTER TABLE digital_plots ADD COLUMN is_demo BOOLEAN DEFAULT FALSE;

-- Add indexes
CREATE INDEX idx_digital_plots_is_demo ON digital_plots(is_demo);
CREATE INDEX idx_digital_plots_user_crop ON digital_plots(user_id, crop_name);
```

Existing plots will default to `is_demo=false` (real plots).

---

## Summary

The unified plot system provides:

✅ **Single endpoint** for all plot creation  
✅ **Demo plots** for learning and templates  
✅ **Real plots** with full calendar integration  
✅ **Multiple crops** per farmer (unlimited)  
✅ **Multiple photos** per plot  
✅ **Full editability** including demo↔real conversion  
✅ **Flexible filtering** for plot queries  
✅ **Backward compatibility** with legacy endpoints  

Farmers can now:
- Start with demo plots to learn the system
- Convert demos to real plots when ready
- Manage multiple crops simultaneously
- Upload as many photos as needed
- Edit any plot at any time
