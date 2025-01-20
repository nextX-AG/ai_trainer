from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

def test_db_connection():
    load_dotenv('.env.development')
    db_url = os.getenv('DATABASE_URL')
    
    try:
        engine = create_engine(db_url)
        # Versuche eine Verbindung herzustellen
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("Datenbankverbindung erfolgreich!")
            return True
    except Exception as e:
        print(f"Fehler bei der Datenbankverbindung: {e}")
        return False

if __name__ == "__main__":
    test_db_connection() 