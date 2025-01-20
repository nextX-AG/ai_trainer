import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
import logging
from typing import Dict, Optional, List
from datetime import datetime

from src.config import TrainingConfig
from src.data.dataset import FaceDataset
from simswap.models.model import SimSwap
from simswap.losses import IDLoss, AttributeLoss, ReconstructionLoss
from src.database.database import get_db

logger = logging.getLogger(__name__)

class TrainingService:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.optimizer = None
        self.current_epoch = 0
        self.global_step = 0
        self.db = get_db()
        
    def setup(self, dataset_path: Path):
        """Initialisiert das Training"""
        # Dataset und DataLoader
        dataset = FaceDataset(dataset_path)
        self.train_loader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.num_workers
        )
        
        # Modell
        self.model = SimSwap()
        self.model.to(self.device)
        
        # Optimizer
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate
        )
        
        # Loss Functions
        self.id_loss = IDLoss().to(self.device)
        self.attr_loss = AttributeLoss().to(self.device)
        self.rec_loss = ReconstructionLoss().to(self.device)
        
    async def train_epoch(self):
        """Trainiert eine Epoche"""
        self.model.train()
        epoch_losses = []
        
        for batch_idx, batch in enumerate(self.train_loader):
            source_imgs = batch['source'].to(self.device)
            target_imgs = batch['target'].to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(source_imgs, target_imgs)
            
            # Losses berechnen
            id_loss = self.id_loss(output, source_imgs) * self.config.id_loss_weight
            attr_loss = self.attr_loss(output, target_imgs) * self.config.attr_loss_weight
            rec_loss = self.rec_loss(output, target_imgs) * self.config.rec_loss_weight
            
            total_loss = id_loss + attr_loss + rec_loss
            
            # Backward pass
            total_loss.backward()
            self.optimizer.step()
            
            # Logging
            if batch_idx % 10 == 0:
                logger.info(f"Epoch {self.current_epoch} [{batch_idx}/{len(self.train_loader)}] "
                          f"Loss: {total_loss.item():.4f}")
            
            epoch_losses.append(total_loss.item())
            self.global_step += 1
            
            # Checkpointing
            if self.global_step % self.config.checkpoint_interval == 0:
                self.save_checkpoint()
                
        self.current_epoch += 1
        return sum(epoch_losses) / len(epoch_losses)
        
    def save_checkpoint(self, path: Optional[Path] = None):
        """Speichert einen Checkpoint"""
        if path is None:
            path = Path(f"checkpoints/model_{self.global_step}.pth")
            
        path.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'config': self.config
        }
        
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint gespeichert: {path}")

    def create_training_job(self, model_id: str, dataset_id: str, parameters: Dict = None) -> Dict:
        return self.db.table('training_jobs').insert({
            'model_id': model_id,
            'dataset_id': dataset_id,
            'status': 'pending',
            'progress': 0.0,
            'parameters': parameters or {},
            'metrics': {},
            'started_at': datetime.utcnow().isoformat()
        }).execute()

    def get_training_job(self, job_id: str) -> Optional[Dict]:
        result = self.db.table('training_jobs').select('*').eq('id', job_id).execute()
        return result.data[0] if result.data else None

    def list_training_jobs(self, model_id: Optional[str] = None) -> List[Dict]:
        query = self.db.table('training_jobs').select('*')
        if model_id:
            query = query.eq('model_id', model_id)
        result = query.execute()
        return result.data

    def update_training_job(self, job_id: str, data: Dict) -> Dict:
        return self.db.table('training_jobs').update(data).eq('id', job_id).execute() 