"""Base DAO class for common database operations"""
from typing import Optional, List, Dict, Any, TypeVar, Generic, Type
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar('T')


class BaseDAO(Generic[T]):
    """Base Data Access Object with common operations"""
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactions"""
        async with self.session.begin():
            yield self.session
    
    async def commit(self):
        """Commit current transaction"""
        await self.session.commit()
    
    async def rollback(self):
        """Rollback current transaction"""
        await self.session.rollback()
    
    async def refresh(self, instance: T):
        """Refresh instance from database"""
        await self.session.refresh(instance)
    
    async def add(self, instance: T) -> T:
        """Add instance to session"""
        self.session.add(instance)
        return instance
    
    async def add_all(self, instances: List[T]) -> List[T]:
        """Add multiple instances to session"""
        self.session.add_all(instances)
        return instances
    
    async def flush(self):
        """Flush pending changes"""
        await self.session.flush()
    
    def handle_error(self, error: Exception, context: str = ""):
        """Handle database errors consistently"""
        error_msg = f"Database error in {self.__class__.__name__}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"
        
        # Log error here if logger is available
        # logger.error(error_msg, exc_info=True)
        
        # Re-raise as generic Exception to avoid parameter issues
        raise Exception(error_msg) from error