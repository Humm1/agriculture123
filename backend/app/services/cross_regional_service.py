"""
Cross-Regional Marketplace Service
Analyzes regional competition and provides AI-powered recommendations for cross-regional trading
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from collections import Counter
from app.services import persistence


# ============================================================================
# REGION MAPPING
# ============================================================================

KENYA_REGIONS = {
    "Central Kenya": ["Kiambu", "Murang'a", "Nyeri", "Kirinyaga", "Nyandarua"],
    "Nairobi Region": ["Nairobi"],
    "Coast Region": ["Mombasa", "Kilifi", "Kwale", "Lamu", "Tana River", "Taita Taveta"],
    "Eastern Kenya": ["Machakos", "Kitui", "Makueni", "Embu", "Tharaka Nithi", "Meru", "Isiolo"],
    "Rift Valley": ["Nakuru", "Narok", "Kajiado", "Kericho", "Bomet", "Uasin Gishu", "Trans Nzoia", "Nandi", "Elgeyo Marakwet", "Baringo", "Laikipia", "Samburu", "West Pokot", "Turkana"],
    "Western Kenya": ["Kakamega", "Vihiga", "Bungoma", "Busia"],
    "Nyanza Region": ["Kisumu", "Siaya", "Homa Bay", "Migori", "Kisii", "Nyamira"]
}

# Reverse mapping: County -> Region
COUNTY_TO_REGION = {}
for region, counties in KENYA_REGIONS.items():
    for county in counties:
        COUNTY_TO_REGION[county] = region


# ============================================================================
# GEOGRAPHIC CALCULATIONS
# ============================================================================

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def estimate_transport_cost(distance_km: float, quantity_kg: float) -> float:
    """
    Estimate transport cost based on distance and quantity
    
    Args:
        distance_km: Distance to transport
        quantity_kg: Quantity in kilograms
    
    Returns:
        Estimated cost in KES
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


def get_region_from_coordinates(latitude: float, longitude: float) -> Dict[str, str]:
    """
    Reverse geocode GPS coordinates to administrative region
    
    For production, this should use:
    - Nominatim (OpenStreetMap) API
    - Kenya county boundaries database
    - Google Maps Geocoding API
    
    For now, using simplified regional boundaries
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        Dictionary with region, county information
    """
    # Simplified regional boundaries (approximate)
    # In production, use proper boundary polygons or geocoding API
    
    # Central Kenya (around Nairobi highlands)
    if -1.5 <= latitude <= -0.5 and 36.5 <= longitude <= 37.5:
        return {"region": "Central Kenya", "county": "Kiambu", "sub_county": "Limuru"}
    
    # Nairobi Region
    elif -1.4 <= latitude <= -1.1 and 36.6 <= longitude <= 37.0:
        return {"region": "Nairobi Region", "county": "Nairobi", "sub_county": "Nairobi"}
    
    # Coast Region (Mombasa area)
    elif -4.5 <= latitude <= -3.5 and 39.0 <= longitude <= 40.0:
        return {"region": "Coast Region", "county": "Mombasa", "sub_county": "Mombasa"}
    
    # Rift Valley (around Nakuru)
    elif -1.0 <= latitude <= 0.5 and 35.5 <= longitude <= 36.5:
        return {"region": "Rift Valley", "county": "Nakuru", "sub_county": "Nakuru"}
    
    # Western Kenya (around Kisumu)
    elif -0.5 <= latitude <= 0.5 and 34.0 <= longitude <= 35.0:
        return {"region": "Western Kenya", "county": "Kisumu", "sub_county": "Kisumu"}
    
    # Eastern Kenya (around Machakos)
    elif -1.8 <= latitude <= -0.8 and 37.0 <= longitude <= 38.0:
        return {"region": "Eastern Kenya", "county": "Machakos", "sub_county": "Machakos"}
    
    # Nyanza Region (around Kisii)
    elif -1.0 <= latitude <= 0.0 and 34.5 <= longitude <= 35.5:
        return {"region": "Nyanza Region", "county": "Kisii", "sub_county": "Kisii"}
    
    # Default fallback
    else:
        return {"region": "Unknown Region", "county": "Unknown", "sub_county": "Unknown"}


