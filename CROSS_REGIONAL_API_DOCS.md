# Cross-Regional Marketplace API Documentation

## Base URL
```
http://localhost:8000/api/marketplace
```

---

## 🌾 Farmer Endpoints

### 1. Get Farmer Location & Region
Retrieve farmer's GPS coordinates and administrative region.

**Endpoint**: `GET /farmer/farmer-location/{farmer_id}`

**Path Parameters:**
- `farmer_id` (string, required): Farmer's unique identifier

**Response Example:**
```json
{
  "farmer_id": "F12345",
  "location": {
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  "region": "Central Kenya",
  "county": "Kiambu",
  "sub_county": "Limuru"
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/marketplace/farmer/farmer-location/F12345"
```

**JavaScript Example:**
```javascript
const response = await axios.get(`${API_BASE_URL}/farmer-location/${farmerId}`);
const { location, region } = response.data;
```

---

### 2. Analyze Cross-Regional Opportunities
AI-powered analysis of regional competition and target market recommendations.

**Endpoint**: `POST /farmer/analyze-cross-regional`

**Form Data Parameters:**
- `farmer_id` (string, required): Farmer's ID
- `farmer_region` (string, required): Farmer's current region
- `crops` (string, required): Comma-separated list of crops (e.g., "maize,beans")
- `radius_km` (float, optional): Radius for local competition analysis (default: 50)

**Response Example:**
```json
{
  "status": "success",
  "farmer_id": "F12345",
  "farmer_region": "Central Kenya",
  "crops": ["maize"],
  "local_competition": {
    "local_farmers_count": 89,
    "same_crop_farmers": 67,
    "competition_score": 0.85,
    "status": "HIGH",
    "message": "High competition: 67 farmers in your region grow maize"
  },
  "recommended_regions": [
    {
      "region": "Nairobi Region",
      "buyer_density": 3.2,
      "local_supply": "LOW",
      "demand_score": 0.92,
      "avg_price_kes": 65,
      "reason": "High demand (many buyers), Low local production, Above-average prices"
    },
    {
      "region": "Coast Region",
      "buyer_density": 2.8,
      "local_supply": "VERY_LOW",
      "demand_score": 0.88,
      "avg_price_kes": 62,
      "reason": "High demand (many buyers), Low local production"
    }
  ],
  "avoid_regions": [
    {
      "region": "Rift Valley",
      "reason": "Oversupplied - 250 farmers, low prices"
    }
  ],
  "matched_buyers": [
    {
      "buyer_id": "B5678",
      "business_name": "Nairobi Fresh Foods Ltd",
      "region": "Nairobi Region",
      "distance_km": 45.2,
      "requirements": {
        "crop": "maize",
        "quantity_needed_kg": 5000,
        "frequency": "weekly",
        "max_price_kes": 70
      }
    }
  ],
  "summary": {
    "competition_status": "HIGH",
    "top_target_region": "Nairobi Region",
    "potential_matches": 12,
    "recommendation": "High local competition detected (67 farmers). We recommend targeting Nairobi Region where demand is 3.2x higher."
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/marketplace/farmer/analyze-cross-regional" \
  -F "farmer_id=F12345" \
  -F "farmer_region=Central Kenya" \
  -F "crops=maize" \
  -F "radius_km=50"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('farmer_id', farmerId);
formData.append('farmer_region', farmerRegion);
formData.append('crops', 'maize,beans');
formData.append('radius_km', 50);

const response = await axios.post(`${API_BASE_URL}/analyze-cross-regional`, formData);
const { recommended_regions, local_competition } = response.data;
```

---

### 3. Create Listing with Cross-Regional Options
Create a marketplace listing with cross-regional targeting.

**Endpoint**: `POST /farmer/create-listing`

