import torch
from torch.utils.data import Dataset
from pathlib import Path
import cv2
import numpy as np
from typing import Dict, List, Tuple
import random
import albumentations as A
from albumentations.pytorch import ToTensorV2

class FaceDataset(Dataset):
    def __init__(self, 
                 dataset_path: Path,
                 image_size: int = 224,
                 augment: bool = True):
        """
        Args:
            dataset_path: Pfad zum Dataset
            image_size: Zielgröße der Bilder
            augment: Ob Datenaugmentation verwendet werden soll
        """
        self.dataset_path = Path(dataset_path)
        self.image_size = image_size
        self.augment = augment
        
        # Alle Bilder finden
        self.image_paths = list(self.dataset_path.rglob("*.jpg")) + \
                          list(self.dataset_path.rglob("*.png"))
                          
        # Augmentation Pipeline
        self.transform = A.Compose([
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.OneOf([
                A.RandomBrightness(limit=0.2, p=1),
                A.RandomContrast(limit=0.2, p=1),
                A.RandomGamma(p=1)
            ], p=0.3),
            A.OneOf([
                A.GaussNoise(p=1),
                A.GaussianBlur(p=1),
                A.MotionBlur(p=1)
            ], p=0.2),
            A.Normalize(
                mean=[0.5, 0.5, 0.5],
                std=[0.5, 0.5, 0.5],
            ),
            ToTensorV2()
        ])
        
        self.basic_transform = A.Compose([
            A.Resize(image_size, image_size),
            A.Normalize(
                mean=[0.5, 0.5, 0.5],
                std=[0.5, 0.5, 0.5],
            ),
            ToTensorV2()
        ])
        
    def __len__(self) -> int:
        return len(self.image_paths)
        
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        # Quellbild laden
        source_path = self.image_paths[idx]
        source_img = cv2.imread(str(source_path))
        source_img = cv2.cvtColor(source_img, cv2.COLOR_BGR2RGB)
        
        # Zufälliges Zielbild wählen (nicht das gleiche wie Quelle)
        target_idx = random.choice([i for i in range(len(self)) if i != idx])
        target_path = self.image_paths[target_idx]
        target_img = cv2.imread(str(target_path))
        target_img = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)
        
        # Augmentation anwenden
        if self.augment:
            source_augmented = self.transform(image=source_img)
            target_augmented = self.transform(image=target_img)
        else:
            source_augmented = self.basic_transform(image=source_img)
            target_augmented = self.basic_transform(image=target_img)
            
        return {
            'source': source_augmented['image'],
            'target': target_augmented['image'],
            'source_path': str(source_path),
            'target_path': str(target_path)
        } 