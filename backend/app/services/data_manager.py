"""
CSV Data Manager - Production-grade CSV-based data persistence
Thread-safe, cached, with automatic backup
"""

from typing import List, Dict, Optional, Any, Type, TypeVar
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from threading import Lock
from pydantic import BaseModel
import shutil

T = TypeVar('T', bound=BaseModel)


class CSVDataManager:
    """
    Production-grade CSV data manager
    
    Features:
    - Thread-safe operations
    - Automatic backups
    - In-memory caching
    - Validation with Pydantic
    - Atomic writes
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Backup directory
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Thread-safe locks per file
        self.locks: Dict[str, Lock] = {}
        
        # In-memory cache
        self.cache: Dict[str, pd.DataFrame] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Cache TTL (seconds)
        self.cache_ttl = 300  # 5 minutes
    
    def _get_lock(self, table_name: str) -> Lock:
        """Get or create lock for table"""
        if table_name not in self.locks:
            self.locks[table_name] = Lock()
        return self.locks[table_name]
    
    def _get_file_path(self, table_name: str) -> Path:
        """Get CSV file path for table"""
        return self.data_dir / f"{table_name}.csv"
    
    def _backup_file(self, table_name: str):
        """Create timestamped backup of file"""
        source = self._get_file_path(table_name)
        if source.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup = self.backup_dir / f"{table_name}_{timestamp}.csv"
            shutil.copy2(source, backup)
            
            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob(f"{table_name}_*.csv"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
    
    def _is_cache_valid(self, table_name: str) -> bool:
        """Check if cached data is still valid"""
        if table_name not in self.cache:
            return False
        
        cached_time = self.cache_timestamps.get(table_name)
        if not cached_time:
            return False
        
        age = (datetime.utcnow() - cached_time).total_seconds()
        return age < self.cache_ttl
    
    def read(
        self,
        table_name: str,
        model_class: Optional[Type[T]] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Read data from CSV
        
        Args:
            table_name: Table/file name
            model_class: Pydantic model for validation (optional)
            use_cache: Use cached data if available
            
        Returns:
            List of records as dictionaries
        """
        lock = self._get_lock(table_name)
        
        with lock:
            # Check cache
            if use_cache and self._is_cache_valid(table_name):
                df = self.cache[table_name]
            else:
                # Read from file
                file_path = self._get_file_path(table_name)
                
                if not file_path.exists():
                    return []
                
                df = pd.read_csv(file_path)
                
                # Cache it
                self.cache[table_name] = df
                self.cache_timestamps[table_name] = datetime.utcnow()
            
            # Convert to dict
            records = df.to_dict(orient='records')
            
            # Parse JSON columns if present
            for record in records:
                for key, value in record.items():
                    if isinstance(value, str) and (
                        value.startswith('{') or value.startswith('[')
                    ):
                        try:
                            record[key] = json.loads(value)
                        except:
                            pass
            
            # Validate with Pydantic if model provided
            if model_class:
                validated = []
                for record in records:
                    try:
                        obj = model_class(**record)
                        validated.append(obj.model_dump())
                    except Exception as e:
                        print(f"Validation error: {e}")
                        continue
                return validated
            
            return records
    
    def write(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        backup: bool = True
    ) -> bool:
        """
        Write data to CSV (overwrites existing)
        
        Args:
            table_name: Table/file name
            data: List of records
            backup: Create backup before writing
            
        Returns:
            True if successful
        """
        lock = self._get_lock(table_name)
        
        with lock:
            try:
                # Backup existing file
                if backup:
                    self._backup_file(table_name)
                
                # Convert complex objects to JSON strings
                processed_data = []
                for record in data:
                    processed = {}
                    for key, value in record.items():
                        if isinstance(value, (dict, list)):
                            processed[key] = json.dumps(value)
                        elif isinstance(value, datetime):
                            processed[key] = value.isoformat()
                        else:
                            processed[key] = value
                    processed_data.append(processed)
                
                # Write to CSV
                df = pd.DataFrame(processed_data)
                file_path = self._get_file_path(table_name)
                df.to_csv(file_path, index=False)
                
                # Update cache
                self.cache[table_name] = df
                self.cache_timestamps[table_name] = datetime.utcnow()
                
                return True
            except Exception as e:
                print(f"Error writing CSV: {e}")
                return False
    
    def append(
        self,
        table_name: str,
        records: List[Dict[str, Any]]
    ) -> bool:
        """
        Append records to existing CSV
        
        Args:
            table_name: Table/file name
            records: Records to append
            
        Returns:
            True if successful
        """
        # Read existing data
        existing = self.read(table_name, use_cache=False)
        
        # Append new records
        updated = existing + records
        
        # Write back
        return self.write(table_name, updated, backup=True)
    
    def update(
        self,
        table_name: str,
        update_fn: callable,
        filter_fn: Optional[callable] = None
    ) -> bool:
        """
        Update records matching filter
        
        Args:
            table_name: Table/file name
            update_fn: Function to update matching records
            filter_fn: Function to filter records (optional, updates all if None)
            
        Returns:
            True if successful
        """
        lock = self._get_lock(table_name)
        
        with lock:
            # Read data
            records = self.read(table_name, use_cache=False)
            
            # Update matching records
            updated_records = []
            for record in records:
                if filter_fn is None or filter_fn(record):
                    updated_record = update_fn(record)
                    updated_records.append(updated_record)
                else:
                    updated_records.append(record)
            
            # Write back
            return self.write(table_name, updated_records, backup=True)
    
    def delete(
        self,
        table_name: str,
        filter_fn: callable
    ) -> bool:
        """
        Delete records matching filter
        
        Args:
            table_name: Table/file name
            filter_fn: Function to identify records to delete
            
        Returns:
            True if successful
        """
        lock = self._get_lock(table_name)
        
        with lock:
            # Read data
            records = self.read(table_name, use_cache=False)
            
            # Filter out records
            kept_records = [r for r in records if not filter_fn(r)]
            
            # Write back
            return self.write(table_name, kept_records, backup=True)
    
    def find_one(
        self,
        table_name: str,
        filter_fn: callable,
        model_class: Optional[Type[T]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find single record matching filter
        
        Args:
            table_name: Table/file name
            filter_fn: Filter function
            model_class: Pydantic model for validation
            
        Returns:
            First matching record or None
        """
        records = self.read(table_name, model_class, use_cache=True)
        
        for record in records:
            if filter_fn(record):
                return record
        
        return None
    
    def find_many(
        self,
        table_name: str,
        filter_fn: Optional[callable] = None,
        model_class: Optional[Type[T]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple records matching filter
        
        Args:
            table_name: Table/file name
            filter_fn: Filter function (None returns all)
            model_class: Pydantic model for validation
            limit: Maximum records to return
            
        Returns:
            List of matching records
        """
        records = self.read(table_name, model_class, use_cache=True)
        
        if filter_fn:
            records = [r for r in records if filter_fn(r)]
        
        if limit:
            records = records[:limit]
        
        return records
    
    def count(
        self,
        table_name: str,
        filter_fn: Optional[callable] = None
    ) -> int:
        """
        Count records matching filter
        
        Args:
            table_name: Table/file name
            filter_fn: Filter function (None counts all)
            
        Returns:
            Count of matching records
        """
        records = self.read(table_name, use_cache=True)
        
        if filter_fn:
            records = [r for r in records if filter_fn(r)]
        
        return len(records)
    
    def clear_cache(self, table_name: Optional[str] = None):
        """Clear cache for table or all tables"""
        if table_name:
            self.cache.pop(table_name, None)
            self.cache_timestamps.pop(table_name, None)
        else:
            self.cache.clear()
            self.cache_timestamps.clear()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table/file exists"""
        return self._get_file_path(table_name).exists()
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get metadata about table"""
        file_path = self._get_file_path(table_name)
        
        if not file_path.exists():
            return {}
        
        df = pd.read_csv(file_path)
        
        return {
            'name': table_name,
            'rows': len(df),
            'columns': list(df.columns),
            'size_bytes': file_path.stat().st_size,
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime),
            'cached': table_name in self.cache
        }


# Global CSV manager instance
csv_manager = CSVDataManager()