**Form Data Parameters (Standard):**
- `farmer_id` (string, required)
- `field_id` (string, required)
- `crop` (string, required)
- `quantity_kg` (float, required)
- `quality_grade` (string, optional): "A", "B", "C", "Premium" (default: "B")
- `ready_date` (string, required): ISO format date
- `minimum_order_kg` (float, optional): default 50
- `target_price_kes_per_kg` (float, optional)
- `storage_location` (string, required)
- `delivery_available` (boolean, optional): default false
- `organic_certified` (boolean, optional): default false
- `images` (file[], optional): Max 5 images

**Form Data Parameters (Cross-Regional):**
- `farmer_region` (string, optional): Farmer's region
- `prefer_cross_regional` (boolean, optional): Prioritize cross-regional buyers (default: false)
- `avoid_local_competition` (boolean, optional): Exclude buyers from own region (default: false)
- `target_regions` (string, optional): JSON array of target regions (e.g., '["Nairobi Region","Coast Region"]')

**Response Example:**
```json
{
  "status": "success",
  "listing_id": "LOT_F12345_1709140800",
  "listing": {
    "listing_id": "LOT_F12345_1709140800",
    "farmer_id": "F12345",
    "crop": "maize",
    "quantity_kg": 5000,
    "farmer_region": "Central Kenya",
    "prefer_cross_regional": true,
    "avoid_local_competition": true,
    "target_regions": ["Nairobi Region", "Coast Region"],
    "excluded_regions": ["Central Kenya"],
    "status": "active"
  },
  "ai_recommendations": {
    "optimal_sale_window": {
      "start_date": "2025-11-01",
      "end_date": "2025-11-15"
    },
    "market_recommendations": [
      "Price expected to rise 12% in 2 weeks",
      "High demand from Nairobi buyers",
      "Transport costs manageable for 300km distance"
    ]
  },
  "cross_regional_insights": {
    "message": "High local competition detected (67 farmers). We recommend targeting Nairobi Region where demand is 3.2x higher.",
    "recommended_regions": ["Nairobi Region", "Coast Region", "Western Kenya"],
    "avoid_regions": [
      {
        "region": "Rift Valley",
        "reason": "High competition - 250 maize farmers"
      }
    ],
    "visibility": {
      "visible_to_regions": ["Nairobi Region", "Coast Region"],
      "excluded_regions": ["Central Kenya"]
    },
    "local_competition": {
      "local_farmers_count": 89,
      "same_crop_farmers": 67,
      "competition_score": 0.85,
      "status": "HIGH"
    }
  }
}
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('farmer_id', farmerId);
formData.append('field_id', fieldId);
formData.append('crop', 'maize');
formData.append('quantity_kg', 5000);
formData.append('ready_date', '2025-11-15');
formData.append('storage_location', 'Farm Storage');

// Cross-regional parameters
formData.append('farmer_region', farmerRegion);
formData.append('prefer_cross_regional', true);
formData.append('avoid_local_competition', true);
formData.append('target_regions', JSON.stringify(['Nairobi Region', 'Coast Region']));

const response = await axios.post(`${API_BASE_URL}/create-listing`, formData);
```

---

## 🛒 Buyer Endpoints

### 4. Get Buyer Location & Region
Retrieve buyer's business location and administrative region.

**Endpoint**: `GET /buyer/buyer-location/{buyer_id}`

**Path Parameters:**
- `buyer_id` (string, required): Buyer's unique identifier

**Response Example:**
```json
{
  "buyer_id": "B5678",
  "business_name": "Nairobi Fresh Foods Ltd",
  "business_type": "Wholesaler",
  "location": {
    "latitude": -1.2864,
    "longitude": 36.8172
  },
  "region": "Nairobi Region",
  "county": "Nairobi",
  "verified": true
}
```

**JavaScript Example:**
```javascript
const response = await axios.get(`${API_BASE_URL}/buyer-location/${buyerId}`);
const { region, business_name } = response.data;
```

---

