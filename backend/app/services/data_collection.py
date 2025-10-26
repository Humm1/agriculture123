"""
Data Collection Service for AI Model Training
Fetches prediction data from Supabase to improve models
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client
import pandas as pd
import numpy as np
from pathlib import Path

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rwspbvgmmxabglptljkg.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

# Only initialize Supabase client if we have a valid key
if SUPABASE_SERVICE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
else:
    supabase = None
    print("WARNING: Supabase client not initialized - missing SUPABASE_SERVICE_ROLE_KEY")



class DataCollectionService:
    """Service to collect and prepare data for model training"""
    
    def __init__(self):
        # Use global supabase or create new client with service key
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if service_key:
            self.supabase = create_client(SUPABASE_URL, service_key)
        else:
            self.supabase = None
            print("WARNING: DataCollectionService - No Supabase key available")
        
        self.data_dir = Path("training_data")
        self.data_dir.mkdir(exist_ok=True)
    
    # ===================================
    # PEST DETECTION DATA
    # ===================================
    
    def fetch_pest_predictions(
        self, 
        days_back: int = 30,
        min_confidence: float = 0.7,
        user_confirmed_only: bool = False
    ) -> pd.DataFrame:
        """
        Fetch pest detection predictions for model improvement
        
        Args:
            days_back: Number of days to look back
            min_confidence: Minimum confidence score
            user_confirmed_only: Only fetch user-confirmed predictions
        
        Returns:
            DataFrame with pest prediction data
        """
        print(f"📊 Fetching pest predictions from last {days_back} days...")
        
        # Calculate date range
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        # Build query
        query = self.supabase.table('pest_predictions').select('*').gte('created_at', start_date)
        
        if min_confidence:
            query = query.gte('confidence_score', min_confidence)
        
        if user_confirmed_only:
            query = query.eq('user_confirmed', True)
        
        # Execute query
        response = query.execute()
        
        if not response.data:
            print("⚠️ No pest predictions found")
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        print(f"✅ Fetched {len(df)} pest predictions")
        
        # Add features for analysis
        df['date'] = pd.to_datetime(df['created_at'])
        df['month'] = df['date'].dt.month
        df['season'] = df['month'].apply(self._get_season)
        
        return df
    
    def fetch_pest_training_data(self) -> Dict[str, List]:
        """
        Fetch pest data formatted for model retraining
        
        Returns:
            Dictionary with image_urls, labels, and metadata
        """
        print("🎯 Fetching pest training data...")
        
        # Fetch confirmed predictions with user feedback
        response = self.supabase.table('pest_predictions')\
            .select('image_url, pest_detected, actual_pest, confidence_score, user_confirmed, crop_affected')\
            .eq('user_confirmed', True)\
            .execute()
        
        if not response.data:
            print("⚠️ No confirmed pest training data available")
            return {"image_urls": [], "labels": [], "metadata": []}
        
        training_data = {
            "image_urls": [],
            "labels": [],
            "metadata": []
        }
        
        for record in response.data:
            # Use actual_pest if user corrected, otherwise use detected pest
            label = record.get('actual_pest') or record.get('pest_detected')
            
            training_data["image_urls"].append(record['image_url'])
            training_data["labels"].append(label)
            training_data["metadata"].append({
                "confidence": record['confidence_score'],
                "crop": record.get('crop_affected'),
                "user_confirmed": record['user_confirmed']
            })
        
        print(f"✅ Prepared {len(training_data['labels'])} pest training samples")
        return training_data
    
    # ===================================
    # DISEASE DETECTION DATA
    # ===================================
    
    def fetch_disease_predictions(
        self, 
        days_back: int = 30,
        min_confidence: float = 0.7,
        user_confirmed_only: bool = False
    ) -> pd.DataFrame:
        """Fetch disease detection predictions"""
        print(f"📊 Fetching disease predictions from last {days_back} days...")
        
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        query = self.supabase.table('disease_predictions').select('*').gte('created_at', start_date)
        
        if min_confidence:
            query = query.gte('confidence_score', min_confidence)
        
        if user_confirmed_only:
            query = query.eq('user_confirmed', True)
        
        response = query.execute()
        
        if not response.data:
            print("⚠️ No disease predictions found")
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        print(f"✅ Fetched {len(df)} disease predictions")
        
        df['date'] = pd.to_datetime(df['created_at'])
        df['month'] = df['date'].dt.month
        df['season'] = df['month'].apply(self._get_season)
        
        return df
    
    def fetch_disease_training_data(self) -> Dict[str, List]:
        """Fetch disease data formatted for model retraining"""
        print("🎯 Fetching disease training data...")
        
        response = self.supabase.table('disease_predictions')\
            .select('image_url, disease_detected, actual_disease, confidence_score, user_confirmed, crop_affected, growth_stage, treatment_effectiveness')\
            .eq('user_confirmed', True)\
            .execute()
        
        if not response.data:
            print("⚠️ No confirmed disease training data available")
            return {"image_urls": [], "labels": [], "metadata": []}
        
        training_data = {
            "image_urls": [],
            "labels": [],
            "metadata": []
        }
        
        for record in response.data:
            label = record.get('actual_disease') or record.get('disease_detected')
            
            training_data["image_urls"].append(record['image_url'])
            training_data["labels"].append(label)
            training_data["metadata"].append({
                "confidence": record['confidence_score'],
                "crop": record.get('crop_affected'),
                "growth_stage": record.get('growth_stage'),
                "treatment_effectiveness": record.get('treatment_effectiveness'),
                "user_confirmed": record['user_confirmed']
            })
        
        print(f"✅ Prepared {len(training_data['labels'])} disease training samples")
        return training_data
    
    # ===================================
    # STORAGE CONDITION DATA
    # ===================================
    
    def fetch_storage_predictions(
        self, 
        days_back: int = 30,
        min_confidence: float = 0.7
    ) -> pd.DataFrame:
        """Fetch storage condition predictions"""
        print(f"📊 Fetching storage predictions from last {days_back} days...")
        
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        response = self.supabase.table('storage_predictions')\
            .select('*')\
            .gte('created_at', start_date)\
            .gte('confidence_score', min_confidence)\
            .execute()
        
        if not response.data:
            print("⚠️ No storage predictions found")
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        print(f"✅ Fetched {len(df)} storage predictions")
        
        df['date'] = pd.to_datetime(df['created_at'])
        
        return df
    
    def fetch_storage_training_data(self) -> Dict[str, List]:
        """Fetch storage data formatted for model retraining"""
        print("🎯 Fetching storage training data...")
        
        response = self.supabase.table('storage_predictions')\
            .select('image_url, storage_condition, issues_detected, risk_level, confidence_score, user_confirmed, actual_outcome, crop_stored, storage_type, temperature, humidity')\
            .eq('user_confirmed', True)\
            .execute()
        
        if not response.data:
            print("⚠️ No confirmed storage training data available")
            return {"image_urls": [], "labels": [], "metadata": []}
        
        training_data = {
            "image_urls": [],
            "labels": [],
            "metadata": []
        }
        
        for record in response.data:
            training_data["image_urls"].append(record['image_url'])
            training_data["labels"].append(record['storage_condition'])
            training_data["metadata"].append({
                "issues": record.get('issues_detected', []),
                "risk_level": record.get('risk_level'),
                "confidence": record['confidence_score'],
                "actual_outcome": record.get('actual_outcome'),
                "crop": record.get('crop_stored'),
                "storage_type": record.get('storage_type'),
                "temperature": record.get('temperature'),
                "humidity": record.get('humidity')
            })
        
        print(f"✅ Prepared {len(training_data['labels'])} storage training samples")
        return training_data
    
    # ===================================
    # ANALYTICS & INSIGHTS
    # ===================================
    
    def get_pest_distribution(self, days_back: int = 90) -> Dict:
        """Get distribution of pest types detected"""
        df = self.fetch_pest_predictions(days_back=days_back)
        
        if df.empty:
            return {}
        
        distribution = df['pest_detected'].value_counts().to_dict()
        
        # Add seasonal patterns
        seasonal_dist = df.groupby(['season', 'pest_detected']).size().unstack(fill_value=0)
        
        return {
            "overall_distribution": distribution,
            "seasonal_patterns": seasonal_dist.to_dict(),
            "total_predictions": len(df),
            "unique_pests": df['pest_detected'].nunique(),
            "avg_confidence": float(df['confidence_score'].mean())
        }
    
    def get_disease_distribution(self, days_back: int = 90) -> Dict:
        """Get distribution of diseases detected"""
        df = self.fetch_disease_predictions(days_back=days_back)
        
        if df.empty:
            return {}
        
        distribution = df['disease_detected'].value_counts().to_dict()
        
        # Crop-specific patterns
        crop_disease = df.groupby(['crop_affected', 'disease_detected']).size().unstack(fill_value=0)
        
        return {
            "overall_distribution": distribution,
            "crop_specific_patterns": crop_disease.to_dict(),
            "total_predictions": len(df),
            "unique_diseases": df['disease_detected'].nunique(),
            "avg_confidence": float(df['confidence_score'].mean())
        }
    
    def get_model_performance_metrics(self) -> Dict:
        """Calculate model performance metrics based on user feedback"""
        print("📈 Calculating model performance metrics...")
        
        metrics = {
            "pest_detection": self._calculate_pest_metrics(),
            "disease_detection": self._calculate_disease_metrics(),
            "storage_assessment": self._calculate_storage_metrics()
        }
        
        return metrics
    
    def _calculate_pest_metrics(self) -> Dict:
        """Calculate pest detection model accuracy"""
        response = self.supabase.table('pest_predictions')\
            .select('pest_detected, actual_pest, confidence_score, user_confirmed')\
            .not_.is_('user_confirmed', 'null')\
            .execute()
        
        if not response.data:
            return {"accuracy": 0, "total_feedback": 0}
        
        df = pd.DataFrame(response.data)
        
        # Calculate accuracy (where model was correct)
        correct = df[df['user_confirmed'] == True].shape[0]
        total = len(df)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Average confidence
        avg_confidence = float(df['confidence_score'].mean())
        
        return {
            "accuracy": round(accuracy, 2),
            "total_feedback": total,
            "correct_predictions": correct,
            "avg_confidence": round(avg_confidence, 4)
        }
    
    def _calculate_disease_metrics(self) -> Dict:
        """Calculate disease detection model accuracy"""
        response = self.supabase.table('disease_predictions')\
            .select('disease_detected, actual_disease, confidence_score, user_confirmed')\
            .not_.is_('user_confirmed', 'null')\
            .execute()
        
        if not response.data:
            return {"accuracy": 0, "total_feedback": 0}
        
        df = pd.DataFrame(response.data)
        
        correct = df[df['user_confirmed'] == True].shape[0]
        total = len(df)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        avg_confidence = float(df['confidence_score'].mean())
        
        return {
            "accuracy": round(accuracy, 2),
            "total_feedback": total,
            "correct_predictions": correct,
            "avg_confidence": round(avg_confidence, 4)
        }
    
    def _calculate_storage_metrics(self) -> Dict:
        """Calculate storage assessment model accuracy"""
        response = self.supabase.table('storage_predictions')\
            .select('storage_condition, confidence_score, user_confirmed, actual_outcome')\
            .not_.is_('user_confirmed', 'null')\
            .execute()
        
        if not response.data:
            return {"accuracy": 0, "total_feedback": 0}
        
        df = pd.DataFrame(response.data)
        
        correct = df[df['user_confirmed'] == True].shape[0]
        total = len(df)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        avg_confidence = float(df['confidence_score'].mean())
        
        return {
            "accuracy": round(accuracy, 2),
            "total_feedback": total,
            "correct_predictions": correct,
            "avg_confidence": round(avg_confidence, 4)
        }
    
    # ===================================
    # DATA EXPORT FOR TRAINING
    # ===================================
    
    def export_training_dataset(
        self, 
        prediction_type: str,
        output_format: str = "csv"
    ) -> str:
        """
        Export training dataset to file
        
        Args:
            prediction_type: 'pest', 'disease', or 'storage'
            output_format: 'csv', 'json', or 'parquet'
        
        Returns:
            Path to exported file
        """
        print(f"💾 Exporting {prediction_type} training dataset...")
        
        # Fetch appropriate data
        if prediction_type == "pest":
            data = self.fetch_pest_training_data()
        elif prediction_type == "disease":
            data = self.fetch_disease_training_data()
        elif prediction_type == "storage":
            data = self.fetch_storage_training_data()
        else:
            raise ValueError(f"Unknown prediction type: {prediction_type}")
        
        if not data["labels"]:
            print("⚠️ No data to export")
            return ""
        
        # Create DataFrame
        df = pd.DataFrame({
            "image_url": data["image_urls"],
            "label": data["labels"],
            "metadata": data["metadata"]
        })
        
        # Export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prediction_type}_training_data_{timestamp}"
        
        if output_format == "csv":
            filepath = self.data_dir / f"{filename}.csv"
            df.to_csv(filepath, index=False)
        elif output_format == "json":
            filepath = self.data_dir / f"{filename}.json"
            df.to_json(filepath, orient="records", indent=2)
        elif output_format == "parquet":
            filepath = self.data_dir / f"{filename}.parquet"
            df.to_parquet(filepath, index=False)
        else:
            raise ValueError(f"Unknown format: {output_format}")
        
        print(f"✅ Exported to: {filepath}")
        return str(filepath)
    
    def export_all_training_data(self) -> Dict[str, str]:
        """Export all training datasets"""
        print("📦 Exporting all training datasets...")
        
        exports = {
            "pest": self.export_training_dataset("pest", "csv"),
            "disease": self.export_training_dataset("disease", "csv"),
            "storage": self.export_training_dataset("storage", "csv")
        }
        
        print("✅ All datasets exported!")
        return exports
    
    # ===================================
    # HELPER METHODS
    # ===================================
    
    @staticmethod
    def _get_season(month: int) -> str:
        """Determine season from month (East Africa context)"""
        if month in [3, 4, 5]:
            return "long_rains"
        elif month in [10, 11, 12]:
            return "short_rains"
        elif month in [6, 7, 8, 9]:
            return "dry_season"
        else:
            return "transition"


# ===================================
# USAGE EXAMPLE
# ===================================

if __name__ == "__main__":
    service = DataCollectionService()
    
    # Fetch recent pest predictions
    pest_df = service.fetch_pest_predictions(days_back=30)
    print(f"\nPest Predictions Shape: {pest_df.shape}")
    
    # Get pest distribution
    pest_dist = service.get_pest_distribution(days_back=90)
    print(f"\nPest Distribution: {pest_dist}")
    
    # Get model performance
    metrics = service.get_model_performance_metrics()
    print(f"\nModel Performance: {metrics}")
    
    # Export training data
    exports = service.export_all_training_data()
    print(f"\nExported Files: {exports}")
