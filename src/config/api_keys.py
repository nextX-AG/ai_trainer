import os
from pathlib import Path
import json
from typing import Dict
from cryptography.fernet import Fernet

class APIKeyManager:
    def __init__(self):
        self.config_dir = Path("config")
        self.config_file = self.config_dir / "api_keys.enc"
        self.key_file = self.config_dir / ".key"
        self._ensure_config_dir()
        self._init_encryption()
        
    def _ensure_config_dir(self):
        """Erstellt Konfigurationsverzeichnis falls nicht vorhanden"""
        self.config_dir.mkdir(exist_ok=True)
        
    def _init_encryption(self):
        """Initialisiert oder lädt den Verschlüsselungsschlüssel"""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        else:
            with open(self.key_file, 'rb') as f:
                key = f.read()
        self.cipher = Fernet(key)
        
    def save_api_key(self, service: str, api_key: str):
        """Speichert einen verschlüsselten API-Key"""
        keys = self.load_api_keys()
        keys[service] = api_key
        
        encrypted_data = self.cipher.encrypt(json.dumps(keys).encode())
        with open(self.config_file, 'wb') as f:
            f.write(encrypted_data)
            
    def load_api_keys(self) -> Dict[str, str]:
        """Lädt alle API-Keys"""
        if not self.config_file.exists():
            return {}
            
        with open(self.config_file, 'rb') as f:
            encrypted_data = f.read()
            
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception:
            return {}
            
    def get_api_key(self, service: str) -> str:
        """Holt einen spezifischen API-Key"""
        keys = self.load_api_keys()
        return keys.get(service) 