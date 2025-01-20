import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import vgg19
import numpy as np

class IDLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval()
        for param in self.facenet.parameters():
            param.requires_grad = False
            
    def forward(self, generated, real):
        gen_features = self.facenet(generated)
        real_features = self.facenet(real)
        return F.l1_loss(gen_features, real_features)

class AttributeLoss(nn.Module):
    def __init__(self):
        super().__init__()
        vgg = vgg19(pretrained=True).features
        self.slice1 = torch.nn.Sequential()
        self.slice2 = torch.nn.Sequential()
        self.slice3 = torch.nn.Sequential()
        
        for x in range(2):
            self.slice1.add_module(str(x), vgg[x])
        for x in range(2, 7):
            self.slice2.add_module(str(x), vgg[x])
        for x in range(7, 12):
            self.slice3.add_module(str(x), vgg[x])
            
        for param in self.parameters():
            param.requires_grad = False
            
    def forward(self, generated, target):
        gen_features = [self.slice1(generated)]
        gen_features.append(self.slice2(gen_features[-1]))
        gen_features.append(self.slice3(gen_features[-1]))
        
        target_features = [self.slice1(target)]
        target_features.append(self.slice2(target_features[-1]))
        target_features.append(self.slice3(target_features[-1]))
        
        loss = 0
        for gen_feat, target_feat in zip(gen_features, target_features):
            loss += F.l1_loss(gen_feat, target_feat)
            
        return loss / len(gen_features)

class ReconstructionLoss(nn.Module):
    def __init__(self):
        super().__init__()
        
    def forward(self, generated, target):
        return F.l1_loss(generated, target) 