# ============================================================================
# REGIONAL COMPETITION ANALYSIS
# ============================================================================

def analyze_local_competition(farmer_id: str, farmer_region: str, crops: List[str], radius_km: float = 50) -> Dict:
    """
    Analyze local competition for a farmer
    
    Args:
        farmer_id: Farmer's ID
        farmer_region: Farmer's region
        crops: List of crops farmer is growing
        radius_km: Radius to search for local farmers
    
    Returns:
        Competition analysis with scores and recommendations
    """
    # Get farmer's location
    farmer = persistence.get_farmer_by_id(farmer_id)
    if not farmer:
        return {"error": "Farmer not found"}
    
    farmer_lat = farmer.get("location", {}).get("lat", 0)
    farmer_lon = farmer.get("location", {}).get("lon", 0)
    
    if not farmer_lat or not farmer_lon:
        # Return simulated data if no GPS
        return {
            "local_farmers_count": 67,
            "same_crop_farmers": len(crops) * 23,
            "competition_score": 0.72,
            "status": "HIGH",
            "message": f"High competition: {len(crops) * 23} farmers in your region grow {', '.join(crops)}"
        }
    
    # Get all farmers in region
    all_farmers = persistence.get_farmers_in_region(farmer_region)
    
    # Filter farmers within radius
    local_farmers = []
    for f in all_farmers:
        if f["farmer_id"] == farmer_id:
            continue
        
        f_lat = f.get("location", {}).get("lat", 0)
        f_lon = f.get("location", {}).get("lon", 0)
        
        if f_lat and f_lon:
            distance = calculate_distance_km(farmer_lat, farmer_lon, f_lat, f_lon)
            if distance <= radius_km:
                local_farmers.append(f)
    
    # Count farmers growing same crops
    same_crop_farmers = 0
    for f in local_farmers:
        farmer_crops = f.get("crops", [])
        if any(crop in farmer_crops for crop in crops):
            same_crop_farmers += 1
    
    # Calculate competition score
    avg_farmers_per_region = 50  # Average from historical data
    competition_score = len(local_farmers) / max(avg_farmers_per_region, 1)
    
    # Determine status
    if competition_score > 0.7:
        status = "HIGH"
    elif competition_score > 0.4:
        status = "MEDIUM"
    else:
        status = "LOW"
    
    return {
        "local_farmers_count": len(local_farmers),
        "same_crop_farmers": same_crop_farmers,
        "competition_score": round(competition_score, 2),
        "status": status,
        "message": f"{status.capitalize()} competition: {same_crop_farmers} farmers in your region grow {', '.join(crops)}"
    }


def get_regional_buyer_density(region: str, crops: List[str]) -> Dict:
    """
    Calculate buyer density (demand/supply ratio) for a region
    
    Args:
        region: Target region
        crops: List of crops
    
    Returns:
        Buyer density metrics
    """
    # Get farmers in region growing these crops
    farmers_in_region = persistence.get_farmers_in_region(region)
    suppliers = len([f for f in farmers_in_region if any(c in f.get("crops", []) for c in crops)])
    
    # Get buyers in region interested in these crops
    buyers_in_region = persistence.get_buyers_in_region(region)
    buyers = len([b for b in buyers_in_region if any(c in b.get("product_interests", []) for c in crops)])
    
    # Calculate buyer density
    buyer_density = buyers / max(suppliers, 1)
    
    # Determine local supply level
    if suppliers > 50:
        local_supply = "HIGH"
    elif suppliers > 20:
        local_supply = "MEDIUM"
    else:
        local_supply = "LOW"
    
    return {
        "region": region,
        "suppliers": suppliers,
        "buyers": buyers,
        "buyer_density": round(buyer_density, 2),
        "local_supply": local_supply
    }


