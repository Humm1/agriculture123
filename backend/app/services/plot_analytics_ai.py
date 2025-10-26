"""
AI-Powered Plot Analytics Service
Multi-image analysis, disease detection, weather predictions, fertilizer recommendations
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from PIL import Image
import io
import base64

# For future ML model integration
try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logging.warning("TensorFlow not installed - using mock predictions")

logger = logging.getLogger(__name__)


class PlotAnalyticsAI:
    """
    AI service for crop health analysis, disease detection, and predictions
    """
    
    def __init__(self):
        self.models = {}
        self._load_models()
        
    def _load_models(self):
        """Load pre-trained AI models"""
        # TODO: Load actual trained models
        # For now, we'll use rule-based and statistical methods
        self.models = {
            'disease_detector': None,  # Will load disease detection model
            'health_scorer': None,     # Will load health scoring model
            'weather_predictor': None  # Will load weather impact model
        }
        logger.info("AI models initialized (using mock predictions until models are trained)")
    
    
    async def analyze_image(
        self, 
        image_data: bytes, 
        metadata: Dict
    ) -> Dict:
        """
        Analyze a single crop image for health, disease, and stress indicators
        
        Args:
            image_data: Raw image bytes
            metadata: Dict with gps_location, weather_conditions, growth_stage
            
        Returns:
            Dict with analysis results
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Extract features
            features = self._extract_image_features(image)
            
            # Detect diseases
            disease_results = self._detect_diseases(features, metadata)
            
            # Calculate health scores
            health_scores = self._calculate_health_scores(features, metadata)
            
            # Detect stress indicators
            stress_indicators = self._detect_stress_indicators(features, metadata)
            
            return {
                'analyzed': True,
                'confidence_score': disease_results['confidence'],
                'diseases': disease_results['diseases'],
                'health_scores': health_scores,
                'stress_indicators': stress_indicators,
                'recommendations': self._generate_recommendations(disease_results, health_scores),
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                'analyzed': False,
                'error': str(e)
            }
    
    
    async def analyze_batch(
        self, 
        images: List[Tuple[bytes, Dict]]
    ) -> List[Dict]:
        """
        Analyze multiple images in batch for better performance
        
        Args:
            images: List of (image_data, metadata) tuples
            
        Returns:
            List of analysis results
        """
        results = []
        for image_data, metadata in images:
            result = await self.analyze_image(image_data, metadata)
            results.append(result)
        return results
    
    
    def _extract_image_features(self, image: Image.Image) -> Dict:
        """Extract features from crop image"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Calculate basic color statistics (proxy for health)
        if len(img_array.shape) == 3:
            r_mean = np.mean(img_array[:,:,0])
            g_mean = np.mean(img_array[:,:,1])
            b_mean = np.mean(img_array[:,:,2])
            
            # Green index (healthy plants have more green)
            green_index = g_mean / (r_mean + g_mean + b_mean + 1e-6)
            
            # Yellow/brown index (disease/stress indicator)
            yellow_index = (r_mean + g_mean) / (2 * b_mean + 1e-6)
        else:
            green_index = 0.33
            yellow_index = 0.5
        
        return {
            'green_index': float(green_index),
            'yellow_index': float(yellow_index),
            'image_size': image.size,
            'brightness': float(np.mean(img_array))
        }
    
    
    def _detect_diseases(self, features: Dict, metadata: Dict) -> Dict:
        """
        Detect potential diseases based on image features and metadata
        
        In production: Use trained CNN model
        For now: Rule-based detection
        """
        diseases = []
        confidence = 0.5
        
        # Leaf yellowing indicator
        if features['yellow_index'] > 0.7:
            diseases.append({
                'name': 'Possible Nutrient Deficiency',
                'severity': 'medium',
                'confidence': 0.65,
                'symptoms': ['Leaf yellowing', 'Chlorosis'],
                'likely_cause': 'Nitrogen or Iron deficiency'
            })
        
        # Low green index (unhealthy)
        if features['green_index'] < 0.25:
            diseases.append({
                'name': 'Leaf Blight or Wilt',
                'severity': 'high',
                'confidence': 0.58,
                'symptoms': ['Brown spots', 'Wilting'],
                'likely_cause': 'Fungal infection or water stress'
            })
        
        # Weather-related disease risk
        weather = metadata.get('weather_conditions', {})
        if weather.get('humidity', 0) > 80 and weather.get('temp', 0) > 25:
            diseases.append({
                'name': 'Fungal Disease Risk',
                'severity': 'low',
                'confidence': 0.52,
                'symptoms': ['High humidity conditions'],
                'likely_cause': 'Favorable environment for fungal growth'
            })
        
        if diseases:
            confidence = sum(d['confidence'] for d in diseases) / len(diseases)
        
        return {
            'diseases': diseases,
            'confidence': confidence,
            'disease_detected': len(diseases) > 0
        }
    
    
    def _calculate_health_scores(self, features: Dict, metadata: Dict) -> Dict:
        """Calculate crop health scores (0-100)"""
        
        # Overall health based on green index
        base_health = features['green_index'] * 100
        
        # Adjust for yellow index (disease indicator)
        yellow_penalty = (features['yellow_index'] - 0.5) * 20
        overall_health = max(0, min(100, base_health - yellow_penalty))
        
        # Component scores
        leaf_health = overall_health * 1.05  # Leaves tend to be primary indicator
        stem_health = overall_health * 0.95
        
        # Weather stress adjustment
        weather = metadata.get('weather_conditions', {})
        weather_stress = self._calculate_weather_stress(weather)
        
        return {
            'overall_health_score': float(min(100, max(0, overall_health))),
            'leaf_health_score': float(min(100, max(0, leaf_health))),
            'stem_health_score': float(min(100, max(0, stem_health))),
            'vigor_index': float(features['green_index']),
            'weather_stress_score': float(weather_stress),
            'vs_optimal_percentage': float((overall_health / 100) * 100)
        }
    
    
    def _calculate_weather_stress(self, weather: Dict) -> float:
        """Calculate weather-induced stress (0-1)"""
        stress = 0.0
        
        # Temperature stress
        temp = weather.get('temp', 25)
        if temp < 10 or temp > 35:
            stress += 0.3
        
        # Humidity stress
        humidity = weather.get('humidity', 60)
        if humidity < 30 or humidity > 85:
            stress += 0.2
        
        # Rainfall stress
        rainfall = weather.get('rainfall', 0)
        if rainfall > 50:  # Heavy rain
            stress += 0.2
        elif rainfall < 5:  # Drought
            stress += 0.3
        
        return min(1.0, stress)
    
    
    def _detect_stress_indicators(self, features: Dict, metadata: Dict) -> Dict:
        """Detect various stress indicators"""
        indicators = {}
        
        # Water stress
        if features['yellow_index'] > 0.6:
            indicators['water_stress'] = 0.4
        else:
            indicators['water_stress'] = 0.1
        
        # Nutrient deficiency
        if features['green_index'] < 0.3:
            indicators['nutrient_deficiency'] = 0.6
        else:
            indicators['nutrient_deficiency'] = 0.1
        
        # Heat stress
        temp = metadata.get('weather_conditions', {}).get('temp', 25)
        if temp > 32:
            indicators['heat_stress'] = min(1.0, (temp - 32) / 10)
        else:
            indicators['heat_stress'] = 0.0
        
        return indicators
    
    
    def _generate_recommendations(self, disease_results: Dict, health_scores: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Disease-based recommendations
        if disease_results['disease_detected']:
            for disease in disease_results['diseases']:
                if 'Nutrient' in disease['name']:
                    recommendations.append("Apply nitrogen-rich fertilizer or compost")
                elif 'Fungal' in disease['name']:
                    recommendations.append("Apply organic fungicide or neem oil")
                elif 'Wilt' in disease['name']:
                    recommendations.append("Check irrigation and improve drainage")
        
        # Health-based recommendations
        if health_scores['overall_health_score'] < 60:
            recommendations.append("Consider soil testing for nutrient deficiencies")
            recommendations.append("Increase monitoring frequency to twice weekly")
        
        # Weather-based recommendations
        if health_scores['weather_stress_score'] > 0.5:
            recommendations.append("Provide shade during peak heat hours")
            recommendations.append("Adjust irrigation schedule based on weather")
        
        return recommendations
    
    
    async def predict_disease_progression(
        self, 
        current_disease: Dict,
        weather_forecast: List[Dict],
        crop_type: str
    ) -> Dict:
        """
        Predict how disease will progress based on weather and crop type
        
        Returns:
            Dict with progression forecast
        """
        # Simple progression model
        base_spread_rate = 0.10  # 10% per day
        
        # Adjust based on weather
        avg_humidity = np.mean([w.get('humidity', 60) for w in weather_forecast])
        avg_temp = np.mean([w.get('temp', 25) for w in weather_forecast])
        
        # High humidity increases fungal spread
        if avg_humidity > 75:
            spread_rate = base_spread_rate * 1.5
        else:
            spread_rate = base_spread_rate * 0.8
        
        # Calculate days to critical spread
        current_severity = {'low': 0.2, 'medium': 0.5, 'high': 0.8}.get(
            current_disease.get('severity', 'medium'), 0.5
        )
        
        days_to_critical = int((0.9 - current_severity) / spread_rate)
        
        return {
            'spread_rate': spread_rate,
            'days_to_critical': max(1, days_to_critical),
            'projected_severity': min(1.0, current_severity + (spread_rate * 7)),
            'weather_favorability': 'high' if avg_humidity > 75 else 'moderate',
            'intervention_urgency': 'high' if days_to_critical < 7 else 'medium'
        }
    
    
    async def recommend_fertilizers(
        self, 
        soil_data: Dict,
        crop_type: str,
        area_size: float,
        budget: Optional[float] = None
    ) -> Dict:
        """
        Recommend cost-effective fertilizer options (organic vs inorganic)
        
        Args:
            soil_data: Soil nutrient levels
            crop_type: Type of crop
            area_size: Plot size in hectares
            budget: Optional budget constraint
            
        Returns:
            Dict with fertilizer recommendations
        """
        
        # Calculate nutrient needs (simplified)
        base_n = 120  # kg/hectare for most crops
        base_p = 60
        base_k = 80
        
        # Adjust based on soil test
        n_needed = max(0, base_n - soil_data.get('nitrogen', 0)) * area_size
        p_needed = max(0, base_p - soil_data.get('phosphorus', 0)) * area_size
        k_needed = max(0, base_k - soil_data.get('potassium', 0)) * area_size
        
        # Organic options (East African context)
        organic_options = [
            {
                'name': 'Composted Cow Manure',
                'type': 'organic',
                'npk_ratio': '2-1-1',
                'quantity_kg': n_needed * 50,  # Lower NPK requires more volume
                'cost_per_kg': 0.50,  # KES per kg
                'availability': 'High - Local farms',
                'application_method': 'Broadcast and incorporate before planting',
                'effectiveness_score': 0.75,
                'long_term_benefits': ['Improves soil structure', 'Increases water retention']
            },
            {
                'name': 'Chicken Manure',
                'type': 'organic',
                'npk_ratio': '4-2-1',
                'quantity_kg': n_needed * 25,
                'cost_per_kg': 1.00,
                'availability': 'Medium - Poultry farms',
                'application_method': 'Well-composted, applied 2 weeks before planting',
                'effectiveness_score': 0.85,
                'long_term_benefits': ['High nitrogen', 'Quick release']
            },
            {
                'name': 'Vermicompost',
                'type': 'organic',
                'npk_ratio': '2-1-1',
                'quantity_kg': n_needed * 40,
                'cost_per_kg': 2.00,
                'availability': 'Low - Specialized suppliers',
                'application_method': 'Top dressing during growth',
                'effectiveness_score': 0.90,
                'long_term_benefits': ['Highest quality', 'Disease suppression']
            }
        ]
        
        # Inorganic options
        inorganic_options = [
            {
                'name': 'DAP (Diammonium Phosphate)',
                'type': 'inorganic',
                'npk_ratio': '18-46-0',
                'quantity_kg': (n_needed / 0.18 + p_needed / 0.46) / 2,
                'cost_per_kg': 3.50,
                'availability': 'High - Agro-dealers',
                'application_method': 'Basal application at planting',
                'effectiveness_score': 0.95,
                'fast_acting': True
            },
            {
                'name': 'CAN (Calcium Ammonium Nitrate)',
                'type': 'inorganic',
                'npk_ratio': '27-0-0',
                'quantity_kg': n_needed / 0.27,
                'cost_per_kg': 2.80,
                'availability': 'High - Agro-dealers',
                'application_method': 'Top dressing 4-6 weeks after planting',
                'effectiveness_score': 0.95,
                'fast_acting': True
            },
            {
                'name': 'NPK 17-17-17',
                'type': 'inorganic',
                'npk_ratio': '17-17-17',
                'quantity_kg': max(n_needed, p_needed, k_needed) / 0.17,
                'cost_per_kg': 3.20,
                'availability': 'High - Agro-dealers',
                'application_method': 'Split application at planting and top dressing',
                'effectiveness_score': 0.92,
                'balanced': True
            }
        ]
        
        # Calculate total costs
        organic_total = sum(opt['quantity_kg'] * opt['cost_per_kg'] for opt in organic_options[:2])  # Use top 2
        inorganic_total = sum(opt['quantity_kg'] * opt['cost_per_kg'] for opt in inorganic_options[:2])
        
        # Determine recommendation
        cost_difference = organic_total - inorganic_total
        
        if budget and budget < min(organic_total, inorganic_total):
            recommended = 'hybrid'
            reasoning = f"Budget constraint (KES {budget:.2f}). Use inorganic for quick boost, organic for soil health."
        elif abs(cost_difference) < (organic_total * 0.2):  # Within 20%
            recommended = 'organic'
            reasoning = "Costs similar, organic provides long-term soil benefits and sustainability."
        elif organic_total < inorganic_total:
            recommended = 'organic'
            reasoning = f"Organic is cheaper (saves KES {abs(cost_difference):.2f}) and improves soil health."
        else:
            recommended = 'inorganic'
            reasoning = f"Inorganic is cheaper (saves KES {abs(cost_difference):.2f}) and faster-acting for immediate needs."
        
        return {
            'nitrogen_needed': n_needed,
            'phosphorus_needed': p_needed,
            'potassium_needed': k_needed,
            'organic_options': organic_options,
            'organic_total_cost': organic_total,
            'organic_effectiveness_score': np.mean([o['effectiveness_score'] for o in organic_options]),
            'inorganic_options': inorganic_options,
            'inorganic_total_cost': inorganic_total,
            'inorganic_effectiveness_score': np.mean([o['effectiveness_score'] for o in inorganic_options]),
            'cost_difference': cost_difference,
            'recommended_method': recommended,
            'reasoning': reasoning,
            'application_schedule': self._create_application_schedule(recommended, crop_type),
            'local_suppliers': self._get_local_suppliers(),
            'expected_results': {
                'yield_increase': '15-25%' if recommended == 'organic' else '20-30%',
                'health_improvement': '20-30%',
                'time_to_effect': '2-3 weeks' if recommended == 'inorganic' else '3-5 weeks'
            }
        }
    
    
    def _create_application_schedule(self, method: str, crop_type: str) -> List[Dict]:
        """Create fertilizer application schedule"""
        base_date = datetime.now()
        
        if method == 'organic':
            return [
                {
                    'date': base_date.isoformat(),
                    'type': 'Composted manure',
                    'amount': 'Full dose',
                    'method': 'Incorporate into soil before planting'
                },
                {
                    'date': (base_date + timedelta(days=30)).isoformat(),
                    'type': 'Top dressing',
                    'amount': '25% of initial',
                    'method': 'Apply around plants'
                }
            ]
        else:  # inorganic
            return [
                {
                    'date': base_date.isoformat(),
                    'type': 'DAP',
                    'amount': 'Full dose',
                    'method': 'Basal application at planting'
                },
                {
                    'date': (base_date + timedelta(days=21)).isoformat(),
                    'type': 'CAN',
                    'amount': '50% of nitrogen',
                    'method': 'Top dressing'
                },
                {
                    'date': (base_date + timedelta(days=42)).isoformat(),
                    'type': 'CAN',
                    'amount': 'Remaining nitrogen',
                    'method': 'Top dressing'
                }
            ]
    
    
    def _get_local_suppliers(self) -> List[Dict]:
        """Get local fertilizer suppliers (placeholder)"""
        return [
            {
                'name': 'Local Agro-Dealer Network',
                'type': 'Both organic and inorganic',
                'contact': 'Check nearest agro-vet',
                'note': 'Prices vary by region'
            },
            {
                'name': 'Farmer Cooperatives',
                'type': 'Bulk organic materials',
                'contact': 'Local cooperative office',
                'note': 'Often cheaper for large quantities'
            }
        ]
    
    
    async def analyze_weather_impact(
        self, 
        current_weather: Dict,
        forecast: List[Dict],
        crop_type: str,
        growth_stage: str
    ) -> Dict:
        """
        Analyze weather impact on crop health and predict risks
        
        Returns:
            Dict with weather analysis and recommendations
        """
        
        # Identify stress factors
        stress_factors = {}
        if current_weather.get('temp', 0) > 32:
            stress_factors['heat_stress'] = True
        if current_weather.get('rainfall', 0) < 5:
            stress_factors['drought'] = True
        if current_weather.get('humidity', 0) > 80:
            stress_factors['high_humidity'] = True
        
        # Analyze forecast for risk periods
        risk_periods = []
        for i, day in enumerate(forecast[:7]):
            risks = []
            if day.get('temp', 0) > 35:
                risks.append('Extreme heat')
            if day.get('rainfall', 0) > 50:
                risks.append('Heavy rainfall - disease risk')
            if day.get('humidity', 0) > 85 and day.get('temp', 0) > 25:
                risks.append('Fungal disease favorable')
            
            if risks:
                risk_periods.append({
                    'day': i + 1,
                    'date': (datetime.now() + timedelta(days=i+1)).isoformat(),
                    'risks': risks,
                    'severity': 'high' if len(risks) > 1 else 'medium'
                })
        
        # Disease risk from weather
        avg_humidity = np.mean([d.get('humidity', 60) for d in forecast])
        avg_temp = np.mean([d.get('temp', 25) for d in forecast])
        
        disease_risk = 0.0
        favorable_diseases = []
        
        if avg_humidity > 75 and 20 < avg_temp < 30:
            disease_risk += 0.6
            favorable_diseases.extend(['Leaf blight', 'Downy mildew', 'Fungal infections'])
        
        if avg_temp > 30:
            disease_risk += 0.3
            favorable_diseases.extend(['Bacterial wilt', 'Viral diseases'])
        
        # Recommendations
        weather_adjustments = {}
        protective_measures = []
        
        if stress_factors.get('heat_stress'):
            weather_adjustments['irrigation'] = 'increase'
            weather_adjustments['mulching'] = 'apply'
            protective_measures.append('Provide shade netting during peak heat hours (12-3 PM)')
        
        if stress_factors.get('high_humidity'):
            weather_adjustments['spacing'] = 'increase airflow'
            protective_measures.append('Apply preventive fungicide before forecast rain')
        
        if stress_factors.get('drought'):
            weather_adjustments['irrigation'] = 'critical'
            protective_measures.append('Implement drip irrigation or mulching to conserve moisture')
        
        return {
            'current_conditions': current_weather,
            'stress_factors': stress_factors,
            'optimal_variance': {
                'temp_variance': abs(current_weather.get('temp', 25) - 25),
                'humidity_variance': abs(current_weather.get('humidity', 60) - 60)
            },
            'forecast_data': forecast[:7],
            'risk_periods': risk_periods,
            'disease_risk_score': min(1.0, disease_risk),
            'favorable_diseases': list(set(favorable_diseases)),
            'weather_adjustments': weather_adjustments,
            'protective_measures': protective_measures,
            'overall_risk_level': 'high' if disease_risk > 0.6 else ('medium' if disease_risk > 0.3 else 'low')
        }


# Singleton instance
plot_analytics_ai = PlotAnalyticsAI()
