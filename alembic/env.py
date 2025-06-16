from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv
import os
import sys

# Add your app root to sys.path if necessary


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import your Base or models here
from app.main.model.advogado import Advogado
from app.main.model.requerente import Requerente
from app.main.model.demanda import Demanda
from app.main.model.advogado_pfp import AdvogadoPFP
from app.main.model.processo import Processo
from app.main.model.chat_message import ChatMessage
from app.main.model.chat import Chat
# import other models as needed

# IMPORTANT: import your Base metadata object, or create one if models don't share it
from app.main.extensions import db

target_metadata = db.metadata  # Assuming you use SQLAlchemy instance's metadata

config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

load_dotenv()
db_user = os.getenv('MYSQL_USER')
db_password = os.getenv('MYSQL_PASSWORD')
db_host = os.getenv('MYSQL_HOST')
db_name = os.getenv('MYSQL_DB')

alembic_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:3306/{db_name}"
config.set_main_option('sqlalchemy.url', alembic_url)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
