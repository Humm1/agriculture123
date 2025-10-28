"""
Public API Data Collection for ML Model Training
==================================================

Fetches real agricultural datasets from public APIs and open-source databases:
1. PlantVillage Dataset (54,000+ plant disease images)
2. iNaturalist API (pest identification and observations)
3. OpenWeatherMap API (climate data)
4. FAO SoilGrids API (soil data - no key required)
5. GBIF API (Global Biodiversity Information Facility)
6. Kaggle Datasets (via direct downloads)

Usage:
    python collect_public_api_data.py --all
    python collect_public_api_data.py --pests --diseases
    python collect_public_api_data.py --climate --soil
"""

import os
import sys
import json
import requests
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from io import BytesIO
from PIL import Image
import zipfile
import argparse

# Configuration
BASE_DIR = Path(__file__).parent / "training_data_public"
BASE_DIR.mkdir(exist_ok=True)

# API Keys (from environment or free tier)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
INATURALIST_BASE = "https://api.inaturalist.org/v1"
FAO_SOILGRIDS_BASE = "https://rest.isric.org/soilgrids/v2.0"
GBIF_BASE = "https://api.gbif.org/v1"
PLANTVILLAGE_GITHUB = "https://github.com/spMohanty/PlantVillage-Dataset"

print("=" * 80)
print("🌍 AgroShield Public API Data Collection System")
print("=" * 80)


# ============================================================================
# 1. PLANTVILLAGE DATASET (Disease Detection)
# ============================================================================

