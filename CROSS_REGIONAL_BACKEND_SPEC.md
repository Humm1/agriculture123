# Cross-Regional Marketplace Backend Implementation Spec

## Overview
This document specifies the backend API endpoints and logic needed to support the cross-regional marketplace feature, where farmers sell to buyers in different regions to avoid local competition.

---

## 🎯 Business Logic

### Core Concept
- **Farmers** want to avoid selling in regions with high local competition (many farmers growing the same crop)
- **Buyers** want to diversify their supply sources by sourcing from multiple regions
- **System** analyzes regional competition and recommends optimal target markets
- **Matching** connects farmers in Region A with buyers in Region B (where Region B doesn't grow same crop heavily)

### Key Metrics
1. **Local Competition Score**: Ratio of local farmers growing same crop to average regional density
2. **Buyer Density Score**: Ratio of buyers to suppliers in a given region
3. **Regional Diversity Score**: Number of unique regions represented in search results / total listings
4. **Transport Cost Factor**: Distance-based cost calculation for cross-regional trade

---

## 🛠️ Required API Endpoints

### 1. Get Farmer Location & Region
**Endpoint**: `GET /api/marketplace/farmer/farmer-location/{farmer_id}`

**Purpose**: Retrieve farmer's geographic location and administrative region

**Response**:
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

**Implementation Notes**:
- Query `farmers` table for GPS coordinates
- Use reverse geocoding or admin boundaries database to determine region
- Cache region data to reduce API calls

---

### 2. Analyze Cross-Regional Opportunities
**Endpoint**: `POST /api/marketplace/farmer/analyze-cross-regional`

**Purpose**: AI-powered analysis of regional competition and target market recommendations

**Request Body**:
```json
{
  "farmer_id": "F12345",
  "farmer_region": "Central Kenya",
  "crops": ["maize", "beans"],
  "radius_km": 50
}
```

**Response**:
```json
{
  "local_competition": {
    "local_farmers_count": 127,
    "same_crop_farmers": 89,
    "competition_score": 0.85,
    "status": "HIGH",
    "message": "High competition: 89 farmers in your region grow maize"
  },
  "recommended_regions": [
    {
      "region": "Nairobi Region",
      "buyer_density": 3.2,
      "local_supply": "LOW",
      "demand_score": 0.92,
      "reason": "High demand, low local production"
    },
    {
      "region": "Coast Region (Mombasa)",
      "buyer_density": 2.8,
      "local_supply": "VERY_LOW",
      "demand_score": 0.88,
      "reason": "Tourist hotels need consistent supply, minimal local maize production"
    }
  ],
  "avoid_regions": [
    {
      "region": "Rift Valley",
      "reason": "Oversupplied - 250+ maize farmers, low prices"
    }
  ],
  "matched_buyers": [
    {
      "buyer_id": "B5678",
      "region": "Nairobi Region",
      "distance_km": 45,
      "requirements": {
        "crop": "maize",
        "quantity_needed_kg": 5000,
        "frequency": "weekly"
      }
    }
  ]
}
```

**Algorithm**:
```python
def analyze_cross_regional_opportunities(farmer_id, farmer_region, crops, radius_km):
    # Step 1: Calculate local competition
    local_farmers = query_farmers_within_radius(farmer_id, radius_km)
    same_crop_farmers = filter_by_crops(local_farmers, crops)
    competition_score = len(same_crop_farmers) / avg_farmers_per_region
    
    # Step 2: Analyze all regions
    all_regions = get_all_regions()
    region_scores = []
    
    for region in all_regions:
        if region == farmer_region:
            continue  # Skip farmer's own region
        
        # Count suppliers and buyers in this region
        suppliers = count_farmers_in_region(region, crops)
        buyers = count_buyers_in_region(region, crops)
        
        # Calculate buyer density (demand/supply ratio)
        buyer_density = buyers / max(suppliers, 1)
        
        # Calculate demand score based on:
        # - Buyer density
        # - Historical purchase volume
        # - Price trends (higher prices = higher demand)
        demand_score = calculate_demand_score(region, crops)
        
        # Determine local supply level
        local_supply = "HIGH" if suppliers > 50 else "MEDIUM" if suppliers > 20 else "LOW"
        
        region_scores.append({
            "region": region,
            "buyer_density": buyer_density,
            "local_supply": local_supply,
            "demand_score": demand_score,
            "suppliers": suppliers,
            "buyers": buyers
        })
    
    # Step 3: Sort by demand score and return top 5
    recommended_regions = sorted(region_scores, key=lambda x: x['demand_score'], reverse=True)[:5]
    
    # Step 4: Find regions to avoid (oversupplied)
    avoid_regions = [r for r in region_scores if r['local_supply'] == 'HIGH' and r['buyer_density'] < 0.5]
    
    # Step 5: Match with active buyers in recommended regions
    matched_buyers = []
    for rec_region in recommended_regions[:3]:
        buyers = get_active_buyers_in_region(rec_region['region'], crops)
        for buyer in buyers:
            distance = calculate_distance(farmer_location, buyer.location)
            matched_buyers.append({
                "buyer_id": buyer.id,
                "region": rec_region['region'],
                "distance_km": distance,
                "requirements": buyer.requirements
            })
    
    return {
        "local_competition": {
            "local_farmers_count": len(local_farmers),
            "same_crop_farmers": len(same_crop_farmers),
            "competition_score": competition_score,
            "status": "HIGH" if competition_score > 0.7 else "MEDIUM" if competition_score > 0.4 else "LOW"
        },
        "recommended_regions": recommended_regions,
        "avoid_regions": avoid_regions[:3],
        "matched_buyers": matched_buyers
    }
```

---

### 3. Create Listing with Cross-Regional Parameters (UPDATE EXISTING)
**Endpoint**: `POST /api/marketplace/farmer/create-listing`

**New Parameters to Add**:
```json
{
  // Existing parameters...
  "farmer_region": "Central Kenya",
  "prefer_cross_regional": true,
  "avoid_local_competition": true,
  "target_regions": ["Nairobi Region", "Coast Region (Mombasa)"]
}
```

**Enhanced Response**:
```json
{
  "listing_id": "L78910",
  "status": "active",
  "cross_regional_insights": {
    "message": "Your listing will be prioritized for buyers in Nairobi Region and Coast Region. Excluding Central Kenya buyers to avoid competition.",
    "recommended_regions": ["Nairobi Region", "Coast Region (Mombasa)"],
    "avoid_regions": [
      {
        "region": "Rift Valley",
        "reason": "High competition - 250 maize farmers"
      }
    ],
    "visibility": {
      "visible_to_regions": ["Nairobi Region", "Coast Region (Mombasa)", "Western Kenya"],
      "excluded_regions": ["Central Kenya", "Rift Valley"]
    }
  }
}
```

**Implementation**:
```python
def create_listing_with_cross_regional(data):
    # 1. Create listing as usual
    listing = create_listing(data)
    
    # 2. Apply cross-regional preferences
    if data.get('prefer_cross_regional'):
        # Set visibility rules
        if data.get('avoid_local_competition'):
            # Exclude farmer's own region from visibility
            listing.excluded_regions = [data['farmer_region']]
        
        if data.get('target_regions'):
            # Prioritize specific target regions
            listing.prioritized_regions = data['target_regions']
    
    # 3. Calculate regional insights
    insights = analyze_cross_regional_opportunities(
        farmer_id=data['farmer_id'],
        farmer_region=data['farmer_region'],
        crops=[data['crop']],
        radius_km=50
    )
    
    # 4. Return enhanced response
    return {
        "listing_id": listing.id,
        "status": listing.status,
        "cross_regional_insights": format_insights_for_farmer(insights)
    }
```

---

### 4. Get Buyer Location & Region
**Endpoint**: `GET /api/marketplace/buyer/buyer-location/{buyer_id}`

**Purpose**: Retrieve buyer's business location and region

**Response**:
```json
{
  "buyer_id": "B5678",
  "location": {
    "latitude": -1.2864,
    "longitude": 36.8172
  },
  "region": "Nairobi Region",
  "business_type": "Wholesaler",
  "verified": true
}
```

---

### 5. Search Listings with Cross-Regional Filters (UPDATE EXISTING)
**Endpoint**: `GET /api/marketplace/buyer/search-listings`

**New Query Parameters**:
```
buyer_id=B5678
buyer_region=Nairobi Region
exclude_my_region=true
prefer_different_regions=true
cross_regional_only=true
target_regions=[]
// Existing parameters...
```

**Enhanced Response**:
```json
{
  "listings": [
    {
      "listing_id": "L78910",
      "crop": "maize",
      "farmer_id": "F12345",
      "farmer_region": "Western Kenya",
      "quantity_available_kg": 5000,
      "target_price_kes_per_kg": 45,
      "distance_km": 320,
      "estimated_transport_cost_kes": 12000,
      "is_cross_regional": true,
      "regional_benefits": "Diversifies your supply, farmer avoids local competition"
    }
    // More listings...
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
    "message": "Excellent regional diversity! 87% of results are from different regions."
  }
}
```

**Algorithm**:
```python
def search_listings_with_cross_regional(buyer_id, buyer_region, filters):
    # 1. Base query
    query = Listing.query.filter(status='active')
    
    # 2. Apply standard filters (crop, price, etc.)
    query = apply_standard_filters(query, filters)
    
    # 3. Apply cross-regional logic
    if filters.get('exclude_my_region'):
        # Exclude listings from buyer's own region
        query = query.filter(Listing.farmer_region != buyer_region)
    
    if filters.get('cross_regional_only'):
        # Only show listings marked as cross-regional
        query = query.filter(Listing.prefer_cross_regional == True)
    
    if filters.get('target_regions'):
        # Filter to specific target regions
        query = query.filter(Listing.farmer_region.in_(filters['target_regions']))
    
    # 4. Sort by regional diversity
    if filters.get('prefer_different_regions'):
        # Prioritize listings from under-represented regions
        listings = query.all()
        listings = sort_by_regional_diversity(listings)
    else:
        listings = query.all()
    
    # 5. Calculate regional insights
    total_listings = len(listings)
    regions_covered = len(set([l.farmer_region for l in listings]))
    cross_regional_count = len([l for l in listings if l.farmer_region != buyer_region])
    
    # How many local listings were excluded?
    excluded_query = Listing.query.filter(
        status='active',
        farmer_region=buyer_region
    )
    excluded_query = apply_standard_filters(excluded_query, filters)
    excluded_local_listings = excluded_query.count()
    
    # Calculate average distance
    avg_distance = sum([l.distance_km for l in listings]) / max(total_listings, 1)
    
    # Diversity score (0-1)
    diversity_score = regions_covered / max(total_listings, 1)
    
    # Top regions by listing count
    region_counts = Counter([l.farmer_region for l in listings])
    top_regions = [r[0] for r in region_counts.most_common(3)]
    
    return {
        "listings": [format_listing_for_buyer(l) for l in listings],
        "regional_insights": {
            "total_listings": total_listings,
            "regions_covered": regions_covered,
            "local_count": 0 if filters.get('exclude_my_region') else local_count,
            "cross_regional_count": cross_regional_count,
            "excluded_local_listings": excluded_local_listings,
            "avg_distance_km": avg_distance,
            "diversity_score": diversity_score,
            "top_regions": top_regions
        }
    }

def sort_by_regional_diversity(listings):
    """
    Sort listings to maximize regional diversity.
    Uses a greedy algorithm to alternate between regions.
    """
    sorted_listings = []
    region_counts = Counter()
    
    remaining = listings.copy()
    
    while remaining:
        # Find listing from least-represented region
        best_listing = None
        min_count = float('inf')
        
        for listing in remaining:
            region = listing.farmer_region
            if region_counts[region] < min_count:
                min_count = region_counts[region]
                best_listing = listing
        
        # Add to sorted list
        sorted_listings.append(best_listing)
        region_counts[best_listing.farmer_region] += 1
        remaining.remove(best_listing)
    
    return sorted_listings
```

---

## 📊 Database Schema Updates

### farmers table
```sql
ALTER TABLE farmers ADD COLUMN region VARCHAR(100);
ALTER TABLE farmers ADD COLUMN county VARCHAR(100);
ALTER TABLE farmers ADD COLUMN sub_county VARCHAR(100);
ALTER TABLE farmers ADD COLUMN latitude DECIMAL(10, 8);
ALTER TABLE farmers ADD COLUMN longitude DECIMAL(11, 8);
```

### buyers table
```sql
ALTER TABLE buyers ADD COLUMN region VARCHAR(100);
ALTER TABLE buyers ADD COLUMN latitude DECIMAL(10, 8);
ALTER TABLE buyers ADD COLUMN longitude DECIMAL(11, 8);
```

### listings table
```sql
ALTER TABLE listings ADD COLUMN farmer_region VARCHAR(100);
ALTER TABLE listings ADD COLUMN prefer_cross_regional BOOLEAN DEFAULT FALSE;
ALTER TABLE listings ADD COLUMN avoid_local_competition BOOLEAN DEFAULT FALSE;
ALTER TABLE listings ADD COLUMN target_regions TEXT;  -- JSON array
ALTER TABLE listings ADD COLUMN excluded_regions TEXT;  -- JSON array
ALTER TABLE listings ADD COLUMN prioritized_regions TEXT;  -- JSON array
```

### New table: regional_analytics
```sql
CREATE TABLE regional_analytics (
    id SERIAL PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    crop VARCHAR(50) NOT NULL,
    farmer_count INT DEFAULT 0,
    buyer_count INT DEFAULT 0,
    avg_price_kes DECIMAL(10, 2),
    total_supply_kg BIGINT DEFAULT 0,
    total_demand_kg BIGINT DEFAULT 0,
    buyer_density DECIMAL(5, 2),  -- buyers/farmers ratio
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(region, crop)
);
```

---

## 🧮 Helper Functions

### Calculate Distance Between Coordinates
```python
from math import radians, sin, cos, sqrt, atan2

def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Haversine formula to calculate distance between two GPS coordinates
    """
    R = 6371  # Earth radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
```

### Estimate Transport Cost
```python
def estimate_transport_cost(distance_km, quantity_kg):
    """
    Estimate transport cost based on distance and quantity
    """
    # Base rate: 10 KES per km per ton
    base_rate_per_km_per_ton = 10
    
    # Convert kg to tons
    quantity_tons = quantity_kg / 1000
    
    # Calculate base cost
    base_cost = distance_km * quantity_tons * base_rate_per_km_per_ton
    
    # Add fuel surcharge for long distances (>200km)
    if distance_km > 200:
        fuel_surcharge = base_cost * 0.15
    else:
        fuel_surcharge = 0
    
    total_cost = base_cost + fuel_surcharge
    
    return round(total_cost, 2)
```

### Get Region from GPS Coordinates
```python
import requests

def get_region_from_coordinates(latitude, longitude):
    """
    Reverse geocode GPS coordinates to administrative region
    Option 1: Use Nominatim (free)
    Option 2: Use Kenya county boundaries database
    """
    # Option 1: Nominatim (OpenStreetMap)
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
    response = requests.get(url)
    data = response.json()
    
    # Extract region/county from address
    address = data.get('address', {})
    county = address.get('county', 'Unknown')
    
    # Map to standard region names
    region_mapping = {
        'Kiambu': 'Central Kenya',
        'Nairobi': 'Nairobi Region',
        'Mombasa': 'Coast Region (Mombasa)',
        'Nakuru': 'Rift Valley',
        'Kisumu': 'Western Kenya',
        # Add more mappings...
    }
    
    region = region_mapping.get(county, county)
    
    return {
        "region": region,
        "county": county,
        "raw_address": address
    }
```

---

## 🧪 Testing Scenarios

### Test Case 1: High Competition Farmer
**Setup**:
- Farmer in Central Kenya (Kiambu)
- Growing maize
- 89 local farmers growing maize within 50km

**Expected Behavior**:
1. `analyze-cross-regional` returns:
   - `competition_score`: 0.85 (HIGH)
   - `recommended_regions`: ["Nairobi Region", "Coast Region (Mombasa)"]
   - `message`: "High competition: 89 farmers in your region grow maize"
2. `create-listing` with `avoid_local_competition=true`:
   - Listing excluded from Central Kenya buyers
   - Visible to Nairobi and Coast buyers
3. Farmer sees alert: "⚠️ High competition: 89 farmers in your region grow maize. Targeting 2 cross-regional markets."

### Test Case 2: Cross-Regional Buyer Search
**Setup**:
- Buyer in Nairobi Region
- Looking for maize
- `exclude_my_region=true`

**Expected Behavior**:
1. Search returns 23 listings from 5 different regions
2. NO listings from Nairobi Region
3. `regional_insights` shows:
   - `excluded_local_listings`: 17
   - `diversity_score`: 0.87
   - `top_regions`: ["Western Kenya", "Coast Region", "Eastern Kenya"]
4. Buyer sees alert: "🌍 Found 23 listings from 5 different regions. Excluded 17 local listings to avoid supporting your competition."

### Test Case 3: Specialized Crop (Low Competition)
**Setup**:
- Farmer in Coast Region
- Growing coconuts (specialized crop)
- Only 5 local farmers growing coconuts

**Expected Behavior**:
1. `analyze-cross-regional` returns:
   - `competition_score`: 0.15 (LOW)
   - `message`: "Low competition: Only 5 farmers in your region grow coconuts"
2. Recommendations focus on high-demand areas (hotels in Nairobi, Mombasa)
3. No need to exclude local region (low competition)

---

## 📈 Analytics & Monitoring

### Metrics to Track
1. **Cross-Regional Adoption Rate**: % of listings with `prefer_cross_regional=true`
2. **Regional Diversity Score**: Average diversity score across all searches
3. **Competition Impact**: Price differences between high-competition and low-competition regions
4. **Distance vs. Volume**: Correlation between transport distance and order size
5. **Regional Trade Flow**: Matrix showing trade volume between regions

### Dashboard Queries
```sql
-- Cross-regional listing adoption
SELECT 
    COUNT(*) FILTER (WHERE prefer_cross_regional = true) AS cross_regional_listings,
    COUNT(*) AS total_listings,
    ROUND(COUNT(*) FILTER (WHERE prefer_cross_regional = true) * 100.0 / COUNT(*), 2) AS adoption_rate
FROM listings
WHERE status = 'active';

-- Regional trade flow matrix
SELECT 
    l.farmer_region,
    b.region AS buyer_region,
    COUNT(*) AS transactions,
    SUM(o.quantity_kg) AS total_volume_kg,
    AVG(o.final_price_kes_per_kg) AS avg_price
FROM orders o
JOIN listings l ON o.listing_id = l.listing_id
JOIN buyers b ON o.buyer_id = b.buyer_id
WHERE o.status = 'completed'
GROUP BY l.farmer_region, b.region
ORDER BY total_volume_kg DESC;

-- Top cross-regional routes
SELECT 
    l.farmer_region || ' → ' || b.region AS route,
    COUNT(*) AS order_count,
    AVG(o.distance_km) AS avg_distance_km,
    AVG(o.transport_cost_kes) AS avg_transport_cost
FROM orders o
JOIN listings l ON o.listing_id = l.listing_id
JOIN buyers b ON o.buyer_id = b.buyer_id
WHERE l.farmer_region != b.region
GROUP BY route
ORDER BY order_count DESC
LIMIT 10;
```

---

## 🚀 Deployment Checklist

- [ ] Update database schema (add region columns)
- [ ] Create `regional_analytics` table
- [ ] Implement `GET /farmer-location/{farmer_id}`
- [ ] Implement `POST /analyze-cross-regional`
- [ ] Update `POST /create-listing` with cross-regional parameters
- [ ] Implement `GET /buyer-location/{buyer_id}`
- [ ] Update `GET /search-listings` with cross-regional filters
- [ ] Add distance calculation helper function
- [ ] Add transport cost estimation helper function
- [ ] Add reverse geocoding helper function
- [ ] Populate existing records with region data (migration script)
- [ ] Set up regional analytics cron job (update every hour)
- [ ] Add monitoring dashboard for cross-regional metrics
- [ ] Test all scenarios (high competition, low competition, cross-regional search)
- [ ] Load test with 10,000+ concurrent users
- [ ] Document API changes in Swagger/OpenAPI spec

---

## 📝 Notes

### Performance Optimization
- **Cache region data**: Store farmer/buyer regions in memory cache (Redis) to avoid repeated geocoding
- **Pre-calculate analytics**: Run regional analytics cron job every hour instead of real-time calculation
- **Index database**: Add indexes on `region`, `farmer_region`, `prefer_cross_regional` columns
- **Pagination**: Limit search results to 50 per page for large result sets

### Future Enhancements
1. **Regional Price Trends**: Show historical price data by region to help farmers choose target markets
2. **Transport Coordination**: Connect farmers with shared logistics providers for cross-regional shipments
3. **Regional Demand Forecasting**: Predict which regions will have supply shortages in 30/60/90 days
4. **Multi-Region Listings**: Allow farmers to create one listing visible in multiple target regions
5. **Regional Partnerships**: Connect farmers in same region to pool supply for larger cross-regional orders

---

## 🔗 Related Documentation
- Frontend implementation: `agroshield-app/src/screens/FarmerMarketplace.js`
- Frontend implementation: `agroshield-app/src/screens/BuyerMarketplace.js`
- Database schema: `backend/migrations/`
- API routes: `backend/app/routes/`

---

**Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Author**: AgroShield Development Team