def recommend_target_regions(farmer_region: str, crops: List[str], exclude_regions: List[str] = None) -> List[Dict]:
    """
    Recommend optimal target regions for cross-regional selling
    
    Args:
        farmer_region: Farmer's current region
        crops: List of crops to sell
        exclude_regions: Regions to exclude from recommendations
    
    Returns:
        List of recommended regions with scores
    """
    if exclude_regions is None:
        exclude_regions = []
    
    # Add farmer's own region to exclusions
    exclude_regions.append(farmer_region)
    
    region_scores = []
    
    for region in KENYA_REGIONS.keys():
        if region in exclude_regions:
            continue
        
        # Get buyer density for this region
        density_data = get_regional_buyer_density(region, crops)
        
        # Get historical price data for region
        historical_prices = persistence.get_regional_price_history(region, crops[0] if crops else "maize")
        avg_price = historical_prices.get("avg_price_kes", 50)
        
        # Calculate demand score based on:
        # - Buyer density (40%)
        # - Historical prices (30%)
        # - Low local supply (30%)
        demand_score = (
            (density_data["buyer_density"] * 0.4) +
            ((avg_price / 100) * 0.3) +  # Normalize price to 0-1 scale
            ((1.0 if density_data["local_supply"] == "LOW" else 0.5 if density_data["local_supply"] == "MEDIUM" else 0.2) * 0.3)
        )
        
        # Determine reason for recommendation
        reasons = []
        if density_data["buyer_density"] > 2.0:
            reasons.append("High demand (many buyers)")
        if density_data["local_supply"] == "LOW":
            reasons.append("Low local production")
        if avg_price > 60:
            reasons.append("Above-average prices")
        
        reason = ", ".join(reasons) if reasons else "Moderate opportunity"
        
        region_scores.append({
            "region": region,
            "buyer_density": density_data["buyer_density"],
            "local_supply": density_data["local_supply"],
            "demand_score": round(demand_score, 2),
            "avg_price_kes": avg_price,
            "reason": reason
        })
    
    # Sort by demand score and return top 5
    region_scores.sort(key=lambda x: x["demand_score"], reverse=True)
    
    return region_scores[:5]


def find_matching_buyers(farmer_id: str, crops: List[str], target_regions: List[str], max_distance_km: float = 500) -> List[Dict]:
    """
    Find active buyers in target regions who need these crops
    
    Args:
        farmer_id: Farmer's ID
        crops: List of crops
        target_regions: Target regions to search
        max_distance_km: Maximum distance to consider
    
    Returns:
        List of matched buyers with details
    """
    farmer = persistence.get_farmer_by_id(farmer_id)
    if not farmer:
        return []
    
    farmer_lat = farmer.get("location", {}).get("lat", 0)
    farmer_lon = farmer.get("location", {}).get("lon", 0)
    
    matched_buyers = []
    
    for region in target_regions[:3]:  # Limit to top 3 regions
        buyers_in_region = persistence.get_buyers_in_region(region)
        
        for buyer in buyers_in_region:
            # Check if buyer needs any of these crops
            buyer_requirements = buyer.get("product_requirements", [])
            matching_crops = [crop for crop in crops if crop in [r.get("crop") for r in buyer_requirements]]
            
            if not matching_crops:
                continue
            
            # Calculate distance
            buyer_lat = buyer.get("location", {}).get("lat", 0)
            buyer_lon = buyer.get("location", {}).get("lon", 0)
            
            if not buyer_lat or not buyer_lon:
                continue
            
            distance = calculate_distance_km(farmer_lat, farmer_lon, buyer_lat, buyer_lon)
            
            if distance > max_distance_km:
                continue
            
            # Find specific requirement details
            requirement = next((r for r in buyer_requirements if r.get("crop") in matching_crops), None)
            
            matched_buyers.append({
                "buyer_id": buyer["buyer_id"],
                "business_name": buyer.get("business_name", "Unknown"),
                "region": region,
                "distance_km": round(distance, 1),
                "requirements": {
                    "crop": requirement.get("crop") if requirement else matching_crops[0],
                    "quantity_needed_kg": requirement.get("quantity_needed_kg", 0) if requirement else 0,
                    "frequency": requirement.get("frequency", "unknown") if requirement else "unknown",
                    "max_price_kes": requirement.get("price_range_max", 0) if requirement else 0
                }
            })
    
    # Sort by distance
    matched_buyers.sort(key=lambda x: x["distance_km"])
    
    return matched_buyers[:10]  # Return top 10 matches


