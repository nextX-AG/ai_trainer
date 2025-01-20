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

Die Anwendung ist in folgende Hauptbereiche unterteilt:
- Overview (Dashboard)
- Projekte (Projektverwaltung)
- Scraping (Datensammlung)
- Training (Modelltraining)
- Datasets (Datenverwaltung)
- Models (Modellverwaltung)
- Face Swap Studio (Anwendung)
- Einstellungen (Konfiguration)

### Navigation
Die Navigation ist hierarchisch aufgebaut:
1. Hauptnavigation (immer sichtbar)
2. Kontextabhängige Unternavigation
3. Einstellungen über das Zahnrad-Icon erreichbar

# Wichtige Entwicklungsinformationen

## Routing und Navigation

### Root-Route
- Die Root-Route ("/") leitet standardmäßig zu /projects weiter
- Implementiert in `src/api/views/index_view.py`
- Muss als erste Route in `app.py` registriert werden 