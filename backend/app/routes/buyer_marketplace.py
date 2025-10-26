"""
Buyer Marketplace Portal (B2B/B2C)
Professional interface for food processors, restaurants, retailers, schools
to source produce directly from verified farmers
"""

from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.services import persistence
from app.services.ai_market_optimizer import market_optimizer
from app.services.cross_regional_service import (
    get_region_from_coordinates,
    search_cross_regional_listings,
    calculate_distance_km,
    estimate_transport_cost
)

router = APIRouter()


# ============================================================================
# MODELS
# ============================================================================

class BuyerRegistration(BaseModel):
    business_name: str
    business_type: str  # Processor, Restaurant, Retailer, School, Aggregator
    business_registration_number: str
    vat_number: Optional[str] = None
    contact_person: str
    phone_number: str
    email: str
    physical_address: str
    location_lat: float
    location_lon: float
    annual_volume_kg: Optional[float] = None
    payment_method: str = "M-Pesa"


class ProductRequirement(BaseModel):
    crop: str
    quantity_needed_kg: float
    quality_requirement: str  # A, B, Premium
    frequency: str  # one-time, weekly, monthly
    price_range_min: float
    price_range_max: float
    delivery_required: bool = True
    organic_only: bool = False
    additional_specs: Optional[str] = None


class BuyerOffer(BaseModel):
    listing_id: str
    quantity_kg: float
    offered_price_kes_per_kg: float
    payment_terms: str = "50% deposit, 50% on delivery"
    requested_delivery_date: str
    delivery_location: str
    transport_responsibility: str = "buyer"  # buyer or farmer
    offer_notes: Optional[str] = None


# ============================================================================
# BUYER REGISTRATION & VERIFICATION
# ============================================================================

@router.post("/register-buyer")
async def register_buyer(
    business_name: str = Form(...),
    business_type: str = Form(...),
    business_registration_number: str = Form(...),
    vat_number: Optional[str] = Form(None),
    contact_person: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    physical_address: str = Form(...),
    location_lat: float = Form(...),
    location_lon: float = Form(...),
    annual_volume_kg: Optional[float] = Form(None),
    payment_method: str = Form("M-Pesa"),
    registration_certificate: Optional[UploadFile] = File(None),
    business_license: Optional[UploadFile] = File(None)
):
    """
    Verified buyer registration with KYB (Know Your Business)
    
    Verification Requirements:
    - Business registration number (verified against government DB)
    - VAT number (for tax compliance)
    - Business license upload
    - Physical address verification
    """
    # Check if business already registered
    existing = persistence.get_buyer_by_registration_number(business_registration_number)
    if existing:
        raise HTTPException(status_code=400, detail="Business already registered")
    
    # Upload verification documents
    docs = {}
    if registration_certificate:
        cert_contents = await registration_certificate.read()
        docs["registration_certificate"] = persistence.save_buyer_document(
            business_registration_number, "registration", cert_contents
        )
    
    if business_license:
        license_contents = await business_license.read()
        docs["business_license"] = persistence.save_buyer_document(
            business_registration_number, "license", license_contents
        )
    
    # Create buyer profile
    buyer = {
        "buyer_id": f"BYR_{business_registration_number}_{int(datetime.now().timestamp())}",
        "business_name": business_name,
        "business_type": business_type,
        "business_registration_number": business_registration_number,
        "vat_number": vat_number,
        "contact_person": contact_person,
        "phone_number": phone_number,
        "email": email,
        "physical_address": physical_address,
        "location": {
            "lat": location_lat,
            "lon": location_lon
        },
        "annual_volume_kg": annual_volume_kg,
        "payment_method": payment_method,
        "verification_status": "pending",  # pending, verified, rejected
        "verification_documents": docs,
        "buyer_rating": 0,
        "total_orders": 0,
        "total_volume_kg": 0,
        "registered_at": datetime.now().isoformat(),
        "verified_at": None,
        "account_status": "active"
    }
    
    buyer_id = persistence.create_buyer_profile(buyer)
    
    # Trigger verification process
    persistence.queue_buyer_verification(buyer_id)
    
    return {
        "status": "success",
        "buyer_id": buyer_id,
        "message": "Buyer registration submitted for verification",
        "verification_status": "pending",
        "estimated_verification_time": "24-48 hours",
        "next_steps": [
            "Our team will verify your business documents",
            "You will receive an email/SMS once verified",
            "Verified buyers can browse listings and make offers",
            "Set up your Product Requirements for intelligent matching"
        ]
    }


