from setuptools import setup, find_packages

setup(
    name="cursor-ai",
    version="0.1.0",
    description="Ein Framework für autonomes AI Training und Datenverarbeitung",
    author="Cursor AI Team",
    packages=find_packages(),
    install_requires=[
        # Basis-Dependencies
        "numpy>=1.19.0",
        "opencv-python-headless>=4.5.0",
        "pillow>=8.0.0",
        "dlib>=19.22.0",
        "tensorflow>=2.0.0",
        "mtcnn>=0.1.0",
        
        # API und Web
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "aiofiles>=0.7.0",
        
        # Scraping und Datenerfassung
        "scrapy>=2.5.0",
        "beautifulsoup4>=4.9.0",
        "requests>=2.26.0",
        
        # Datenbank
        "sqlalchemy>=1.4.0",
        "alembic>=1.7.0",
        "psycopg2-binary>=2.9.0",
    ],
    extras_require={
        'dev': [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "mypy>=0.910",
            "pylint>=2.9.0",
            "python-json-logger>=2.0.0"
        ],
        'gpu': [
            "torch>=1.9.0",
            "torchvision>=0.10.0",
        ]
    },
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'cursor-ai=src.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
) 