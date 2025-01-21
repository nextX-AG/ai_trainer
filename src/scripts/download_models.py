import os
import urllib.request
import bz2
import shutil
from pathlib import Path

def download_shape_predictor():
    """Downloads the shape predictor model if it doesn't exist"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    predictor_path = models_dir / "shape_predictor_68_face_landmarks.dat"
    
    if not predictor_path.exists():
        print("Downloading shape predictor model...")
        url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        bz2_path = predictor_path.with_suffix('.dat.bz2')
        
        # Download
        urllib.request.urlretrieve(url, bz2_path)
        
        # Extract
        with bz2.BZ2File(bz2_path) as fr, open(predictor_path, 'wb') as fw:
            shutil.copyfileobj(fr, fw)
            
        # Cleanup
        bz2_path.unlink()
        print("Shape predictor model downloaded successfully!")
    else:
        print("Shape predictor model already exists.")

if __name__ == "__main__":
    download_shape_predictor() 