from supabase import create_client, Client
import json

# Supabase Konfiguration
SUPABASE_URL = "https://peltztqybrtzbnduddvf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlbHR6dHF5YnJ0emJuZHVkZHZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczOTAyOTEsImV4cCI6MjA1Mjk2NjI5MX0.ImCYzU4gYYXKmYHrIHagC7Ohh3OctNyf7w-vOFx2fe8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_tables():
    # Test Scene erstellen
    scene_data = {
        "project_id": "19622b45-39a4-4f46-8d06-b713284c2cde",  # ID vom existierenden Projekt
        "name": "Test Scene",
        "description": "Eine Test-Scene",
        "keywords": json.dumps(["test", "demo"]),
        "target_attributes": json.dumps({"type": "training", "difficulty": "easy"})
    }
    
    try:
        response = supabase.table('scenes').insert(scene_data).execute()
        print("Scene erstellt:", response.data)
        
        # Test Download erstellen
        download_data = {
            "project_id": "19622b45-39a4-4f46-8d06-b713284c2cde",
            "url": "https://example.com/test.mp4",
            "metadata": json.dumps({"format": "mp4", "duration": 120})
        }
        
        response = supabase.table('downloads').insert(download_data).execute()
        print("Download erstellt:", response.data)
        
    except Exception as e:
        print(f"Fehler: {str(e)}")

if __name__ == "__main__":
    test_tables() 