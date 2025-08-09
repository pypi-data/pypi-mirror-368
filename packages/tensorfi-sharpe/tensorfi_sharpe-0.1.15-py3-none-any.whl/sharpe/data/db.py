"""
database read and write
"""

from contextlib import contextmanager
import os
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from typing import Generator, Iterable, Optional, Union, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import insert

from .model import Base
from ..utils.logger import get_logger
from ..utils import env

# Configure logger
logger = get_logger(__name__)

env.load_env()


def get_database_url() -> str:
    """Get database URL from environment variables."""
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    NETWORK_PROTOCOL = os.getenv("NETWORK_PROTOCOL")

    if not all([DB_PASSWORD, DB_HOST, DB_PORT, NETWORK_PROTOCOL]):
        raise ValueError("One or more database environment variables are not set.")

    if NETWORK_PROTOCOL == "IPV4":
        conn_str = f"postgresql://postgres.{DB_HOST}:{DB_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:{DB_PORT}/postgres"
    elif NETWORK_PROTOCOL == "IPV6":
        conn_str = f"postgresql://postgres:{DB_PASSWORD}@db.{DB_HOST}.supabase.co:{DB_PORT}/postgres"
    else:
        raise ValueError(f"Unknown network protocol: {NETWORK_PROTOCOL}")

    return conn_str


def get_async_database_url() -> str:
    """Get async database URL from environment variables."""
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    NETWORK_PROTOCOL = os.getenv("NETWORK_PROTOCOL")

    if not all([DB_PASSWORD, DB_HOST, DB_PORT, NETWORK_PROTOCOL]):
        raise ValueError("One or more database environment variables are not set.")

    if NETWORK_PROTOCOL == "IPV4":
        conn_str = f"postgresql+asyncpg://postgres.{DB_HOST}:{DB_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:{DB_PORT}/postgres"
    elif NETWORK_PROTOCOL == "IPV6":
        conn_str = f"postgresql+asyncpg://postgres:{DB_PASSWORD}@db.{DB_HOST}.supabase.co:{DB_PORT}/postgres"
    else:
        raise ValueError(f"Unknown network protocol: {NETWORK_PROTOCOL}")

    return conn_str


### database init / reset ###


def init_db() -> Engine:
    """Initialize the database and create all tables."""
    engine = create_engine(get_database_url())
    Base.metadata.create_all(engine)
    return engine


def get_engine(async_engine: bool = False) -> Union[Engine, AsyncEngine]:
    """Get SQLAlchemy engine.

    Args:
        async_engine: If True, returns an AsyncEngine, otherwise returns a regular Engine
    """
    if async_engine:
        return create_async_engine(get_async_database_url())
    return create_engine(get_database_url())


def test_connection() -> bool:
    """Test the database connection.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"Database connection test: FAILED - {str(e)}")
        return False


async def test_async_connection() -> bool:
    """Test the async database connection.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    engine = get_engine(async_engine=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Async database connection test: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"Async database connection test: FAILED - {str(e)}")
        return False
    finally:
        # Explicitly dispose the engine to prevent event loop closed errors
        await engine.dispose()


@contextmanager
def get_db_session(engine: Optional[Engine] = None) -> Generator[Session, None, None]:
    """Get database session."""
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    engine = get_engine(async_engine=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


### write ###


def write(items: Iterable[DeclarativeMeta], batch_size: int = 1000) -> None:
    """
    Bulk upsert items in batches using Postgres' ON CONFLICT.
    - If row exists, update it (merge logic).
    - Otherwise, insert it.
    - Processes data in batches of `batch_size` (default: 1000 rows per commit).
    """

    items_list = list(items)
    if not items_list:
        logger.debug("No items to write.")
        return

    logger.debug(f"Processing {len(items_list)} items in batches of {batch_size}.")

    # Determine the model class (assumes all items belong to the same table)
    model_class = type(items_list[0])

    # Get primary and non-primary key columns
    pk_cols = [col.name for col in model_class.__table__.primary_key.columns]
    non_pk_cols = [
        c.name for c in model_class.__table__.columns if c.name not in pk_cols
    ]

    # Process in batches of `batch_size`
    for i in range(0, len(items_list), batch_size):
        batch = items_list[i : i + batch_size]
        logger.debug(f"Processing batch {i // batch_size + 1}: {len(batch)} rows.")

        # Convert batch items to dictionary format
        values_to_insert = [
            {col.name: getattr(obj, col.name) for col in model_class.__table__.columns}
            for obj in batch
        ]

        # Build Insert statement
        stmt = insert(model_class).values(values_to_insert)

        # Ensure there are columns to update
        if non_pk_cols:
            update_dict = {col: getattr(stmt.excluded, col) for col in non_pk_cols}
            stmt = stmt.on_conflict_do_update(index_elements=pk_cols, set_=update_dict)
        else:
            logger.info("No non-primary key columns to update. Performing insert-only.")

        # Execute batch operation
        with get_db_session() as session:
            try:
                session.execute(stmt)
                session.commit()
                logger.info(
                    f"Successfully upserted {len(batch)} items into {model_class.__tablename__}."
                )
            except Exception as e:
                logger.error(f"Error during batch upsert: {e}")
                session.rollback()
                break  # Stop processing if an error occurs

    logger.info(
        f"Completed upserting {len(items_list)} items into {model_class.__tablename__}."
    )


### read ###


def query_statement(table: str) -> str:
    """Get a comprehensive SQL query for the given table.

    This function generates a SELECT statement that includes all columns for the specified table.
    It uses SQLAlchemy's model registry to find the correct model class and generate the query.

    Args:
        table: Table name (use model.__tablename__)

    Returns:
        str: SQL SELECT statement for the table

    Raises:
        ValueError: If the table name is not found in the registered models
    """
    from sqlalchemy.orm.decl_api import DeclarativeMeta

    # Dynamically map table names to SQLAlchemy models
    def get_model(table_name: str) -> DeclarativeMeta:
        for model_class in Base.registry._class_registry.values():
            if (
                isinstance(model_class, DeclarativeMeta)
                and getattr(model_class, "__tablename__", None) == table_name
            ):
                return model_class
        raise ValueError(
            f"Table '{table_name}' not found in the registered models. "
            f"Available tables: {', '.join(sorted(m.__tablename__ for m in Base.registry._class_registry.values() if hasattr(m, '__tablename__')))}"
        )

    model = get_model(table)
    with get_db_session() as session:
        query = session.query(model).statement

    return str(query)


def read(query: str) -> pd.DataFrame:
    """Execute a SQL query and return results as a DataFrame."""
    with get_db_session() as session:
        return pd.read_sql(query, session.bind)


async def read_async(query: str) -> pd.DataFrame:
    """Execute a SQL query asynchronously and return results as a DataFrame.

    Note: This preserves the original data types from PostgreSQL, including datetime types.
    """
    engine = get_engine(async_engine=True)
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(query))
            # Convert to DataFrame before connection is closed
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            return df
    except Exception as e:
        logger.error(f"Database error executing query: {str(e)}")
        logger.error(f"Failed query: {query}")
        raise
    finally:
        # Explicitly dispose the engine to prevent event loop closed errors
        await engine.dispose()
