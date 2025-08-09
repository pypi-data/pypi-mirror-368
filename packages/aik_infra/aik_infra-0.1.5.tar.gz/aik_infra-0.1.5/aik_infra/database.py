"""
async database configuration and repository base classes
Implements Repository pattern for clean architecture using async SQLAlchemy with asyncpg
"""

import os
import random
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, delete, update, text, Executable, inspect
from sqlalchemy.sql.dml import Update, Delete, Insert

# Type variables for generic repository
T = TypeVar('T')
ID = TypeVar('ID')

# Base class for all models
Base = declarative_base()

# 🔧 Global engines and session factory for connection pooling
_engines = None
_session_factory = None

def get_database_urls() -> (str, List[str]):
    """Get database URLs for write and read replicas from environment variables."""
    write_url = os.getenv("DATABASE_URL")
    if not write_url:
        raise ValueError("DATABASE_URL environment variable is not set.")

    read_urls_str = os.getenv("READ_REPLICA_URLS")
    read_urls = [url.strip() for url in read_urls_str.split(',')] if read_urls_str else []
    
    return write_url, read_urls

def _create_engine_internal(database_url: str, app_name_suffix: str = ""):
    """Internal function to create an async engine."""
    is_sqlite = "sqlite" in database_url.lower()
    app_name = os.getenv("APP_NAME", "unknown_service")
    if app_name_suffix:
        app_name = f"{app_name}{app_name_suffix}"

    if is_sqlite:
        return create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
    else:
        return create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            connect_args={
                "server_settings": {
                    "application_name": app_name
                }
            }
        )

def get_engines() -> Dict[str, Any]:
    """Get global async engines for read and write."""
    global _engines
    if _engines is None:
        write_url, read_urls = get_database_urls()
        
        write_engine = _create_engine_internal(write_url, app_name_suffix="_writer")
        
        if read_urls:
            read_engines = [_create_engine_internal(url, app_name_suffix=f"_reader_{i}") for i, url in enumerate(read_urls)]
        else:
            # If no read replicas are configured, use the write engine for reads as a fallback.
            read_engines = [write_engine]
            
        _engines = {
            'write': write_engine,
            'read': read_engines
        }
    return _engines

class RoutingAsyncSession(AsyncSession):
    """
    A custom AsyncSession that routes queries to read or write replicas.
    - Write queries (INSERT, UPDATE, DELETE) go to the 'write' engine.
    - Queries within a transaction go to the 'write' engine.
    - Read queries (SELECT) go to a randomly chosen 'read' engine.
    """
    def get_bind(self, mapper=None, clause=None, **kw):
        engines = get_engines()
        
        # If inside a transaction, always use the write database to ensure consistency.
        if self.in_transaction() or self.in_nested_transaction():
            return engines['write']

        # If the statement is a write operation, use the write database.
        if isinstance(clause, (Insert, Update, Delete)):
            return engines['write']
            
        # For SELECT statements, use a read replica.
        if isinstance(clause, (Executable)):
             # A simple heuristic to check for SELECT statements.
            if clause.is_select:
                return random.choice(engines['read'])

        # Fallback to the write engine for any other case.
        return engines['write']


def get_session_factory():
    """Get global session factory that uses the routing session."""
    global _session_factory
    if _session_factory is None:
        engines = get_engines()
        _session_factory = async_sessionmaker(
            class_=RoutingAsyncSession,
            bind=engines['write'],
            expire_on_commit=False
        )
    return _session_factory

async def dispose_engine():
    """Dispose of all global engines."""
    global _engines
    if _engines:
        await _engines['write'].dispose()
        for engine in _engines['read']:
            await engine.dispose()
        _engines = None

def get_session() -> AsyncSession:
    """Get a new session from the global pool"""
    return get_session_factory()()

@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Get async context-managed session from the global pool"""
    async with get_session_factory()() as session:
        yield session


class AsyncDatabaseConfig:
    """Async database configuration - now uses global engines"""

    def __init__(self, base=None):
        self.base = base or Base
        # We rely on the global engines, but can get one for operations like create_tables
        self.engine = get_engines()['write'] 
        self.async_session_factory = get_session_factory()

    def get_session(self) -> AsyncSession:
        """Return a new async session from the global pool"""
        return self.async_session_factory()

    @asynccontextmanager
    async def get_session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """Return async context-managed session from the global pool"""
        async with self.async_session_factory() as session:
            yield session

    async def create_schema(self, schema_name: str):
        """Create schema if it does not exist"""
        async with self.engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    async def create_tables(self):
        """Create all tables (run manually from startup) on the write replica"""
        # If the base has a schema, create it.
        schema = getattr(self.base.metadata, "schema", None)
        if schema:
            await self.create_schema(schema)
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

    async def drop_tables(self):
        """Drop all tables (for testing) from the write replica"""
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.drop_all)

    async def dispose(self):
        """Dispose of the engine - now calls global dispose"""
        await dispose_engine()


class AsyncBaseRepository(Generic[T, ID], ABC):
    """
    Async base repository implementing basic CRUD operations
    """

    def __init__(self, session: AsyncSession, model_class: type):
        self.session = session
        self.model_class = model_class

    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        pass

    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        pass

    @abstractmethod
    async def exists(self, entity_id: ID) -> bool:
        pass


class AsyncSQLAlchemyRepository(AsyncBaseRepository[T, ID]):
    """
    Concrete async implementation using SQLAlchemy
    """

    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        result = await self.session.get(self.model_class, entity_id)
        return result

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        stmt = select(self.model_class).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.session.merge(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity_id: ID) -> bool:
        obj = await self.get_by_id(entity_id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False

    async def exists(self, entity_id: ID) -> bool:
        stmt = select(self.model_class).where(self.model_class.id == entity_id)
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def filter_by(self, **kwargs) -> List[T]:
        stmt = select(self.model_class).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by(self, criteria: Dict[str, Any]) -> List[T]:
        stmt = select(self.model_class)
        for key, value in criteria.items():
            if hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Get total count of entities"""
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())


class AsyncUnitOfWork:
    """
    Async Unit of Work for transactional consistency
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        elif not self._committed:
            await self.rollback()

    async def commit(self):
        await self.session.commit()
        self._committed = True

    async def rollback(self):
        await self.session.rollback()

    async def flush(self):
        await self.session.flush()


# 🔧 Instantiate config - now simplified
def get_db_config(base=None) -> AsyncDatabaseConfig:
    return AsyncDatabaseConfig(base)


# 📦 FastAPI dependency - now uses global session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_context() as session:
        yield session