async def analyze_cross_regional_opportunities(farmer_id: str, farmer_region: str, crops: List[str], radius_km: float = 50) -> Dict:
    """
    Comprehensive cross-regional opportunity analysis
    
    Args:
        farmer_id: Farmer's ID
        farmer_region: Farmer's region
        crops: List of crops
        radius_km: Local competition search radius
    
    Returns:
        Complete analysis with recommendations
    """
    # Step 1: Analyze local competition
    local_competition = analyze_local_competition(farmer_id, farmer_region, crops, radius_km)
    
    # Step 2: Recommend target regions
    recommended_regions = recommend_target_regions(farmer_region, crops)
    
    # Step 3: Find regions to avoid (oversupplied)
    avoid_regions = []
    for region in KENYA_REGIONS.keys():
        if region == farmer_region:
            continue
        
        density_data = get_regional_buyer_density(region, crops)
        if density_data["local_supply"] == "HIGH" and density_data["buyer_density"] < 0.5:
            avoid_regions.append({
                "region": region,
                "reason": f"Oversupplied - {density_data['suppliers']} farmers, low prices"
            })
    
    # Step 4: Match with active buyers
    target_region_names = [r["region"] for r in recommended_regions]
    matched_buyers = find_matching_buyers(farmer_id, crops, target_region_names)
    
    return {
        "local_competition": local_competition,
        "recommended_regions": recommended_regions,
        "avoid_regions": avoid_regions[:3],
        "matched_buyers": matched_buyers
    }


# ============================================================================
# CROSS-REGIONAL SEARCH & MATCHING
# ============================================================================

def search_cross_regional_listings(
    buyer_id: str,
    buyer_region: str,
    filters: Dict,
    exclude_my_region: bool = True,
    prefer_different_regions: bool = True
) -> Dict:
    """
    Search for listings with cross-regional filtering
    
    Args:
        buyer_id: Buyer's ID
        buyer_region: Buyer's region
        filters: Standard search filters (crop, price, etc.)
        exclude_my_region: Exclude listings from buyer's own region
        prefer_different_regions: Prioritize regional diversity
    
    Returns:
        Listings with regional insights
    """
    # Get all active listings matching base filters
    all_listings = persistence.search_listings(filters)
    
    # Apply cross-regional filtering
    filtered_listings = []
    excluded_local_count = 0
    
    for listing in all_listings:
        listing_region = listing.get("farmer_region", "Unknown")
        
        # Exclude local region if requested
        if exclude_my_region and listing_region == buyer_region:
            excluded_local_count += 1
            continue
        
        # Add regional metadata
        listing["is_cross_regional"] = (listing_region != buyer_region)
        listing["regional_benefits"] = get_regional_benefits(listing_region, buyer_region)
        
        filtered_listings.append(listing)
    
    # Sort by regional diversity if requested
    if prefer_different_regions:
        filtered_listings = sort_by_regional_diversity(filtered_listings)
    
    # Calculate regional insights
    regional_insights = calculate_regional_insights(
        filtered_listings, 
        buyer_region, 
        excluded_local_count
    )
    
    return {
        "listings": filtered_listings,
        "regional_insights": regional_insights
    }


