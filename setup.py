from setuptools import setup, find_packages

setup(
    name="ai_trainer",
    version="0.1.0",
    description="Ein Framework für autonomes AI Training und Datenverarbeitung",
    author="Cursor AI Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.1",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "supabase-py>=0.0.2",
        "aiohttp>=3.8.1",
        "python-multipart>=0.0.5",
        "pillow>=8.3.2",
        "opencv-python>=4.5.3.56",
        "numpy>=1.21.2",
        "pydantic>=1.8.2"
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