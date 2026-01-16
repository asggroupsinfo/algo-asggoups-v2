"""
Database Interface for Plugins - Plan 09: Database Isolation

Defines how plugins interact with their isolated databases.
Each plugin has its own database to prevent data conflicts.

Version: 1.0.0
Date: 2026-01-15
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DatabaseConfig:
    """Configuration for a plugin database"""
    plugin_id: str
    db_path: str
    schema_version: str
    tables: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'plugin_id': self.plugin_id,
            'db_path': self.db_path,
            'schema_version': self.schema_version,
            'tables': self.tables
        }


@dataclass
class MigrationResult:
    """Result of a database migration"""
    success: bool
    records_migrated: int = 0
    records_failed: int = 0
    source_count: int = 0
    target_count: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def data_loss(self) -> bool:
        """Check if any data was lost during migration"""
        return self.source_count != self.target_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'records_migrated': self.records_migrated,
            'records_failed': self.records_failed,
            'source_count': self.source_count,
            'target_count': self.target_count,
            'data_loss': self.data_loss,
            'errors': self.errors,
            'timestamp': self.timestamp.isoformat()
        }


class IDatabaseCapable(ABC):
    """
    Interface for plugins that use databases.
    
    Plugins implementing this interface can:
    - Have their own isolated database
    - Execute queries on their database
    - Insert/update records
    - Participate in cross-plugin aggregation
    """
    
    @abstractmethod
    def get_database_config(self) -> DatabaseConfig:
        """
        Get database configuration for this plugin.
        
        Returns:
            DatabaseConfig with plugin's database settings
        """
        pass
    
    @abstractmethod
    async def initialize_database(self) -> bool:
        """
        Initialize plugin's database with schema.
        
        Creates tables and indexes if they don't exist.
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Execute a query on plugin's database.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        pass
    
    @abstractmethod
    async def insert_record(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert a record into plugin's database.
        
        Args:
            table: Table name
            data: Record data as dictionary
            
        Returns:
            ID of inserted record
        """
        pass
    
    @abstractmethod
    async def update_record(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        Update records in plugin's database.
        
        Args:
            table: Table name
            data: Fields to update
            where: Conditions for update
            
        Returns:
            Number of records updated
        """
        pass


class IDatabaseMigration(ABC):
    """Interface for database migration operations"""
    
    @abstractmethod
    def migrate(self, dry_run: bool = True) -> MigrationResult:
        """
        Migrate data from source to target.
        
        Args:
            dry_run: If True, only simulate migration
            
        Returns:
            MigrationResult with migration details
        """
        pass
    
    @abstractmethod
    def verify(self) -> MigrationResult:
        """
        Verify migration was successful.
        
        Returns:
            MigrationResult with verification details
        """
        pass
    
    @abstractmethod
    def rollback(self) -> bool:
        """
        Rollback migration if possible.
        
        Returns:
            True if rollback successful
        """
        pass
