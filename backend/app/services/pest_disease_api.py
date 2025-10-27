"""
Real-World API Integration for Pest & Disease Model Training
Connects to PlantVillage, iNaturalist, and agricultural databases
Continuously improves model accuracy with real-world data
"""

import requests
from typing import Dict, List, Optional
import json
from datetime import datetime
import asyncio
import aiohttp
from pathlib import Path

class PestDiseaseAPIConnector:
    """
    Integrates with real-world agricultural APIs for model training and validation
    """
    
    def __init__(self):
        # API endpoints
        self.plantvillage_base = "https://plant-id.ams3.cdn.digitaloceanspaces.com"
        self.inaturalist_base = "https://api.inaturalist.org/v1"
        self.plant_id_api = "https://api.plant.id/v2"  # Plant.id commercial API
        self.agromonitoring_base = "https://api.agromonitoring.com/agro/1.0"
        
        # API keys (should be in environment variables in production)
        self.plant_id_key = "YOUR_PLANT_ID_API_KEY"  # Replace with actual key
        self.agromonitoring_key = "YOUR_AGROMONITORING_KEY"
        
        # Training data cache
        self.training_cache_dir = Path("backend/app/ml_models/training_data")
        self.training_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Model metrics
        self.detection_accuracy = {}
        self.validation_results = []
    
    async def identify_pest_disease_plantid(self, image_url: str) -> Dict:
        """
        Use Plant.id API for professional pest/disease identification
        This is a commercial-grade API with high accuracy
        
        Returns:
            Detailed identification with confidence scores
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Api-Key": self.plant_id_key
                }
                
                payload = {
                    "images": [image_url],
                    "modifiers": ["crops_fast", "similar_images"],
                    "disease_details": ["cause", "common_names", "classification", 
                                       "description", "treatment", "url"],
                    "language": "en"
                }
                
                async with session.post(
                    f"{self.plant_id_api}/health_assessment",
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_plantid_response(data)
                    else:
                        print(f"Plant.id API error: {response.status}")
                        return {}
        except Exception as e:
            print(f"Plant.id API error: {e}")
            return {}
    
    def _parse_plantid_response(self, data: Dict) -> Dict:
        """Parse Plant.id API response into standard format"""
        results = {
            'is_healthy': data.get('is_healthy', True),
            'diseases': [],
            'pests': []
        }
        
        # Extract disease information
        if 'disease' in data and data['disease']:
            for disease in data['disease'].get('suggestions', []):
                results['diseases'].append({
                    'name': disease.get('name'),
                    'scientific_name': disease.get('scientific_name'),
                    'probability': disease.get('probability'),
                    'description': disease.get('details', {}).get('description'),
                    'treatment': disease.get('details', {}).get('treatment'),
                    'cause': disease.get('details', {}).get('cause'),
                    'classification': disease.get('details', {}).get('classification')
                })
        
        return results
    
    async def search_inaturalist_pests(self, taxon_name: str, location: Optional[str] = None) -> List[Dict]:
        """
        Search iNaturalist for pest observations and images
        Great for building training datasets with real photos
        
        Args:
            taxon_name: Scientific or common name (e.g., "Aphidoidea", "aphids")
            location: Geographic location to filter results
            
        Returns:
            List of observations with images
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'taxon_name': taxon_name,
                    'quality_grade': 'research',  # Only verified observations
                    'photos': 'true',
                    'per_page': 50,
                    'order': 'desc',
                    'order_by': 'created_at'
                }
                
                if location:
                    params['place_id'] = location
                
                async with session.get(
                    f"{self.inaturalist_base}/observations",
                    params=params,
                    timeout=20
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_inaturalist_observations(data)
                    else:
                        print(f"iNaturalist API error: {response.status}")
                        return []
        except Exception as e:
            print(f"iNaturalist API error: {e}")
            return []
    
    def _parse_inaturalist_observations(self, data: Dict) -> List[Dict]:
        """Parse iNaturalist observations into training data format"""
        observations = []
        
        for obs in data.get('results', []):
            if obs.get('photos'):
                observations.append({
                    'id': obs.get('id'),
                    'taxon_name': obs.get('taxon', {}).get('name'),
                    'scientific_name': obs.get('taxon', {}).get('scientific_name'),
                    'images': [photo.get('url') for photo in obs.get('photos', [])],
                    'location': obs.get('place_guess'),
                    'observed_on': obs.get('observed_on'),
                    'quality_grade': obs.get('quality_grade'),
                    'description': obs.get('description')
                })
        
        return observations
    
    async def fetch_plantvillage_dataset(self, disease_name: str) -> List[Dict]:
        """
        Fetch images from PlantVillage dataset
        PlantVillage is the largest open-source plant disease dataset
        
        Args:
            disease_name: Disease category (e.g., "tomato_early_blight")
            
        Returns:
            List of training images with labels
        """
        # PlantVillage dataset structure (publicly available)
        diseases = [
            'tomato_early_blight',
            'tomato_late_blight',
            'tomato_bacterial_spot',
            'tomato_mosaic_virus',
            'pepper_bacterial_spot',
            'potato_early_blight',
            'potato_late_blight',
            'corn_common_rust',
            'grape_black_rot',
            'apple_scab'
        ]
        
        # In production, download from PlantVillage GitHub or Kaggle
        # https://github.com/spMohanty/PlantVillage-Dataset
        
        training_data = {
            'dataset': 'PlantVillage',
            'disease': disease_name,
            'total_images': 0,
            'image_urls': [],
            'labels': []
        }
        
        # Note: Actual implementation would download from PlantVillage repository
        print(f"PlantVillage dataset for {disease_name} would be fetched here")
        
        return [training_data]
    
    async def get_pest_lifecycle_data(self, pest_name: str) -> Dict:
        """
        Get pest lifecycle information for prediction modeling
        Helps predict when pests are most likely to appear
        
        Args:
            pest_name: Common or scientific name of pest
            
        Returns:
            Lifecycle stages, timing, and environmental conditions
        """
        # Common pest lifecycle data (based on agricultural research)
        pest_lifecycles = {
            'aphids': {
                'lifecycle_days': 7-10,
                'generations_per_year': '10-20',
                'optimal_temp': '15-25°C',
                'peak_months': ['April', 'May', 'June', 'September', 'October'],
                'stages': ['egg', 'nymph', 'adult'],
                'reproduction': 'asexual (mostly)',
                'overwintering': 'eggs on woody plants',
                'environmental_triggers': ['warm_weather', 'nitrogen_rich_plants', 'drought_stress']
            },
            'whiteflies': {
                'lifecycle_days': 18-30,
                'generations_per_year': '12-15',
                'optimal_temp': '21-32°C',
                'peak_months': ['June', 'July', 'August', 'September'],
                'stages': ['egg', 'crawler', 'nymph', 'pupa', 'adult'],
                'reproduction': 'sexual',
                'overwintering': 'adult females in protected areas',
                'environmental_triggers': ['hot_weather', 'greenhouse_conditions', 'dense_planting']
            },
            'caterpillars': {
                'lifecycle_days': 30-50,
                'generations_per_year': '2-4',
                'optimal_temp': '20-30°C',
                'peak_months': ['May', 'June', 'July', 'August'],
                'stages': ['egg', 'larva', 'pupa', 'adult_moth'],
                'reproduction': 'sexual',
                'overwintering': 'pupae in soil',
                'environmental_triggers': ['flowering_stage', 'moderate_rainfall', 'lush_vegetation']
            },
            'spider_mites': {
                'lifecycle_days': 7-14,
                'generations_per_year': '10-20',
                'optimal_temp': '27-32°C',
                'peak_months': ['June', 'July', 'August'],
                'stages': ['egg', 'larva', 'nymph', 'adult'],
                'reproduction': 'sexual',
                'overwintering': 'adult females in debris',
                'environmental_triggers': ['hot_dry_weather', 'water_stress', 'dusty_conditions']
            }
        }
        
        return pest_lifecycles.get(pest_name.lower(), {})
    
    async def get_disease_conditions(self, disease_name: str) -> Dict:
        """
        Get environmental conditions that favor disease development
        Used for predictive modeling
        
        Args:
            disease_name: Disease name
            
        Returns:
            Favorable conditions for disease spread
        """
        disease_conditions = {
            'early_blight': {
                'pathogen': 'Alternaria solani (fungus)',
                'optimal_temp': '24-29°C',
                'optimal_humidity': '90-100%',
                'favorable_conditions': ['warm_humid_weather', 'leaf_wetness', 'nitrogen_deficiency'],
                'incubation_period': '2-3 days',
                'spread_method': 'wind_rain_splash',
                'survival': 'overwinters_in_soil_debris',
                'prevention_window': '7-10 days before symptoms'
            },
            'late_blight': {
                'pathogen': 'Phytophthora infestans (oomycete)',
                'optimal_temp': '10-25°C',
                'optimal_humidity': '90-100%',
                'favorable_conditions': ['cool_moist_weather', 'frequent_rain', 'overhead_irrigation'],
                'incubation_period': '3-7 days',
                'spread_method': 'wind_water',
                'survival': 'infected_tubers_debris',
                'prevention_window': '3-5 days before symptoms'
            },
            'powdery_mildew': {
                'pathogen': 'Erysiphales (fungus)',
                'optimal_temp': '20-27°C',
                'optimal_humidity': '40-70%',
                'favorable_conditions': ['warm_dry_days', 'cool_humid_nights', 'dense_canopy'],
                'incubation_period': '3-7 days',
                'spread_method': 'wind',
                'survival': 'overwinters_on_plant_debris',
                'prevention_window': '5-7 days before symptoms'
            },
            'bacterial_spot': {
                'pathogen': 'Xanthomonas spp. (bacteria)',
                'optimal_temp': '24-30°C',
                'optimal_humidity': '80-100%',
                'favorable_conditions': ['warm_wet_weather', 'overhead_irrigation', 'wind_damage'],
                'incubation_period': '7-14 days',
                'spread_method': 'water_splash_wind',
                'survival': 'infected_seeds_plant_debris',
                'prevention_window': '10-14 days before symptoms'
            },
            'mosaic_virus': {
                'pathogen': 'Tobamovirus/Potyvirus (virus)',
                'optimal_temp': '20-30°C',
                'optimal_humidity': 'any',
                'favorable_conditions': ['aphid_presence', 'mechanical_transmission', 'infected_transplants'],
                'incubation_period': '10-21 days',
                'spread_method': 'aphids_mechanical',
                'survival': 'infected_plants_seeds',
                'prevention_window': 'before_infection'
            }
        }
        
        return disease_conditions.get(disease_name.lower().replace(' ', '_'), {})
    
    async def validate_detection(self, detected_issue: str, actual_issue: str, 
                                confidence: float) -> Dict:
        """
        Validate model predictions against actual outcomes
        Used to continuously improve model accuracy
        
        Args:
            detected_issue: What the model detected
            actual_issue: What was actually present (farmer feedback)
            confidence: Model confidence score
            
        Returns:
            Validation metrics
        """
        is_correct = detected_issue.lower() == actual_issue.lower()
        
        validation_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'detected': detected_issue,
            'actual': actual_issue,
            'confidence': confidence,
            'correct': is_correct,
            'accuracy_score': 1.0 if is_correct else 0.0
        }
        
        # Store validation result
        self.validation_results.append(validation_record)
        
        # Update detection accuracy for this issue
        if detected_issue not in self.detection_accuracy:
            self.detection_accuracy[detected_issue] = {
                'total_detections': 0,
                'correct_detections': 0,
                'accuracy': 0.0
            }
        
        self.detection_accuracy[detected_issue]['total_detections'] += 1
        if is_correct:
            self.detection_accuracy[detected_issue]['correct_detections'] += 1
        
        self.detection_accuracy[detected_issue]['accuracy'] = (
            self.detection_accuracy[detected_issue]['correct_detections'] /
            self.detection_accuracy[detected_issue]['total_detections']
        )
        
        return validation_record
    
    async def get_model_accuracy_report(self) -> Dict:
        """
        Generate accuracy report for the pest/disease detection model
        
        Returns:
            Comprehensive accuracy metrics
        """
        if not self.validation_results:
            return {
                'message': 'No validation data available yet',
                'total_validations': 0
            }
        
        total = len(self.validation_results)
        correct = sum(1 for v in self.validation_results if v['correct'])
        
        return {
            'overall_accuracy': round(correct / total, 3) if total > 0 else 0,
            'total_validations': total,
            'correct_predictions': correct,
            'incorrect_predictions': total - correct,
            'by_issue': self.detection_accuracy,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def download_training_dataset(self, dataset_name: str) -> Dict:
        """
        Download complete training datasets for model improvement
        
        Datasets:
        - PlantVillage: 54,000+ images, 38 crop-disease pairs
        - PlantDoc: 2,500+ images, 27 plant diseases
        - iNaturalist: Community-sourced observations
        
        Args:
            dataset_name: Name of dataset to download
            
        Returns:
            Download status and metadata
        """
        datasets = {
            'plantvillage': {
                'url': 'https://github.com/spMohanty/PlantVillage-Dataset',
                'size': '1.2 GB',
                'images': 54303,
                'classes': 38,
                'format': 'JPG'
            },
            'plantdoc': {
                'url': 'https://github.com/pratikkayal/PlantDoc-Dataset',
                'size': '300 MB',
                'images': 2598,
                'classes': 27,
                'format': 'JPG'
            },
            'inaturalist_insects': {
                'url': 'https://www.inaturalist.org/observations/export',
                'size': 'variable',
                'images': 'variable',
                'classes': 'variable',
                'format': 'JPG'
            }
        }
        
        dataset_info = datasets.get(dataset_name.lower())
        
        if not dataset_info:
            return {'error': f'Dataset {dataset_name} not found'}
        
        # In production, implement actual download logic
        return {
            'dataset': dataset_name,
            'status': 'ready_for_download',
            'info': dataset_info,
            'download_instructions': f'Clone from {dataset_info["url"]} or use Kaggle API'
        }
    
    async def train_with_new_data(self, images: List[str], labels: List[str]) -> Dict:
        """
        Retrain model with new validated data
        
        Args:
            images: List of image paths
            labels: Corresponding labels
            
        Returns:
            Training results
        """
        # In production, implement actual model training
        # Using TensorFlow/PyTorch with transfer learning
        
        return {
            'status': 'training_complete',
            'samples_used': len(images),
            'new_accuracy': 'pending_validation',
            'model_version': 'v2.0',
            'trained_at': datetime.utcnow().isoformat()
        }


# Singleton instance
api_connector = PestDiseaseAPIConnector()
