"""
Seed Test Data for Growth Tracking
Creates a test plot and scheduled events for a user
"""

import sys
import os
from datetime import datetime, timedelta
import uuid

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.supabase_auth import supabase_client

def seed_growth_tracking_data(user_id: str):
    """
    Create test plot and events for a user
    
    Args:
        user_id: The user ID to create data for
    """
    
    print(f"🌱 Seeding growth tracking data for user: {user_id}")
    
    try:
        # 1. Create a test plot
        plot_id = str(uuid.uuid4())
        plot_data = {
            "id": plot_id,
            "user_id": user_id,
            "plot_name": "Demo Maize Plot",
            "crop_name": "Maize",
            "initial_image_url": "https://example.com/maize-initial.jpg",
            "planting_date": datetime.utcnow().isoformat(),
            "location": {
                "latitude": -1.286389,
                "longitude": 36.817223
            },
            "area_size": 2.5,
            "notes": "Test plot for growth tracking demo",
            "setup_completed_at": datetime.utcnow().isoformat()
        }
        
        print(f"📍 Creating digital plot: {plot_data['plot_name']}")
        result = supabase_client.table('digital_plots').insert(plot_data).execute()
        print(f"✅ Plot created with ID: {plot_id}")
        
        # 2. Create scheduled events
        events = []
        
        # Weeding event (upcoming)
        events.append({
            "id": str(uuid.uuid4()),
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "farm_practice",
            "practice_name": "Weeding",
            "scheduled_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            "status": "scheduled",
            "description": "Manual weeding to remove competing plants",
            "priority": "high",
            "estimated_labor_hours": 4
        })
        
        # Fertilizer application (upcoming)
        events.append({
            "id": str(uuid.uuid4()),
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "farm_practice",
            "practice_name": "Fertilizer Application",
            "scheduled_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "scheduled",
            "description": "Apply NPK 23:23:0 fertilizer",
            "priority": "high",
            "estimated_labor_hours": 2
        })
        
        # Photo reminder (upcoming)
        events.append({
            "id": str(uuid.uuid4()),
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "photo_reminder",
            "practice_name": "Weekly Photo Check",
            "scheduled_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "status": "scheduled",
            "description": "Take photos of plant growth for AI analysis",
            "priority": "medium",
            "estimated_labor_hours": 0.5
        })
        
        # Pest monitoring (upcoming)
        events.append({
            "id": str(uuid.uuid4()),
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "alert_action",
            "practice_name": "Pest Monitoring",
            "scheduled_date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
            "status": "scheduled",
            "description": "Check for fall armyworm and other pests",
            "priority": "high",
            "estimated_labor_hours": 1
        })
        
        # Irrigation (upcoming)
        events.append({
            "id": str(uuid.uuid4()),
            "plot_id": plot_id,
            "user_id": user_id,
            "event_type": "farm_practice",
            "practice_name": "Irrigation",
            "scheduled_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "status": "scheduled",
            "description": "Water the crops - soil moisture is low",
            "priority": "urgent",
            "estimated_labor_hours": 3
        })
        
        print(f"📅 Creating {len(events)} scheduled events...")
        result = supabase_client.table('scheduled_events').insert(events).execute()
        print(f"✅ {len(events)} events created successfully")
        
        print("\n✨ Seed data creation complete!")
        print(f"📊 Summary:")
        print(f"   - Plot ID: {plot_id}")
        print(f"   - Plot Name: {plot_data['plot_name']}")
        print(f"   - Scheduled Events: {len(events)}")
        print(f"\n🚀 You can now view this data in the Growth Tracking screen!")
        
        return {
            "success": True,
            "plot_id": plot_id,
            "events_created": len(events)
        }
        
    except Exception as e:
        print(f"❌ Error seeding data: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Get user ID from command line or use default
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        # You'll need to replace this with an actual user ID from your database
        print("❌ Please provide a user ID as an argument")
        print("Usage: python seed_growth_data.py <user_id>")
        print("\nTo find your user ID:")
        print("1. Log in to your app")
        print("2. Check the console logs - your user ID should be printed")
        print("3. Or check your Supabase profiles table")
        sys.exit(1)
    
    seed_growth_tracking_data(user_id)