### 5. Search Listings with Cross-Regional Filters
Search marketplace listings with regional diversity options.

**Endpoint**: `GET /buyer/search-listings`

**Query Parameters (Standard):**
- `buyer_id` (string, required)
- `crop` (string, optional): Filter by crop type
- `min_quantity_kg` (float, optional): Minimum quantity
- `max_price_kes` (float, optional): Maximum price per kg
- `quality_grade` (string, optional): "A", "B", "C", "Premium"
- `radius_km` (int, optional): Search radius (default: 100)
- `organic_only` (boolean, optional): Only organic certified (default: false)
- `ready_within_days` (int, optional): Ready within X days

**Query Parameters (Cross-Regional):**
- `buyer_region` (string, optional): Buyer's region (auto-detected if not provided)
- `exclude_my_region` (boolean, optional): Exclude listings from buyer's own region (default: false)
- `prefer_different_regions` (boolean, optional): Prioritize regional diversity (default: false)
- `cross_regional_only` (boolean, optional): Only show cross-regional listings (default: false)

**Response Example:**
```json
{
  "buyer_id": "B5678",
  "search_filters": {
    "crop": "maize",
    "max_price_kes": 70,
    "radius_km": 100
  },
  "total_results": 23,
  "listings": [
    {
      "listing_id": "LOT_F12345_1709140800",
      "crop": "maize",
      "farmer_id": "F12345",
      "farmer_region": "Western Kenya",
      "quantity_available_kg": 5000,
      "target_price_kes_per_kg": 45,
      "distance_km": 320,
      "estimated_transport_cost_kes": 12000,
      "is_cross_regional": true,
      "regional_benefits": "Diversifies supply, farmer avoids competition"
    }
  ],
  "regional_insights": {
    "total_listings": 23,
    "regions_covered": 5,
    "local_count": 0,
    "cross_regional_count": 23,
    "excluded_local_listings": 17,
    "avg_distance_km": 285,
    "diversity_score": 0.87,
    "top_regions": ["Western Kenya", "Coast Region", "Eastern Kenya"],
    "message": "Excellent regional diversity! Listings from 5 different regions. Excluded 17 local listings to avoid supporting your competition."
  },
  "summary": {
    "total_available_kg": 115000,
    "price_range": {
      "min": 42,
      "max": 58,
      "average": 47.5
    }
  }
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/marketplace/buyer/search-listings?buyer_id=B5678&crop=maize&exclude_my_region=true&prefer_different_regions=true"
```

**JavaScript Example:**
```javascript
const params = {
  buyer_id: buyerId,
  buyer_region: buyerRegion,
  crop: 'maize',
  max_price_kes: 70,
  exclude_my_region: true,
  prefer_different_regions: true,
  cross_regional_only: true
};

const response = await axios.get(`${API_BASE_URL}/search-listings`, { params });
const { listings, regional_insights } = response.data;
```

---

## 📊 Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid parameters or data |
| 403 | Forbidden | Unauthorized access |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error occurred |

---

## 🔑 Key Concepts

### Regional Competition Score
A value from 0-1 indicating local competition level:
- **0.0 - 0.4**: LOW competition (good local opportunity)
- **0.4 - 0.7**: MEDIUM competition (consider cross-regional)
- **0.7 - 1.0**: HIGH competition (highly recommend cross-regional)

### Buyer Density
Ratio of buyers to suppliers in a region:
- **< 0.5**: Oversupplied (too many farmers, not enough buyers)
- **0.5 - 2.0**: Balanced market
- **> 2.0**: High demand (more buyers than suppliers)

### Demand Score
AI-calculated score (0-1) based on:
- Buyer density (40%)
- Historical prices (30%)
- Local supply level (30%)

Higher scores indicate better selling opportunities.

### Regional Diversity Score
Measures how well distributed search results are across regions:
- **0.0 - 0.4**: Low diversity (concentrated in few regions)
- **0.4 - 0.7**: Moderate diversity
- **0.7 - 1.0**: High diversity (excellent regional spread)

