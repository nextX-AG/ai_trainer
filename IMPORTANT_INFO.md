# Wichtige Projekt-Informationen

## Datenbank
- Wir nutzen **Supabase** statt direkter PostgreSQL-Verbindung
- Keine Alembic Migrationen verwenden
- Tabellen werden über Supabase verwaltet
- Bei SQL-Ausführung: `db.rpc('exec_sql', {'query': "SQL HIER"})` statt `db.query()`

## Architektur
- Frontend: React + TypeScript
- Backend: FastAPI + Python
- Datenbank: Supabase (PostgreSQL)
- Templates: Jinja2 für Admin-Interface

## Projektstruktur 

# Wichtige Entwicklungsinformationen

## Routing und Navigation

### Root-Route
- Die Root-Route ("/") leitet standardmäßig zu /projects weiter
- Implementiert in `src/api/views/index_view.py`
- Muss als erste Route in `app.py` registriert werden 