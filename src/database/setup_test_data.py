from src.database.database import get_db
from src.services.project_service import ProjectService
from src.services.model_service import ModelService
from src.services.dataset_service import DatasetService

def setup_test_data():
    db = get_db()
    project_service = ProjectService()
    model_service = ModelService()
    dataset_service = DatasetService()

    # 1. Verfügbare Projekte anzeigen
    print("\n=== Verfügbare Projekte ===")
    projects_response = project_service.list_projects()
    projects = projects_response.data if hasattr(projects_response, 'data') else projects_response
    
    if projects:
        print("Gefundene Projekte:")
        for p in projects:
            print(f"ID: {p['id']} - Name: {p['name']}")
        
        # Projekt auswählen
        project_id = projects[0]['id']  # Nehmen wir das erste Projekt
        print(f"\nVerwende Projekt: {projects[0]['name']} (ID: {project_id})")
    else:
        # Neues Projekt erstellen
        print("\nKeine Projekte gefunden. Erstelle neues Projekt...")
        project_response = project_service.create_project(
            name="Test Projekt",
            description="Automatisch erstelltes Test-Projekt"
        )
        project = project_response.data[0] if hasattr(project_response, 'data') else project_response
        project_id = project['id']
        print(f"Neues Projekt erstellt: {project['name']} (ID: {project_id})")

    # 2. Test Model erstellen
    print("\n=== Erstelle Test Model ===")
    model_response = model_service.create_model(
        name="SimSwap Test Model",
        project_id=project_id,
        model_type="simswap"
    )
    model = model_response.data[0] if hasattr(model_response, 'data') else model_response
    print(f"Model erstellt: {model['name']} (ID: {model['id']})")

    # 3. Test Dataset erstellen
    print("\n=== Erstelle Test Dataset ===")
    dataset_response = dataset_service.create_dataset(
        name="Gesichter Dataset",
        project_id=project_id,
        description="Test Dataset für Gesichtserkennung"
    )
    dataset = dataset_response.data[0] if hasattr(dataset_response, 'data') else dataset_response
    print(f"Dataset erstellt: {dataset['name']} (ID: {dataset['id']})")

    print("\n=== Setup abgeschlossen ===")
    return {
        'project': project_id,
        'model': model['id'],
        'dataset': dataset['id']
    }

if __name__ == "__main__":
    try:
        ids = setup_test_data()
        print("\nErstellte IDs für weitere Verwendung:")
        print(f"Project ID: {ids['project']}")
        print(f"Model ID: {ids['model']}")
        print(f"Dataset ID: {ids['dataset']}")
    except Exception as e:
        print(f"\nFehler beim Setup: {str(e)}") 