---

## 🚀 Integration Examples

### React Native - Farmer Flow
```javascript
// 1. Load farmer region on mount
useEffect(() => {
  loadFarmerRegion();
}, []);

const loadFarmerRegion = async () => {
  const response = await axios.get(`${API_BASE_URL}/farmer-location/${farmerId}`);
  setFarmerRegion(response.data.region);
};

// 2. Analyze opportunities when creating listing
const analyzeCrossRegional = async () => {
  const formData = new FormData();
  formData.append('farmer_id', farmerId);
  formData.append('farmer_region', farmerRegion);
  formData.append('crops', 'maize');
  
  const response = await axios.post(`${API_BASE_URL}/analyze-cross-regional`, formData);
  setTargetRegions(response.data.recommended_regions);
  setLocalCompetition(response.data.local_competition);
};

// 3. Create listing with cross-regional options
const createListing = async () => {
  const formData = new FormData();
  // ... standard fields
  formData.append('farmer_region', farmerRegion);
  formData.append('prefer_cross_regional', true);
  formData.append('avoid_local_competition', true);
  formData.append('target_regions', JSON.stringify(['Nairobi Region', 'Coast Region']));
  
  const response = await axios.post(`${API_BASE_URL}/create-listing`, formData);
  
  if (response.data.cross_regional_insights) {
    Alert.alert('Success', response.data.cross_regional_insights.message);
  }
};
```

### React Native - Buyer Flow
```javascript
// 1. Load buyer region
useEffect(() => {
  if (buyerId) {
    loadBuyerRegion();
  }
}, [buyerId]);

const loadBuyerRegion = async () => {
  const response = await axios.get(`${API_BASE_URL}/buyer-location/${buyerId}`);
  setBuyerRegion(response.data.region);
};

// 2. Search with cross-regional filters
const searchListings = async () => {
  const params = {
    buyer_id: buyerId,
    buyer_region: buyerRegion,
    crop: 'maize',
    exclude_my_region: true,
    prefer_different_regions: true
  };
  
  const response = await axios.get(`${API_BASE_URL}/search-listings`, { params });
  setSearchResults(response.data.listings);
  setRegionalInsights(response.data.regional_insights);
  
  // Show insights
  const insights = response.data.regional_insights;
  Alert.alert(
    '🌍 Cross-Regional Insights',
    `Found ${response.data.listings.length} listings from ${insights.regions_covered} regions\n\n` +
    `Excluded: ${insights.excluded_local_listings} local listings`
  );
};
```

---

## 🛠️ Testing

### Test Scenario 1: High Competition Farmer
```bash
# Get location
curl -X GET "http://localhost:8000/api/marketplace/farmer/farmer-location/F12345"

# Analyze opportunities
curl -X POST "http://localhost:8000/api/marketplace/farmer/analyze-cross-regional" \
  -F "farmer_id=F12345" \
  -F "farmer_region=Central Kenya" \
  -F "crops=maize"

# Expected: High competition score, recommendations for Nairobi/Coast
```

### Test Scenario 2: Cross-Regional Buyer Search
```bash
# Search with exclusions
curl -X GET "http://localhost:8000/api/marketplace/buyer/search-listings?buyer_id=B5678&crop=maize&exclude_my_region=true&prefer_different_regions=true"

# Expected: No Central Kenya listings, high diversity score
```

---

## 📝 Notes

- All endpoints support JSON responses
- Distances calculated using Haversine formula (accurate to ~1km)
- Transport costs estimated at 10 KES/km/ton + 15% surcharge >200km
- Regional boundaries use simplified polygons (production should use proper GIS data)
- Prices in Kenyan Shillings (KES)
- Dates in ISO 8601 format

---

**Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Base URL**: `http://localhost:8000/api/marketplace`
