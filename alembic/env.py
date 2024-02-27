# env.py

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Этот блок кода загружает вашу модель SQLAlchemy
from app.database import Base
from app.models import User, Note
target_metadata = Base.metadata

# Загрузка конфигурации файла alembic.ini
config = context.config

# Настройка подключения к базе данных
config.set_main_option("sqlalchemy.url", "postgresql://postgres:1@localhost/test_db")

# Подключение к базе данных
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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

# Запуск миграций
run_migrations_online()