class PlantVillageCollector:
    """Fetch PlantVillage dataset - 54,000+ labeled plant disease images"""
    
    def __init__(self):
        self.output_dir = BASE_DIR / "plantvillage_diseases"
        self.output_dir.mkdir(exist_ok=True)
        
    def download_dataset(self):
        """
        Download PlantVillage dataset from Kaggle or GitHub
        
        Dataset: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
        Contains 38 classes of plant diseases across 14 crop species
        """
        print("\n🌿 PlantVillage Disease Dataset Collection")
        print("-" * 60)
        
        # Method 1: Direct download from Kaggle API (requires kaggle API token)
        kaggle_dataset = "abdallahalidev/plantvillage-dataset"
        
        try:
            print("📥 Attempting Kaggle download...")
            print(f"   Dataset: {kaggle_dataset}")
            print("   ⚠️  Requires: kaggle.json in ~/.kaggle/ with API credentials")
            print("   Get your API key from: https://www.kaggle.com/settings")
            
            # Check if kaggle CLI is available
            import subprocess
            result = subprocess.run(
                ["kaggle", "datasets", "download", "-d", kaggle_dataset, "-p", str(self.output_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ PlantVillage dataset downloaded!")
                
                # Extract zip if present
                zip_files = list(self.output_dir.glob("*.zip"))
                if zip_files:
                    print(f"📦 Extracting {zip_files[0].name}...")
                    with zipfile.ZipFile(zip_files[0], 'r') as zip_ref:
                        zip_ref.extractall(self.output_dir)
                    print("✅ Extraction complete!")
                    
                return True
            else:
                print(f"⚠️  Kaggle download failed: {result.stderr}")
                
        except FileNotFoundError:
            print("⚠️  Kaggle CLI not installed. Install with: pip install kaggle")
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        # Method 2: Instructions for manual download
        print("\n📋 Manual Download Instructions:")
        print("   1. Visit: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset")
        print("   2. Click 'Download' (requires free Kaggle account)")
        print(f"   3. Extract to: {self.output_dir}")
        print("   4. Re-run this script")
        
        return False
    
    def get_metadata(self) -> Dict:
        """Get dataset statistics"""
        if not self.output_dir.exists():
            return {"status": "not_downloaded", "images": 0}
        
        # Count images
        image_count = sum(1 for _ in self.output_dir.rglob("*.jpg")) + \
                     sum(1 for _ in self.output_dir.rglob("*.JPG"))
        
        # Count classes (subdirectories)
        classes = [d.name for d in self.output_dir.iterdir() if d.is_dir()]
        
        return {
            "status": "ready",
            "images": image_count,
            "classes": len(classes),
            "class_names": classes[:10] if len(classes) > 10 else classes
        }


# ============================================================================
# 2. iNATURALIST API (Pest Identification)
# ============================================================================

class iNaturalistCollector:
    """Fetch pest and insect observations from iNaturalist"""
    
    def __init__(self):
        self.base_url = INATURALIST_BASE
        self.output_dir = BASE_DIR / "inaturalist_pests"
        self.output_dir.mkdir(exist_ok=True)
        
    async def fetch_pest_observations(
        self, 
        taxon_name: str = "Insecta",
        location: str = "Kenya",
        per_page: int = 200,
        quality_grade: str = "research"
    ) -> List[Dict]:
        """
        Fetch pest observations from iNaturalist
        
        Args:
            taxon_name: Scientific name (e.g., "Aphididae", "Insecta")
            location: Location filter
            per_page: Results per page (max 200)
            quality_grade: "research", "needs_id", or "casual"
        
        Returns:
            List of observations with images
        """
        print(f"\n🐛 Fetching {taxon_name} observations from iNaturalist...")
        
        observations = []
        
        async with aiohttp.ClientSession() as session:
            # Search for observations
            params = {
                "taxon_name": taxon_name,
                "place": location,
                "per_page": per_page,
                "quality_grade": quality_grade,
                "has[]": "photos",  # Only observations with photos
                "iconic_taxa": "Insecta"
            }
            
            try:
                async with session.get(
                    f"{self.base_url}/observations",
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        
                        print(f"   Found {len(results)} observations")
                        
                        for obs in results:
                            # Extract relevant data
                            observation = {
                                "id": obs.get("id"),
                                "taxon": obs.get("taxon", {}).get("name"),
                                "common_name": obs.get("taxon", {}).get("preferred_common_name"),
                                "observed_on": obs.get("observed_on"),
                                "location": obs.get("place_guess"),
                                "quality_grade": obs.get("quality_grade"),
                                "images": []
                            }
                            
                            # Extract photo URLs
                            for photo in obs.get("photos", []):
                                observation["images"].append({
                                    "url": photo.get("url").replace("square", "medium"),
                                    "attribution": photo.get("attribution")
                                })
                            
                            observations.append(observation)
                        
                        print(f"✅ Processed {len(observations)} observations with images")
                    else:
                        print(f"⚠️  API error: {response.status}")
                        
            except Exception as e:
                print(f"⚠️  Error fetching observations: {e}")
        
        return observations
    
    async def download_images(self, observations: List[Dict], max_images: int = 500):
        """Download images from observations"""
        print(f"\n📥 Downloading up to {max_images} pest images...")
        
        downloaded = 0
        
        async with aiohttp.ClientSession() as session:
            for obs in observations:
                if downloaded >= max_images:
                    break
                
                taxon = obs.get("taxon", "unknown").replace(" ", "_")
                taxon_dir = self.output_dir / taxon
                taxon_dir.mkdir(exist_ok=True)
                
                for img_info in obs.get("images", []):
                    if downloaded >= max_images:
                        break
                    
                    try:
                        async with session.get(img_info["url"], timeout=30) as response:
                            if response.status == 200:
                                img_data = await response.read()
                                
                                # Save image
                                filename = f"{obs['id']}_{downloaded:04d}.jpg"
                                filepath = taxon_dir / filename
                                
                                with open(filepath, 'wb') as f:
                                    f.write(img_data)
                                
                                downloaded += 1
                                
                                if downloaded % 50 == 0:
                                    print(f"   Downloaded {downloaded}/{max_images} images...")
                                    
                    except Exception as e:
                        print(f"   ⚠️  Error downloading image: {e}")
                        continue
        
        print(f"✅ Downloaded {downloaded} pest images")
        return downloaded


# ============================================================================
# 3. OPENWEATHERMAP API (Climate Data)
# ============================================================================

class OpenWeatherCollector:
    """Fetch historical and forecast climate data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.output_dir = BASE_DIR / "climate_data"
        self.output_dir.mkdir(exist_ok=True)
        
    def fetch_current_weather(self, locations: List[Dict]) -> pd.DataFrame:
        """
        Fetch current weather for multiple locations
        
        Args:
            locations: List of {"name": "City", "lat": X, "lon": Y}
        """
        print("\n🌦️  Fetching current weather data...")
        
        weather_data = []
        
        for loc in locations:
            try:
                url = f"{self.base_url}/weather"
                params = {
                    "lat": loc["lat"],
                    "lon": loc["lon"],
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    weather_data.append({
                        "location": loc["name"],
                        "timestamp": datetime.now().isoformat(),
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "wind_speed": data["wind"]["speed"],
                        "clouds": data["clouds"]["all"],
                        "weather": data["weather"][0]["main"],
                        "description": data["weather"][0]["description"]
                    })
                    
                    print(f"   ✓ {loc['name']}: {data['main']['temp']}°C")
                    
            except Exception as e:
                print(f"   ⚠️  Error for {loc['name']}: {e}")
        
        df = pd.DataFrame(weather_data)
        
        # Save to CSV
        output_file = self.output_dir / f"weather_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Saved {len(df)} weather records to {output_file.name}")
        
        return df


# ============================================================================
# 4. FAO SOILGRIDS API (Soil Data - No API Key Required!)
# ============================================================================

class SoilGridsCollector:
    """Fetch soil property data from FAO SoilGrids (public, no key needed)"""
    
    def __init__(self):
        self.base_url = FAO_SOILGRIDS_BASE
        self.output_dir = BASE_DIR / "soil_data"
        self.output_dir.mkdir(exist_ok=True)
        
    def fetch_soil_properties(self, locations: List[Dict]) -> pd.DataFrame:
        """
        Fetch soil properties for given coordinates
        
        Args:
            locations: List of {"name": "Location", "lat": X, "lon": Y}
        
        Returns:
            DataFrame with soil NPK, pH, organic carbon, etc.
        """
        print("\n🌱 Fetching soil data from FAO SoilGrids (public API)...")
        
        soil_data = []
        
        # Soil properties to fetch
        properties = [
            "nitrogen",      # Total nitrogen
            "phh2o",         # pH in water
            "soc",           # Soil organic carbon
            "clay",          # Clay content
            "sand",          # Sand content
            "silt",          # Silt content
            "bdod"           # Bulk density
        ]
        
        for loc in locations:
            try:
                url = f"{self.base_url}/properties/query"
                params = {
                    "lon": loc["lon"],
                    "lat": loc["lat"],
                    "property": properties,
                    "depth": "0-5cm",  # Top soil layer
                    "value": "mean"
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    record = {
                        "location": loc["name"],
                        "latitude": loc["lat"],
                        "longitude": loc["lon"],
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Extract soil properties
                    for prop in data.get("properties", {}).get("layers", []):
                        prop_name = prop.get("name")
                        values = prop.get("depths", [{}])[0].get("values", {})
                        record[prop_name] = values.get("mean")
                    
                    soil_data.append(record)
                    print(f"   ✓ {loc['name']}: pH={record.get('phh2o', 'N/A')}")
                    
                else:
                    print(f"   ⚠️  Error for {loc['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️  Error for {loc['name']}: {e}")
        
        df = pd.DataFrame(soil_data)
        
        # Save to CSV
        output_file = self.output_dir / f"soil_properties_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Saved {len(df)} soil records to {output_file.name}")
        
        return df


# ============================================================================
# 5. GBIF API (Global Biodiversity - Pest Species Data)
# ============================================================================

class GBIFCollector:
    """Fetch biodiversity data from Global Biodiversity Information Facility"""
    
    def __init__(self):
        self.base_url = GBIF_BASE
        self.output_dir = BASE_DIR / "gbif_species"
        self.output_dir.mkdir(exist_ok=True)
        
    async def search_species(self, query: str, limit: int = 100) -> List[Dict]:
        """
        Search for species occurrences
        
        Args:
            query: Species name or family (e.g., "Aphididae")
            limit: Maximum results
        """
        print(f"\n🔬 Searching GBIF for {query}...")
        
        occurrences = []
        
        async with aiohttp.ClientSession() as session:
            params = {
                "q": query,
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "limit": limit
            }
            
            try:
                async with session.get(
                    f"{self.base_url}/occurrence/search",
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        
                        for result in results:
                            occurrences.append({
                                "species": result.get("species"),
                                "scientific_name": result.get("scientificName"),
                                "country": result.get("country"),
                                "latitude": result.get("decimalLatitude"),
                                "longitude": result.get("decimalLongitude"),
                                "year": result.get("year"),
                                "month": result.get("month")
                            })
                        
                        print(f"✅ Found {len(occurrences)} occurrences")
                    else:
                        print(f"⚠️  API error: {response.status}")
                        
            except Exception as e:
                print(f"⚠️  Error: {e}")
        
        return occurrences


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def collect_all_data():
    """Collect data from all public APIs"""
    
    print("\n" + "=" * 80)
    print("Starting comprehensive data collection...")
    print("=" * 80)
    
    # Kenya agricultural regions for sampling
    kenya_locations = [
        {"name": "Nairobi", "lat": -1.286389, "lon": 36.817223},
        {"name": "Nakuru", "lat": -0.303099, "lon": 36.080025},
        {"name": "Eldoret", "lat": 0.514277, "lon": 35.269779},
        {"name": "Kisumu", "lat": -0.091702, "lon": 34.767956},
        {"name": "Mombasa", "lat": -4.043477, "lon": 39.668206},
        {"name": "Nyeri", "lat": -0.420973, "lon": 36.954699},
        {"name": "Kitale", "lat": 1.021, "lon": 35.006},
        {"name": "Embu", "lat": -0.531, "lon": 37.457}
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "collections": {}
    }
    
    # 1. PlantVillage Disease Dataset
    print("\n" + "=" * 80)
    pv = PlantVillageCollector()
    pv.download_dataset()
    results["collections"]["plantvillage"] = pv.get_metadata()
    
    # 2. iNaturalist Pest Images
    print("\n" + "=" * 80)
    inat = iNaturalistCollector()
    
    # Fetch observations for common agricultural pests
    pest_taxa = [
        "Aphididae",      # Aphids
        "Aleyrodidae",    # Whiteflies
        "Thripidae",      # Thrips
        "Spodoptera",     # Armyworms
        "Agrotis",        # Cutworms
    ]
    
    all_observations = []
    for taxon in pest_taxa:
        obs = await inat.fetch_pest_observations(taxon_name=taxon, location="Kenya", per_page=50)
        all_observations.extend(obs)
    
    # Download images
    downloaded = await inat.download_images(all_observations, max_images=500)
    results["collections"]["inaturalist"] = {
        "observations": len(all_observations),
        "images_downloaded": downloaded
    }
    
    # 3. OpenWeatherMap Climate Data
    print("\n" + "=" * 80)
    if OPENWEATHER_API_KEY:
        weather = OpenWeatherCollector(OPENWEATHER_API_KEY)
        weather_df = weather.fetch_current_weather(kenya_locations)
        results["collections"]["openweather"] = {
            "locations": len(weather_df),
            "latest_file": f"weather_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    else:
        print("⚠️  OPENWEATHER_API_KEY not set. Skipping climate data.")
        print("   Get free API key: https://openweathermap.org/api")
        results["collections"]["openweather"] = {"status": "skipped", "reason": "no_api_key"}
    
    # 4. FAO SoilGrids Data (No API key needed!)
    print("\n" + "=" * 80)
    soil = SoilGridsCollector()
    soil_df = soil.fetch_soil_properties(kenya_locations)
    results["collections"]["soilgrids"] = {
        "locations": len(soil_df),
        "latest_file": f"soil_properties_{datetime.now().strftime('%Y%m%d')}.csv"
    }
    
    # 5. GBIF Species Occurrences
    print("\n" + "=" * 80)
    gbif = GBIFCollector()
    gbif_occurrences = await gbif.search_species("Aphididae", limit=200)
    
    if gbif_occurrences:
        gbif_df = pd.DataFrame(gbif_occurrences)
        gbif_file = gbif.output_dir / f"aphid_occurrences_{datetime.now().strftime('%Y%m%d')}.csv"
        gbif_df.to_csv(gbif_file, index=False)
        results["collections"]["gbif"] = {
            "occurrences": len(gbif_occurrences),
            "latest_file": gbif_file.name
        }
    
    # Save summary
    print("\n" + "=" * 80)
    print("📊 COLLECTION SUMMARY")
    print("=" * 80)
    
    summary_file = BASE_DIR / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(json.dumps(results, indent=2))
    print(f"\n✅ Summary saved to: {summary_file}")
    print(f"📁 All data saved to: {BASE_DIR}")
    
    print("\n" + "=" * 80)
    print("✅ DATA COLLECTION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review collected data in:", BASE_DIR)
    print("2. Run model training with: python train_models_example.py")
    print("3. Check data quality and distribution")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Collect agricultural data from public APIs")
    parser.add_argument("--all", action="store_true", help="Collect from all sources")
    parser.add_argument("--pests", action="store_true", help="Collect pest data (iNaturalist, GBIF)")
    parser.add_argument("--diseases", action="store_true", help="Collect disease data (PlantVillage)")
    parser.add_argument("--climate", action="store_true", help="Collect climate data (OpenWeatherMap)")
    parser.add_argument("--soil", action="store_true", help="Collect soil data (FAO SoilGrids)")
    
    args = parser.parse_args()
    
    # If no specific flags, collect all
    if not any([args.all, args.pests, args.diseases, args.climate, args.soil]):
        args.all = True
    
    print("\n🚀 Starting data collection...")
    print(f"   Output directory: {BASE_DIR}")
    
    # Run async collection
    asyncio.run(collect_all_data())


if __name__ == "__main__":
    main()
