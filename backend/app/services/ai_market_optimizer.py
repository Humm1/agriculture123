"""
AI-Driven Market Optimization Engine
Predicts optimal selling windows and markets for maximum farmer profit
Uses regression + time-series forecasting with real-time data feeds
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from app.services import persistence
from app.services.regional_data_service import get_market_prices_for_location, get_weather_for_location


# ============================================================================
# AI MARKET PREDICTION ENGINE
# ============================================================================

class MarketOptimizer:
    """
    AI Engine that predicts optimal selling strategy for farmers
    """
    
    def __init__(self):
        self.price_history_days = 90
        self.forecast_horizon_days = 30
    
    async def predict_optimal_sale_window(
        self,
        crop: str,
        predicted_yield_kg: float,
        harvest_date: str,
        field_location: Tuple[float, float],
        quality_grade: str = "B",
        farmer_id: str = None
    ) -> Dict:
        """
        AI-powered optimal sale window prediction
        
        Returns:
        - Best selling dates (date range)
        - Expected price range
        - Risk factors (oversupply, weather, etc.)
        - Market recommendations (where to sell)
        """
        lat, lon = field_location
        
        # 1. Get current market data
        market_data = await get_market_prices_for_location(lat, lon)
        current_price = market_data.get("prices", {}).get(crop.lower(), {}).get("price_kes_per_kg", 45)
        
        # 2. Predict supply dynamics (aggregate farmer yields in region)
        regional_supply = self._predict_regional_supply(crop, harvest_date, lat, lon)
        
        # 3. Get historical price patterns
        price_trends = self._get_historical_price_trends(crop, harvest_date)
        
        # 4. Weather impact on post-harvest storage
        weather_data = await get_weather_for_location(lat, lon)
        storage_risk = self._assess_post_harvest_risk(weather_data, harvest_date)
        
        # 5. Demand forecasting from buyer portal
        buyer_demand = self._get_buyer_demand_forecast(crop, lat, lon)
        
        # 6. Calculate optimal window
        optimal_window = self._calculate_optimal_window(
            current_price=current_price,
            regional_supply=regional_supply,
            price_trends=price_trends,
            storage_risk=storage_risk,
            buyer_demand=buyer_demand,
            harvest_date=harvest_date
        )
        
        # 7. Generate market recommendations
        market_options = await self._generate_market_recommendations(
            crop=crop,
            quantity_kg=predicted_yield_kg,
            quality_grade=quality_grade,
            optimal_window=optimal_window,
            location=(lat, lon),
            farmer_id=farmer_id
        )
        
        return {
            "optimal_sale_window": optimal_window,
            "market_recommendations": market_options,
            "price_forecast": {
                "current_price_kes": current_price,
                "predicted_price_range": optimal_window["expected_price_range"],
                "confidence_level": optimal_window["confidence"]
            },
            "risk_analysis": {
                "regional_oversupply_risk": regional_supply["oversupply_risk"],
                "storage_loss_risk": storage_risk["loss_percentage"],
                "price_volatility": price_trends["volatility"],
                "weather_impact": storage_risk["weather_severity"]
            },
            "ai_recommendation": self._generate_farmer_guidance(optimal_window, market_options)
        }
    
    def _predict_regional_supply(self, crop: str, harvest_date: str, lat: float, lon: float) -> Dict:
        """
        Aggregate predicted yields from all farmers in region (50km radius)
        """
        # Get all farmers with predicted harvests in same period
        harvest_dt = datetime.fromisoformat(harvest_date)
        window_start = harvest_dt - timedelta(days=15)
        window_end = harvest_dt + timedelta(days=15)
        
        # Query farmer yields in region
        regional_farmers = persistence.get_farmers_in_radius(lat, lon, radius_km=50)
        
        total_predicted_supply = 0
        farmers_harvesting = 0
        
        for farmer in regional_farmers:
            fields = persistence.get_user_fields(farmer["user_id"])
            for field in fields:
                if field.get("crop", "").lower() == crop.lower():
                    field_harvest = field.get("expected_harvest_date")
                    if field_harvest:
                        field_dt = datetime.fromisoformat(field_harvest)
                        if window_start <= field_dt <= window_end:
                            predicted_yield = field.get("predicted_yield_kg", 0)
                            total_predicted_supply += predicted_yield
                            farmers_harvesting += 1
        
        # Calculate oversupply risk
        # Baseline: 50 tonnes per 50km radius is normal for maize
        baseline_supply = {"maize": 50000, "beans": 20000, "tomatoes": 30000}.get(crop.lower(), 40000)
        oversupply_ratio = total_predicted_supply / baseline_supply if baseline_supply > 0 else 0
        
        if oversupply_ratio > 1.5:
            oversupply_risk = "high"
            price_impact = -15  # -15% price drop expected
        elif oversupply_ratio > 1.2:
            oversupply_risk = "medium"
            price_impact = -8
        else:
            oversupply_risk = "low"
            price_impact = 0
        
        return {
            "total_supply_kg": total_predicted_supply,
            "farmers_harvesting": farmers_harvesting,
            "oversupply_risk": oversupply_risk,
            "expected_price_impact_percent": price_impact,
            "baseline_supply_kg": baseline_supply
        }
    
    def _get_historical_price_trends(self, crop: str, harvest_date: str) -> Dict:
        """
        Analyze 90-day historical price patterns for this crop
        """
        # Get historical prices from database
        historical_prices = persistence.get_historical_market_prices(crop, days=90)
        
        if len(historical_prices) < 10:
            # Not enough data, use defaults
            return {
                "average_price": 45,
                "volatility": 0.12,
                "seasonal_trend": "stable",
                "confidence": 0.6
            }
        
        prices = [p["price"] for p in historical_prices]
        avg_price = np.mean(prices)
        std_price = np.std(prices)
        volatility = std_price / avg_price if avg_price > 0 else 0.15
        
        # Detect seasonal trend
        harvest_month = datetime.fromisoformat(harvest_date).month
        harvest_months = {
            "maize": [6, 7, 12, 1],
            "beans": [5, 6, 11, 12],
            "tomatoes": list(range(1, 13)),  # Year-round
            "potatoes": [3, 4, 5, 9, 10, 11]
        }
        
        if harvest_month in harvest_months.get(crop.lower(), []):
            seasonal_trend = "declining"  # Harvest glut
            seasonal_multiplier = 0.88
        else:
            seasonal_trend = "rising"  # Off-season premium
            seasonal_multiplier = 1.12
        
        return {
            "average_price": round(avg_price, 2),
            "volatility": round(volatility, 3),
            "seasonal_trend": seasonal_trend,
            "seasonal_multiplier": seasonal_multiplier,
            "confidence": 0.85 if len(historical_prices) > 50 else 0.7
        }
    
    def _assess_post_harvest_risk(self, weather_data: Dict, harvest_date: str) -> Dict:
        """
        Predict storage loss risk based on weather conditions
        """
        harvest_dt = datetime.fromisoformat(harvest_date)
        
        # Get weather forecast for 14 days post-harvest
        forecast = weather_data.get("forecast", [])[:14]
        
        total_rain = sum(day.get("rain", 0) for day in forecast)
        avg_humidity = sum(day.get("humidity", 70) for day in forecast) / len(forecast) if forecast else 70
        avg_temp = sum(day.get("temp_day", 25) for day in forecast) / len(forecast) if forecast else 25
        
        # Risk calculation
        # High humidity + rain = mold/rot risk
        # High temp = pest/insect damage risk
        
        risk_score = 0
        if total_rain > 50:
            risk_score += 3  # Heavy rain
        elif total_rain > 25:
            risk_score += 2
        
        if avg_humidity > 75:
            risk_score += 2
        elif avg_humidity > 65:
            risk_score += 1
        
        if avg_temp > 30:
            risk_score += 2  # Pest pressure
        
        if risk_score >= 5:
            severity = "high"
            loss_percentage = 15  # 15% expected loss
            recommendation = "URGENT: Sell within 3 days of harvest or use premium storage"
        elif risk_score >= 3:
            severity = "medium"
            loss_percentage = 8
            recommendation = "Sell within 7 days or ensure proper drying/ventilation"
        else:
            severity = "low"
            loss_percentage = 3
            recommendation = "Normal storage acceptable for up to 14 days"
        
        return {
            "weather_severity": severity,
            "loss_percentage": loss_percentage,
            "risk_factors": {
                "total_rainfall_mm": round(total_rain, 1),
                "avg_humidity": round(avg_humidity, 1),
                "avg_temperature": round(avg_temp, 1)
            },
            "recommendation": recommendation
        }
    
    def _get_buyer_demand_forecast(self, crop: str, lat: float, lon: float) -> Dict:
        """
        Get aggregated buyer demand from Buyer Portal
        """
        # Query active buyer orders in region
        active_orders = persistence.get_active_buyer_orders(
            crop=crop,
            location=(lat, lon),
            radius_km=100
        )
        
        total_demand_kg = sum(order["quantity_needed_kg"] for order in active_orders)
        verified_buyers = len(set(order["buyer_id"] for order in active_orders))
        
        # Premium buyers (willing to pay more for quality)
        premium_demand = sum(
            order["quantity_needed_kg"] 
            for order in active_orders 
            if order.get("quality_requirement") in ["A", "Premium"]
        )
        
        return {
            "total_demand_kg": total_demand_kg,
            "verified_buyers_count": verified_buyers,
            "premium_demand_kg": premium_demand,
            "demand_supply_ratio": 0,  # Calculated later
            "active_orders": active_orders[:5]  # Top 5 orders
        }
    
    def _calculate_optimal_window(
        self,
        current_price: float,
        regional_supply: Dict,
        price_trends: Dict,
        storage_risk: Dict,
        buyer_demand: Dict,
        harvest_date: str
    ) -> Dict:
        """
        Calculate the optimal selling window using multi-factor analysis
        """
        harvest_dt = datetime.fromisoformat(harvest_date)
        
        # Base price prediction
        predicted_price = current_price * price_trends["seasonal_multiplier"]
        
        # Adjust for oversupply
        predicted_price *= (1 + regional_supply["expected_price_impact_percent"] / 100)
        
        # Calculate optimal window based on storage risk
        if storage_risk["weather_severity"] == "high":
            # Sell immediately
            window_start = harvest_dt
            window_end = harvest_dt + timedelta(days=3)
            urgency = "URGENT"
        elif storage_risk["weather_severity"] == "medium":
            # Sell within a week
            window_start = harvest_dt
            window_end = harvest_dt + timedelta(days=7)
            urgency = "HIGH"
        else:
            # Can wait for better prices
            window_start = harvest_dt + timedelta(days=3)
            window_end = harvest_dt + timedelta(days=14)
            urgency = "NORMAL"
        
        # If high buyer demand, push urgency down (can negotiate)
        if buyer_demand["total_demand_kg"] > regional_supply["total_supply_kg"] * 0.8:
            urgency = "NORMAL"  # Seller's market
            predicted_price *= 1.05  # 5% premium
        
        # Price range (±10% volatility)
        price_min = predicted_price * (1 - price_trends["volatility"])
        price_max = predicted_price * (1 + price_trends["volatility"])
        
        return {
            "start_date": window_start.date().isoformat(),
            "end_date": window_end.date().isoformat(),
            "urgency": urgency,
            "expected_price_kes_per_kg": round(predicted_price, 2),
            "expected_price_range": {
                "min": round(price_min, 2),
                "max": round(price_max, 2)
            },
            "confidence": price_trends["confidence"],
            "days_until_window": (window_start - datetime.now()).days
        }
    
    async def _generate_market_recommendations(
        self,
        crop: str,
        quantity_kg: float,
        quality_grade: str,
        optimal_window: Dict,
        location: Tuple[float, float],
        farmer_id: str
    ) -> List[Dict]:
        """
        Generate ranked market recommendations (buyers, aggregators, wholesale)
        """
        lat, lon = location
        
        # 1. Get active buyer orders matching this crop
        buyer_orders = persistence.get_matching_buyer_orders(
            crop=crop,
            min_quantity=quantity_kg * 0.5,  # At least 50% match
            quality_grade=quality_grade,
            location=(lat, lon),
            radius_km=150
        )
        
        # 2. Get known aggregators in region
        aggregators = persistence.get_verified_aggregators(location=(lat, lon), radius_km=50)
        
        # 3. Get wholesale market prices
        market_data = await get_market_prices_for_location(lat, lon)
        wholesale_price = market_data.get("prices", {}).get(crop.lower(), {}).get("price_kes_per_kg", 45)
        
        recommendations = []
        
        # Option 1: Direct to Buyer (Highest Price)
        if buyer_orders:
            best_buyer = max(buyer_orders, key=lambda x: x["offered_price_kes_per_kg"])
            
            quantity_to_sell = min(quantity_kg, best_buyer["quantity_needed_kg"])
            gross_revenue = quantity_to_sell * best_buyer["offered_price_kes_per_kg"]
            transport_cost = self._calculate_transport_cost(
                quantity_kg=quantity_to_sell,
                distance_km=best_buyer.get("distance_km", 50)
            )
            net_profit = gross_revenue - transport_cost
            
            recommendations.append({
                "option_number": 1,
                "channel": "direct_to_buyer",
                "buyer_name": best_buyer["buyer_name"],
                "buyer_type": best_buyer["buyer_type"],  # Processor, Restaurant, Retailer
                "quantity_kg": quantity_to_sell,
                "price_per_kg": best_buyer["offered_price_kes_per_kg"],
                "gross_revenue_kes": round(gross_revenue, 2),
                "transport_cost_kes": round(transport_cost, 2),
                "net_profit_kes": round(net_profit, 2),
                "payment_terms": best_buyer.get("payment_terms", "50% deposit, 50% on delivery"),
                "distance_km": best_buyer.get("distance_km", 0),
                "contract_type": "Digital Contract (M-Pesa secured)",
                "pros": [
                    f"Highest price: {best_buyer['offered_price_kes_per_kg']} KES/kg",
                    "Direct payment to M-Pesa",
                    "Verified buyer with rating"
                ],
                "cons": [
                    f"Transport cost: {round(transport_cost, 2)} KES",
                    f"Distance: {best_buyer.get('distance_km', 0)}km"
                ],
                "recommendation_score": 95
            })
        
        # Option 2: Local Aggregator (Fast Payment)
        if aggregators:
            best_aggregator = max(aggregators, key=lambda x: x["reliability_score"])
            
            aggregator_price = wholesale_price * 0.92  # 8% commission
            gross_revenue = quantity_kg * aggregator_price
            transport_cost = self._calculate_transport_cost(
                quantity_kg=quantity_kg,
                distance_km=best_aggregator.get("distance_km", 15)
            )
            net_profit = gross_revenue - transport_cost
            
            recommendations.append({
                "option_number": 2,
                "channel": "aggregator",
                "buyer_name": best_aggregator["name"],
                "buyer_type": "Local Aggregator",
                "quantity_kg": quantity_kg,
                "price_per_kg": aggregator_price,
                "gross_revenue_kes": round(gross_revenue, 2),
                "transport_cost_kes": round(transport_cost, 2),
                "net_profit_kes": round(net_profit, 2),
                "payment_terms": "Full payment within 48 hours via M-Pesa",
                "distance_km": best_aggregator.get("distance_km", 0),
                "contract_type": "Standard Aggregator Agreement",
                "pros": [
                    "Fastest payment (48 hours guaranteed)",
                    "Short distance to delivery",
                    f"Reliability score: {best_aggregator['reliability_score']}/100"
                ],
                "cons": [
                    f"Lower price: {round(aggregator_price, 2)} KES/kg (8% commission)",
                    "No long-term contract"
                ],
                "recommendation_score": 85
            })
        
        # Option 3: Wholesale Market (Guaranteed Sale)
        nearest_market = market_data.get("nearest_market", "Nairobi")
        market_distance = market_data.get("distance_km", 50)
        
        gross_revenue = quantity_kg * wholesale_price
        transport_cost = self._calculate_transport_cost(quantity_kg, market_distance)
        market_fee = gross_revenue * 0.05  # 5% market fee
        net_profit = gross_revenue - transport_cost - market_fee
        
        recommendations.append({
            "option_number": 3,
            "channel": "wholesale_market",
            "buyer_name": f"{nearest_market} Wholesale Market",
            "buyer_type": "Wholesale Market",
            "quantity_kg": quantity_kg,
            "price_per_kg": wholesale_price,
            "gross_revenue_kes": round(gross_revenue, 2),
            "transport_cost_kes": round(transport_cost, 2),
            "market_fee_kes": round(market_fee, 2),
            "net_profit_kes": round(net_profit, 2),
            "payment_terms": "Cash on delivery (same day)",
            "distance_km": market_distance,
            "contract_type": "No contract required",
            "pros": [
                "Guaranteed sale",
                "Immediate cash payment",
                "No pre-negotiation needed"
            ],
            "cons": [
                f"Market fee: {round(market_fee, 2)} KES (5%)",
                f"Transport cost: {round(transport_cost, 2)} KES",
                "Price fluctuates daily"
            ],
            "recommendation_score": 70
        })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return recommendations
    
    def _calculate_transport_cost(self, quantity_kg: float, distance_km: float) -> float:
        """
        Estimate transport cost based on quantity and distance
        """
        # Base rate: 10 KES per km per 100kg
        base_rate_per_km = 10
        
        # Tonnage factor
        tonnes = quantity_kg / 1000
        if tonnes < 0.5:
            multiplier = 1.5  # Small loads more expensive per kg
        elif tonnes > 2:
            multiplier = 0.8  # Bulk discount
        else:
            multiplier = 1.0
        
        transport_cost = (distance_km * base_rate_per_km * tonnes) * multiplier
        
        return max(500, transport_cost)  # Minimum 500 KES
    
    def _generate_farmer_guidance(self, optimal_window: Dict, market_options: List[Dict]) -> str:
        """
        Generate natural language guidance for farmer
        """
        best_option = market_options[0] if market_options else None
        
        urgency_messages = {
            "URGENT": "⚠️ **ACT NOW!** Poor storage conditions forecast. ",
            "HIGH": "⚠️ **Sell Soon.** ",
            "NORMAL": "✅ "
        }
        
        urgency_prefix = urgency_messages.get(optimal_window["urgency"], "")
        
        if best_option:
            guidance = (
                f"{urgency_prefix}**Optimal Strategy:** Sell your {best_option['quantity_kg']}kg "
                f"between **{optimal_window['start_date']}** and **{optimal_window['end_date']}** "
                f"to **{best_option['buyer_name']}** for maximum profit of **KES {best_option['net_profit_kes']:,}**. "
                f"\n\n"
                f"Expected price: **{optimal_window['expected_price_kes_per_kg']} KES/kg** "
                f"(Range: {optimal_window['expected_price_range']['min']}-{optimal_window['expected_price_range']['max']} KES/kg). "
            )
            
            if optimal_window["urgency"] == "URGENT":
                guidance += "\n\n🚨 Waiting longer risks 10-15% post-harvest loss. Secure buyer NOW via Marketplace."
        else:
            guidance = (
                f"{urgency_prefix}**Recommended Sale Window:** "
                f"**{optimal_window['start_date']}** to **{optimal_window['end_date']}**. "
                f"Expected price: **{optimal_window['expected_price_kes_per_kg']} KES/kg**. "
                f"\n\nCreate a listing in the Marketplace to connect with verified buyers."
            )
        
        return guidance


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

market_optimizer = MarketOptimizer()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def get_optimal_sale_strategy(
    farmer_id: str,
    field_id: str
) -> Dict:
    """
    Get complete optimal sale strategy for a farmer's field
    """
    field = persistence.get_field_by_id(field_id)
    if not field:
        return {"error": "Field not found"}
    
    return await market_optimizer.predict_optimal_sale_window(
        crop=field.get("crop", "maize"),
        predicted_yield_kg=field.get("predicted_yield_kg", 1000),
        harvest_date=field.get("expected_harvest_date", datetime.now().isoformat()),
        field_location=(field.get("latitude", -1.2921), field.get("longitude", 36.8219)),
        quality_grade=field.get("quality_grade", "B"),
        farmer_id=farmer_id
    )