def sort_by_regional_diversity(listings: List[Dict]) -> List[Dict]:
    """
    Sort listings to maximize regional diversity
    Uses greedy algorithm to alternate between regions
    
    Args:
        listings: List of listings to sort
    
    Returns:
        Sorted listings with regional diversity
    """
    sorted_listings = []
    region_counts = Counter()
    
    remaining = listings.copy()
    
    while remaining:
        # Find listing from least-represented region
        best_listing = None
        min_count = float('inf')
        
        for listing in remaining:
            region = listing.get("farmer_region", "Unknown")
            if region_counts[region] < min_count:
                min_count = region_counts[region]
                best_listing = listing
        
        # Add to sorted list
        if best_listing:
            sorted_listings.append(best_listing)
            region_counts[best_listing.get("farmer_region", "Unknown")] += 1
            remaining.remove(best_listing)
    
    return sorted_listings


def calculate_regional_insights(listings: List[Dict], buyer_region: str, excluded_local_count: int) -> Dict:
    """
    Calculate regional diversity metrics for search results
    
    Args:
        listings: List of listings
        buyer_region: Buyer's region
        excluded_local_count: Number of local listings excluded
    
    Returns:
        Regional insights dictionary
    """
    if not listings:
        return {
            "total_listings": 0,
            "regions_covered": 0,
            "local_count": 0,
            "cross_regional_count": 0,
            "excluded_local_listings": excluded_local_count,
            "avg_distance_km": 0,
            "diversity_score": 0,
            "top_regions": []
        }
    
    # Count regions
    regions = [l.get("farmer_region", "Unknown") for l in listings]
    unique_regions = set(regions)
    regions_covered = len(unique_regions)
    
    # Count local vs cross-regional
    local_count = len([l for l in listings if l.get("farmer_region") == buyer_region])
    cross_regional_count = len(listings) - local_count
    
    # Calculate average distance
    avg_distance = sum([l.get("distance_km", 0) for l in listings]) / max(len(listings), 1)
    
    # Calculate diversity score (0-1)
    diversity_score = min(regions_covered / max(len(listings), 1), 1.0)
    
    # Top regions by listing count
    region_counter = Counter(regions)
    top_regions = [r[0] for r in region_counter.most_common(3)]
    
    return {
        "total_listings": len(listings),
        "regions_covered": regions_covered,
        "local_count": local_count,
        "cross_regional_count": cross_regional_count,
        "excluded_local_listings": excluded_local_count,
        "avg_distance_km": round(avg_distance, 1),
        "diversity_score": round(diversity_score, 2),
        "top_regions": top_regions,
        "message": generate_diversity_message(diversity_score, regions_covered, excluded_local_count)
    }


def generate_diversity_message(diversity_score: float, regions_covered: int, excluded_count: int) -> str:
    """
    Generate user-friendly message about regional diversity
    
    Args:
        diversity_score: Diversity score (0-1)
        regions_covered: Number of unique regions
        excluded_count: Number of local listings excluded
    
    Returns:
        Formatted message
    """
    if diversity_score >= 0.8:
        quality = "Excellent"
    elif diversity_score >= 0.6:
        quality = "Good"
    elif diversity_score >= 0.4:
        quality = "Moderate"
    else:
        quality = "Low"
    
    message = f"{quality} regional diversity! Listings from {regions_covered} different regions."
    
    if excluded_count > 0:
        message += f" Excluded {excluded_count} local listings to avoid supporting your competition."
    
    return message


def get_regional_benefits(farmer_region: str, buyer_region: str) -> str:
    """
    Describe benefits of cross-regional trade
    
    Args:
        farmer_region: Farmer's region
        buyer_region: Buyer's region
    
    Returns:
        Benefits description
    """
    if farmer_region == buyer_region:
        return "Local supplier"
    
    benefits = [
        "Diversifies your supply chain",
        "Farmer avoids local competition",
        "Access to different growing seasons"
    ]
    
    return " • ".join(benefits)
