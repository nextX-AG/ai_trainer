from dotenv import load_dotenv
from database import create_tables
import os

if __name__ == "__main__":
    # Lade Umgebungsvariablen
    load_dotenv('.env.development')
    
    # Überprüfe, ob die notwendigen Variablen gesetzt sind
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("Error: SUPABASE_URL und SUPABASE_KEY müssen in .env.development gesetzt sein")
        exit(1)
        
    create_tables()
    print("Tabellen wurden erfolgreich erstellt!") 