@router.get("/buyer-profile/{buyer_id}")
async def get_buyer_profile(buyer_id: str):
    """
    Get buyer profile and statistics
    """
    buyer = persistence.get_buyer_by_id(buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    # Get buyer statistics
    contracts = persistence.get_buyer_contracts(buyer_id)
    
    stats = {
        "total_orders": len(contracts),
        "completed_orders": len([c for c in contracts if c["status"] == "completed"]),
        "active_orders": len([c for c in contracts if c["status"] in ["deposit_paid", "in_transit"]]),
        "total_volume_purchased_kg": sum(c["quantity_kg"] for c in contracts if c["status"] == "completed"),
        "total_spent_kes": sum(c["total_amount_kes"] for c in contracts if c["status"] == "completed"),
        "average_order_size_kg": sum(c["quantity_kg"] for c in contracts) / len(contracts) if contracts else 0,
        "buyer_rating": buyer.get("buyer_rating", 0),
        "on_time_payment_rate": persistence.calculate_payment_rate(buyer_id)
    }
    
    return {
        "buyer_id": buyer_id,
        "profile": buyer,
        "statistics": stats
    }


@router.post("/add-product-requirement")
async def add_product_requirement(
    buyer_id: str = Form(...),
    crop: str = Form(...),
    quantity_needed_kg: float = Form(...),
    quality_requirement: str = Form("B"),
    frequency: str = Form("one-time"),
    price_range_min: float = Form(...),
    price_range_max: float = Form(...),
    delivery_required: bool = Form(True),
    organic_only: bool = Form(False),
    additional_specs: Optional[str] = Form(None)
):
    """
    Define product requirements for intelligent matching
    
    AI uses these requirements to:
    - Match buyer with suitable farmer listings
    - Predict available supply in coming 30/60 days
    - Alert buyer when matching produce becomes available
    """
    buyer = persistence.get_buyer_by_id(buyer_id)
    if not buyer or buyer["verification_status"] != "verified":
        raise HTTPException(status_code=403, detail="Buyer not verified")
    
    requirement = {
        "requirement_id": f"REQ_{buyer_id}_{int(datetime.now().timestamp())}",
        "buyer_id": buyer_id,
        "crop": crop,
        "quantity_needed_kg": quantity_needed_kg,
        "quality_requirement": quality_requirement,
        "frequency": frequency,
        "price_range_min": price_range_min,
        "price_range_max": price_range_max,
        "delivery_required": delivery_required,
        "organic_only": organic_only,
        "additional_specs": additional_specs,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "fulfilled": False
    }
    
    req_id = persistence.create_product_requirement(requirement)
    
    # AI: Find matching listings
    matching_listings = persistence.find_matching_listings(
        crop=crop,
        min_quantity=quantity_needed_kg * 0.5,  # At least 50% match
        quality_grade=quality_requirement,
        max_price=price_range_max,
        buyer_location=(buyer["location"]["lat"], buyer["location"]["lon"]),
        organic_only=organic_only
    )
    
    # AI: Predict future supply
    future_supply = await market_optimizer._predict_regional_supply(
        crop=crop,
        harvest_date=(datetime.now() + timedelta(days=30)).isoformat(),
        lat=buyer["location"]["lat"],
        lon=buyer["location"]["lon"]
    )
    
    return {
        "status": "success",
        "requirement_id": req_id,
        "requirement": requirement,
        "immediate_matches": {
            "count": len(matching_listings),
            "listings": matching_listings[:5],
            "total_available_kg": sum(l["quantity_available_kg"] for l in matching_listings)
        },
        "supply_forecast": {
            "next_30_days": {
                "predicted_supply_kg": future_supply["total_supply_kg"],
                "farmers_harvesting": future_supply["farmers_harvesting"],
                "oversupply_risk": future_supply["oversupply_risk"]
            },
            "recommendation": "High supply expected in 30 days. Consider waiting for better prices." if future_supply["oversupply_risk"] == "high" else "Secure supply now before harvest season ends."
        }
    }


# ============================================================================
# INTELLIGENT SOURCING DASHBOARD
# ============================================================================

@router.get("/search-listings")
async def search_listings(
    buyer_id: str,
    crop: Optional[str] = None,
    min_quantity_kg: Optional[float] = None,
    max_price_kes: Optional[float] = None,
    quality_grade: Optional[str] = None,
    radius_km: int = 100,
    organic_only: bool = False,
    ready_within_days: Optional[int] = None,
    # NEW: Cross-regional parameters
    buyer_region: Optional[str] = Query(None),
    exclude_my_region: bool = Query(False),
    prefer_different_regions: bool = Query(False),
    cross_regional_only: bool = Query(False)
):
    """
    Intelligent search with PostGIS location filtering and cross-regional options
    
    Filters:
    - Location (within radius from buyer)
    - Crop type
    - Quantity available
    - Quality grade
    - Price range
    - Ready date window
    - Organic certification
    
    NEW Cross-Regional Filters:
    - exclude_my_region: Exclude suppliers from buyer's own region
    - prefer_different_regions: Prioritize regional diversity in results
    - cross_regional_only: Only show cross-regional listings
    """
    buyer = persistence.get_buyer_by_id(buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    buyer_location = (buyer["location"]["lat"], buyer["location"]["lon"])
    
    # Get buyer region if not provided
    if not buyer_region:
        region_info = get_region_from_coordinates(buyer_location[0], buyer_location[1])
        buyer_region = region_info.get("region", "Unknown")
    
    # Build search filters
    filters = {
        "crop": crop,
        "min_quantity_kg": min_quantity_kg,
        "max_price_kes": max_price_kes,
        "quality_grade": quality_grade,
        "buyer_location": buyer_location,
        "radius_km": radius_km,
        "organic_only": organic_only,
        "status": "active"
    }
    
    if ready_within_days:
        filters["ready_before"] = (datetime.now() + timedelta(days=ready_within_days)).isoformat()
    
    # Search listings (with PostGIS distance calculation)
    all_listings = persistence.search_listings(filters)
    
    # Apply cross-regional filtering
    listings = []
    excluded_local_count = 0
    
    for listing in all_listings:
        listing_region = listing.get("farmer_region", "Unknown")
        
        # Add distance calculation
        listing["distance_km"] = calculate_distance_km(
            buyer_location[0], buyer_location[1],
            listing["verification_details"]["location"]["lat"], 
            listing["verification_details"]["location"]["lon"]
        )
        
        # Exclude local region if requested
        if exclude_my_region and listing_region == buyer_region:
            excluded_local_count += 1
            continue
        
        # Cross-regional only filter
        if cross_regional_only and listing_region == buyer_region:
            excluded_local_count += 1
            continue
        
        # Add regional metadata
        listing["is_cross_regional"] = (listing_region != buyer_region)
        listing["regional_benefits"] = (
            "Diversifies supply, farmer avoids competition" if listing["is_cross_regional"] 
            else "Local supplier"
        )
        
        # Calculate transport cost
        listing["estimated_transport_cost_kes"] = estimate_transport_cost(
            listing["distance_km"],
            listing["quantity_kg"]
        )
        
        listings.append(listing)
    
    # Sort by regional diversity if requested
    if prefer_different_regions:
        from app.services.cross_regional_service import sort_by_regional_diversity
        listings = sort_by_regional_diversity(listings)
    else:
        # Sort by relevance (distance + price)
        listings.sort(key=lambda x: x["distance_km"] + (x["target_price_kes_per_kg"] / 10))
    
    # Calculate regional insights
    from app.services.cross_regional_service import calculate_regional_insights
    regional_insights = calculate_regional_insights(listings, buyer_region, excluded_local_count)
    
    return {
        "buyer_id": buyer_id,
        "search_filters": filters,
        "total_results": len(listings),
        "listings": listings,
        "regional_insights": regional_insights,
        "summary": {
            "total_available_kg": sum(l["quantity_available_kg"] for l in listings),
            "price_range": {
                "min": min((l["target_price_kes_per_kg"] for l in listings), default=0),
                "max": max((l["target_price_kes_per_kg"] for l in listings), default=0),
                "average": sum(l["target_price_kes_per_kg"] for l in listings) / len(listings) if listings else 0
            },
            "nearest_listing_km": min((l["distance_km"] for l in listings), default=0)
        }
    }


@router.get("/predicted-supply")
async def get_predicted_supply(
    buyer_id: str,
    crop: str,
    days_ahead: int = 30,
    radius_km: int = 100
):
    """
    AI-Powered: Predict available supply in coming 30/60 days
    
    Uses aggregate farmer yield predictions to forecast supply
    Allows buyers to secure supply before harvest
    """
    buyer = persistence.get_buyer_by_id(buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    buyer_location = (buyer["location"]["lat"], buyer["location"]["lon"])
    
    # Predict supply for next 30/60 days
    supply_forecast = await market_optimizer._predict_regional_supply(
        crop=crop,
        harvest_date=(datetime.now() + timedelta(days=days_ahead)).isoformat(),
        lat=buyer_location[0],
        lon=buyer_location[1]
    )
    
    # Get farmers planning to harvest
    upcoming_harvests = persistence.get_upcoming_harvests(
        crop=crop,
        location=buyer_location,
        radius_km=radius_km,
        days_ahead=days_ahead
    )
    
    return {
        "buyer_id": buyer_id,
        "crop": crop,
        "forecast_period": f"Next {days_ahead} days",
        "supply_forecast": supply_forecast,
        "upcoming_harvests": {
            "count": len(upcoming_harvests),
            "farmers": upcoming_harvests[:10],  # Top 10
            "total_predicted_yield_kg": sum(h["predicted_yield_kg"] for h in upcoming_harvests)
        },
        "ai_recommendation": _generate_buyer_supply_guidance(supply_forecast, upcoming_harvests),
        "next_steps": [
            "Contact farmers with upcoming harvests to pre-book supply",
            "Lock in prices before harvest glut" if supply_forecast["oversupply_risk"] == "high" else "Secure supply early",
            "Set up automated alerts for new matching listings"
        ]
    }


# ============================================================================
# BUYER: MAKE OFFERS
# ============================================================================

@router.post("/make-offer")
async def make_offer(
    buyer_id: str = Form(...),
    listing_id: str = Form(...),
    quantity_kg: float = Form(...),
    offered_price_kes_per_kg: float = Form(...),
    payment_terms: str = Form("50% deposit, 50% on delivery"),
    requested_delivery_date: str = Form(...),
    delivery_location: str = Form(...),
    transport_responsibility: str = Form("buyer"),
    offer_notes: Optional[str] = Form(None)
):
    """
    Make an offer to farmer on a listing
    """
    buyer = persistence.get_buyer_by_id(buyer_id)
    if not buyer or buyer["verification_status"] != "verified":
        raise HTTPException(status_code=403, detail="Buyer not verified")
    
    listing = persistence.get_listing_by_id(listing_id)
    if not listing or listing["status"] != "active":
        raise HTTPException(status_code=404, detail="Listing not available")
    
    # Validate quantity
    if quantity_kg > listing["quantity_available_kg"]:
        raise HTTPException(
            status_code=400,
            detail=f"Quantity exceeds available supply ({listing['quantity_available_kg']}kg)"
        )
    
    if quantity_kg < listing["minimum_order_kg"]:
        raise HTTPException(
            status_code=400,
            detail=f"Quantity below minimum order ({listing['minimum_order_kg']}kg)"
        )
    
    # Validate price
    if offered_price_kes_per_kg < listing["target_price_kes_per_kg"] * 0.7:
        raise HTTPException(
            status_code=400,
            detail=f"Offer too low. Farmer's target price: {listing['target_price_kes_per_kg']} KES/kg"
        )
    
    # Create offer
    offer = {
        "offer_id": f"OFR_{buyer_id}_{listing_id}_{int(datetime.now().timestamp())}",
        "buyer_id": buyer_id,
        "farmer_id": listing["farmer_id"],
        "listing_id": listing_id,
        "crop": listing["crop"],
        "quantity_kg": quantity_kg,
        "offered_price_kes_per_kg": offered_price_kes_per_kg,
        "total_offer_amount_kes": quantity_kg * offered_price_kes_per_kg,
        "payment_terms": payment_terms,
        "requested_delivery_date": requested_delivery_date,
        "delivery_location": delivery_location,
        "transport_responsibility": transport_responsibility,
        "offer_notes": offer_notes,
        "status": "pending",  # pending, accepted, countered, declined
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=3)).isoformat()
    }
    
    offer_id = persistence.create_offer(offer)
    
    # Notify farmer
    persistence.notify_farmer_new_offer(listing["farmer_id"], offer_id)
    
    return {
        "status": "success",
        "offer_id": offer_id,
        "offer": offer,
        "message": "Offer sent to farmer",
        "next_steps": [
            "Farmer has 72 hours to respond",
            "You will be notified of their decision (Accept/Counter/Decline)",
            "If accepted, you'll need to deposit 10% earnest money via M-Pesa"
        ]
    }


@router.get("/my-offers/{buyer_id}")
async def get_buyer_offers(buyer_id: str, status: str = "pending"):
    """
    Get all offers made by buyer
    """
    offers = persistence.get_buyer_offers(buyer_id, status=status)
    
    return {
        "buyer_id": buyer_id,
        "total_offers": len(offers),
        "pending_offers": len([o for o in offers if o["status"] == "pending"]),
        "accepted_offers": len([o for o in offers if o["status"] == "accepted"]),
        "offers": offers
    }


# ============================================================================
# ORDER & LOGISTICS MANAGEMENT
# ============================================================================

@router.get("/my-orders/{buyer_id}")
async def get_buyer_orders(buyer_id: str, status: str = "active"):
    """
    Get all orders/contracts for buyer
    """
    contracts = persistence.get_buyer_contracts(buyer_id, status=status)
    
    # Add tracking information
    for contract in contracts:
        if contract["status"] == "in_transit":
            contract["tracking"] = persistence.get_delivery_tracking(contract["contract_id"])
    
    return {
        "buyer_id": buyer_id,
        "total_orders": len(contracts),
        "active_orders": len([c for c in contracts if c["status"] in ["deposit_paid", "in_transit"]]),
        "completed_orders": len([c for c in contracts if c["status"] == "completed"]),
        "orders": contracts
    }


@router.post("/pay-deposit/{contract_id}")
async def pay_earnest_deposit(
    contract_id: str,
    buyer_id: str = Form(...),
    phone_number: str = Form(...)
):
    """
    Pay 10% earnest deposit via M-Pesa to secure contract
    """
    contract = persistence.get_contract_by_id(contract_id)
    
    if not contract or contract["buyer_id"] != buyer_id:
        raise HTTPException(status_code=403, detail="Contract not found or unauthorized")
    
    if contract["status"] != "pending_deposit":
        raise HTTPException(status_code=400, detail="Contract not awaiting deposit")
    
    deposit_amount = contract["total_amount_kes"] * 0.10
    
    # Trigger M-Pesa STK Push
    from app.routes.payments import process_mpesa_payment
    mpesa_response = process_mpesa_payment(
        phone_number=phone_number,
        amount=deposit_amount,
        account_reference=contract_id,
        transaction_desc=f"Earnest deposit for contract {contract_id}"
    )
    
    # Record payment
    persistence.record_contract_payment({
        "contract_id": contract_id,
        "type": "deposit",
        "amount": deposit_amount,
        "payment_method": "M-Pesa",
        "status": "pending",
        "mpesa_checkout_request_id": mpesa_response.get("CheckoutRequestID"),
        "created_at": datetime.now().isoformat()
    })
    
    return {
        "status": "success",
        "message": "M-Pesa payment initiated",
        "deposit_amount_kes": deposit_amount,
        "mpesa_response": mpesa_response,
        "next_steps": [
            "Check your phone for M-Pesa prompt",
            "Enter your M-Pesa PIN to complete payment",
            "Contract will activate once payment is confirmed",
            "Farmer will be notified to prepare produce for delivery"
        ]
    }


@router.post("/confirm-receipt/{contract_id}")
async def confirm_receipt(
    contract_id: str,
    buyer_id: str = Form(...),
    quality_acceptable: bool = Form(True),
    quality_notes: Optional[str] = Form(None),
    receipt_photos: Optional[List[UploadFile]] = File(None)
):
    """
    Buyer confirms receipt and quality
    Triggers final payment to farmer
    """
    contract = persistence.get_contract_by_id(contract_id)
    
    if not contract or contract["buyer_id"] != buyer_id:
        raise HTTPException(status_code=403, detail="Contract not found or unauthorized")
    
    if contract["status"] != "awaiting_buyer_confirmation":
        raise HTTPException(status_code=400, detail="Contract not awaiting confirmation")
    
    # Upload receipt photos
    photo_urls = []
    if receipt_photos:
        for photo in receipt_photos[:5]:
            contents = await photo.read()
            photo_path = persistence.save_receipt_photo(contract_id, contents)
            photo_urls.append(photo_path)
    
    if quality_acceptable:
        # Release final payment to farmer
        final_payment = contract["total_amount_kes"] * 0.90
        
        # Process payment to farmer's M-Pesa
        persistence.process_farmer_payment({
            "contract_id": contract_id,
            "farmer_id": contract["farmer_id"],
            "type": "final",
            "amount": final_payment,
            "payment_method": "M-Pesa",
            "status": "processing",
            "created_at": datetime.now().isoformat()
        })
        
        # Update contract
        persistence.update_contract(contract_id, {
            "status": "completed",
            "buyer_confirmed_receipt": True,
            "quality_acceptable": True,
            "buyer_quality_notes": quality_notes,
            "buyer_receipt_photos": photo_urls,
            "completed_at": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "message": "Receipt confirmed. Final payment processing.",
            "final_payment_kes": final_payment,
            "farmer_payment_status": "processing",
            "next_steps": [
                f"Farmer will receive KES {final_payment:,} in their M-Pesa within 2 hours",
                "Please rate this farmer to help improve the marketplace",
                "Contract completed successfully"
            ]
        }
    else:
        # Quality dispute
        persistence.update_contract(contract_id, {
            "status": "quality_dispute",
            "buyer_confirmed_receipt": True,
            "quality_acceptable": False,
            "buyer_quality_notes": quality_notes,
            "buyer_receipt_photos": photo_urls,
            "dispute_opened_at": datetime.now().isoformat()
        })
        
        # Open mediation
        persistence.open_dispute_mediation(contract_id, quality_notes)
        
        return {
            "status": "dispute_opened",
            "message": "Quality dispute opened. Mediation team notified.",
            "next_steps": [
                "AgroShield mediation team will review your complaint within 24 hours",
                "Both parties will be contacted for evidence",
                "Payment held in escrow until resolution",
                "Please provide additional evidence (photos, lab reports) if available"
            ]
        }


def _generate_buyer_supply_guidance(supply_forecast: Dict, upcoming_harvests: List) -> str:
    """Generate buyer guidance based on supply forecast"""
    if supply_forecast["oversupply_risk"] == "high":
        return (
            f"🟢 **Buyer's Market:** High supply expected ({supply_forecast['total_supply_kg']/1000:.1f} tonnes) "
            f"from {supply_forecast['farmers_harvesting']} farmers. "
            f"Expect prices to drop ~{abs(supply_forecast['expected_price_impact_percent'])}%. "
            f"**Strategy:** Wait for harvest peak (7-10 days) for best prices, or negotiate hard now."
        )
    elif supply_forecast["oversupply_risk"] == "medium":
        return (
            f"🟡 **Balanced Market:** Moderate supply expected ({supply_forecast['total_supply_kg']/1000:.1f} tonnes). "
            f"Prices may drop slightly (~{abs(supply_forecast['expected_price_impact_percent'])}%). "
            f"**Strategy:** Secure supply from top-quality farmers now before competition increases."
        )
    else:
        return (
            f"🔴 **Seller's Market:** Low supply expected ({supply_forecast['total_supply_kg']/1000:.1f} tonnes). "
            f"Prices may rise. **Urgent:** Pre-book supply now with direct contracts to avoid shortages."
        )


# ============================================================================
# CROSS-REGIONAL MARKETPLACE ENDPOINTS
# ============================================================================

@router.get("/buyer-location/{buyer_id}")
async def get_buyer_location(buyer_id: str):
    """
    Get buyer's business location and administrative region
    
    Returns:
        - GPS coordinates
        - Region name
        - Business details
    """
    try:
        # Get buyer profile
        buyer = persistence.get_buyer_by_id(buyer_id)
        if not buyer:
            raise HTTPException(status_code=404, detail="Buyer not found")
        
        # Get location from buyer profile
        location = buyer.get("location", {})
        latitude = location.get("lat", 0)
        longitude = location.get("lon", 0)
        
        # Get region information
        if latitude and longitude:
            region_info = get_region_from_coordinates(latitude, longitude)
        else:
            region_info = {"region": "Unknown", "county": "Unknown"}
        
        return {
            "buyer_id": buyer_id,
            "business_name": buyer.get("business_name", ""),
            "business_type": buyer.get("business_type", ""),
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "region": region_info.get("region", "Unknown"),
            "county": region_info.get("county", "Unknown"),
            "verified": buyer.get("verification_status") == "verified"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting buyer location: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting buyer location: {str(e)}")

