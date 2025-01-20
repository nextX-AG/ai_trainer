from supabase import create_client

# Supabase Konfiguration
SUPABASE_URL = "https://peltztqybrtzbnduddvf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlbHR6dHF5YnJ0emJuZHVkZHZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczOTAyOTEsImV4cCI6MjA1Mjk2NjI5MX0.ImCYzU4gYYXKmYHrIHagC7Ohh3OctNyf7w-vOFx2fe8"

# Client erstellen
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Einfache Abfrage
try:
    response = supabase.table('projects').select("*").limit(1).execute()
    print("Verbindung erfolgreich!")
    print(f"Response: {response}")
except Exception as e:
    print(f"Fehler: {str(e)}") 