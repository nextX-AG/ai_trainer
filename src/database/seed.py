from src.services.model_service import ModelService
from src.services.dataset_service import DatasetService

def seed_data():
    model_service = ModelService()
    dataset_service = DatasetService()
    
    # Test Model erstellen
    model = model_service.create_model(
        name="Test SimSwap Model",
        project_id="1",  # Anpassen an ein existierendes Projekt
        model_type="simswap"
    )
    
    # Test Dataset erstellen
    dataset = dataset_service.create_dataset(
        name="Test Dataset",
        project_id="1",  # Anpassen an ein existierendes Projekt
        description="Ein Test Dataset"
    )

if __name__ == "__main__":
    seed_data() 