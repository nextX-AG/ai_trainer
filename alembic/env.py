from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
from dotenv import load_dotenv

# Models importieren
from src.database.models import Base

# Environment-Variablen laden
load_dotenv('.env.development')

# Alembic Config Objekt
config = context.config

# Logging-Konfiguration von alembic.ini interpretieren
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData Objekt für 'autogenerate' Support
target_metadata = Base.metadata

def get_url():
    # URL-kodierte Version des Passworts verwenden
    password = os.getenv('SUPABASE_DB_PASSWORD').replace('#', '%23').replace('@', '%40')
    return f"postgresql://{os.getenv('SUPABASE_DB_USER')}:{password}@{os.getenv('SUPABASE_DB_HOST')}:6543/{os.getenv('SUPABASE_DB_NAME')}"

def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 