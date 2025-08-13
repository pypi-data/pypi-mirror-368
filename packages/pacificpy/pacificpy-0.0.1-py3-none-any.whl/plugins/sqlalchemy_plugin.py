"""
SQLAlchemy plugin for PacificPy.

This module provides a plugin for integrating SQLAlchemy with PacificPy,
supporting both sync and async engines, session makers, and lifecycle hooks.
"""

import os
from typing import Any, AsyncGenerator, Generator, Optional
from contextlib import contextmanager, asynccontextmanager

# Try to import SQLAlchemy
try:
    from sqlalchemy import create_engine, event, text
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.engine import Engine
    from sqlalchemy.ext.asyncio.engine import AsyncEngine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

from ...di import Dependency

class SQLAlchemyPlugin:
    """Plugin for SQLAlchemy integration."""
    
    def __init__(
        self,
        database_url: str = None,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        async_mode: bool = False,
    ):
        """
        Initialize the SQLAlchemy plugin.
        
        Args:
            database_url: The database URL
            echo: Whether to echo SQL statements
            pool_size: The size of the connection pool
            max_overflow: The maximum overflow of the connection pool
            async_mode: Whether to use async mode
        """
        if not SQLALCHEMY_AVAILABLE:
            raise RuntimeError("SQLAlchemy is required for SQLAlchemyPlugin")
        
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.async_mode = async_mode
        
        # Engine and session maker
        self.engine: Optional[Engine] = None
        self.async_engine: Optional[AsyncEngine] = None
        self.session_maker: Optional[sessionmaker] = None
        self.async_session_maker: Optional[async_sessionmaker] = None
    
    def setup(self) -> None:
        """Set up the SQLAlchemy plugin."""
        if self.async_mode:
            self._setup_async()
        else:
            self._setup_sync()
    
    def _setup_sync(self) -> None:
        """Set up sync SQLAlchemy components."""
        # Create engine
        self.engine = create_engine(
            self.database_url,
            echo=self.echo,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
        )
        
        # Create session maker
        self.session_maker = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )
    
    def _setup_async(self) -> None:
        """Set up async SQLAlchemy components."""
        # Create async engine
        self.async_engine = create_async_engine(
            self.database_url,
            echo=self.echo,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
        )
        
        # Create async session maker
        self.async_session_maker = async_sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
    
    def get_db(self) -> Generator[Session, None, None]:
        """
        Get a database session (sync).
        
        Yields:
            A database session
        """
        if not self.session_maker:
            raise RuntimeError("SQLAlchemy plugin not set up for sync mode")
        
        session = self.session_maker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def get_async_db(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async database session.
        
        Yields:
            An async database session
        """
        if not self.async_session_maker:
            raise RuntimeError("SQLAlchemy plugin not set up for async mode")
        
        session = self.async_session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    @contextmanager
    def get_sync_session(self) -> Generator[Session, None, None]:
        """
        Get a sync database session as a context manager.
        
        Yields:
            A database session
        """
        if not self.session_maker:
            raise RuntimeError("SQLAlchemy plugin not set up for sync mode")
        
        session = self.session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async database session as an async context manager.
        
        Yields:
            An async database session
        """
        if not self.async_session_maker:
            raise RuntimeError("SQLAlchemy plugin not set up for async mode")
        
        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def connect(self) -> None:
        """Connect to the database."""
        if self.async_mode and self.async_engine:
            # For async engines, connection is managed by the engine
            pass
        elif not self.async_mode and self.engine:
            # For sync engines, test the connection
            try:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            except Exception as e:
                raise RuntimeError(f"Failed to connect to database: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.async_mode and self.async_engine:
            await self.async_engine.dispose()
        elif not self.async_mode and self.engine:
            self.engine.dispose()
    
    def get_dependency(self, async_mode: bool = False) -> Dependency:
        """
        Get a dependency for database sessions.
        
        Args:
            async_mode: Whether to return an async dependency
            
        Returns:
            A Dependency instance
        """
        if async_mode:
            return Dependency(self.get_async_db)
        else:
            return Dependency(self.get_db)

# Global SQLAlchemy plugin instance
_sqlalchemy_plugin: Optional[SQLAlchemyPlugin] = None

def configure_sqlalchemy(
    database_url: str = None,
    echo: bool = False,
    pool_size: int = 10,
    max_overflow: int = 20,
    async_mode: bool = False,
) -> SQLAlchemyPlugin:
    """
    Configure the global SQLAlchemy plugin.
    
    Args:
        database_url: The database URL
        echo: Whether to echo SQL statements
        pool_size: The size of the connection pool
        max_overflow: The maximum overflow of the connection pool
        async_mode: Whether to use async mode
        
    Returns:
        The SQLAlchemy plugin instance
    """
    global _sqlalchemy_plugin
    _sqlalchemy_plugin = SQLAlchemyPlugin(
        database_url=database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        async_mode=async_mode,
    )
    _sqlalchemy_plugin.setup()
    return _sqlalchemy_plugin

def get_db() -> Generator[Session, None, None]:
    """
    Get a database session using the global plugin.
    
    Yields:
        A database session
        
    Raises:
        RuntimeError: If SQLAlchemy plugin is not configured
    """
    if not _sqlalchemy_plugin:
        raise RuntimeError("SQLAlchemy plugin not configured")
    
    yield from _sqlalchemy_plugin.get_db()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session using the global plugin.
    
    Yields:
        An async database session
        
    Raises:
        RuntimeError: If SQLAlchemy plugin is not configured
    """
    if not _sqlalchemy_plugin:
        raise RuntimeError("SQLAlchemy plugin not configured")
    
    async for session in _sqlalchemy_plugin.get_async_db():
        yield session

# Example usage:
"""
# In your app setup:
configure_sqlalchemy(
    database_url="postgresql+asyncpg://user:password@localhost/dbname",
    async_mode=True
)

# In your routes:
@app.get("/users")
async def get_users(async_db = Depends(get_async_db)):
    result = await async_db.execute(select(User))
    return result.scalars().all()
"""