import json
import os
import time
from uuid import uuid4
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from copy import deepcopy
import gzip
import shutil
import logging
from pathlib import Path


class Database:
    """
    A lightweight JSON-based database with schema support, transactions, and backup functionality.
    
    Features:
    - Automatic schema migration
    - Transaction support
    - Backup and restore
    - Data validation
    - Indexing
    - Querying
    - Table operations
    
    Args:
        name (str): Database name (default: "database")
        autocommit (bool): Enable auto-commit (default: True)
        schema_version (str): Schema version (default: "2.0")
        backup_count (int): Number of backups to keep (default: 5)
        log_queries (bool): Log database operations (default: False)
    """
    
    def __init__(
        self,
        name: str = "database",
        autocommit: bool = True,
        schema_version: str = "2.0",
        backup_count: int = 5,
        log_queries: bool = False
    ):
        self.name = name
        self.file_path = f"{name}.json"
        self.backup_dir = f"{name}_backups"
        self.autocommit = autocommit
        self.schema_version = schema_version
        self.backup_count = backup_count
        self.log_queries = log_queries
        self.transaction_stack = []
        self._setup_logging()
        self._ensure_backup_dir()
        self.data = self._load_database()
        self._initialize_metadata()
        self._migrate_schema()

    def _setup_logging(self) -> None:
        """Configure logging for the database"""
        self.logger = logging.getLogger(f"Database_{self.name}")
        self.logger.setLevel(logging.DEBUG if self.log_queries else logging.ERROR)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def _ensure_backup_dir(self) -> None:
        """Ensure backup directory exists"""
        os.makedirs(self.backup_dir, exist_ok=True)

    def _load_database(self) -> Dict:
        """Load database from file or create new if doesn't exist"""
        default_structure = {
            "tables": {},
            "indexes": {},
            "schemas": {},
            "_metadata": {
                "version": self.schema_version,
                "created_at": time.time(),
                "last_modified": time.time(),
                "schema_version": self.schema_version,
                "schema_history": [],
                "edit_count": 0,
                "backups": []
            }
        }

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if not isinstance(data.get("tables"), dict):
                        raise ValueError("Invalid database structure: 'tables' must be a dictionary")
                    
                    for key in default_structure:
                        if key not in data:
                            data[key] = default_structure[key]
                    
                    return data
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.error(f"Error loading database: {str(e)}. Attempting to restore from backup.")
                return self._restore_latest_backup() or default_structure
        return default_structure

    def _initialize_metadata(self) -> None:
        """Initialize metadata if not present"""
        if "_metadata" not in self.data:
            self.data["_metadata"] = {
                "version": self.schema_version,
                "created_at": time.time(),
                "last_modified": time.time(),
                "schema_version": self.schema_version,
                "schema_history": [],
                "edit_count": 0,
                "backups": []
            }
        else:
            defaults = {
                "edit_count": 0,
                "schema_history": [],
                "backups": []
            }
            for key, value in defaults.items():
                if key not in self.data["_metadata"]:
                    self.data["_metadata"][key] = value
            
            self.data["_metadata"].update({
                "last_modified": time.time(),
                "schema_version": self.schema_version
            })
        self._commit()

    def _migrate_schema(self) -> None:
        """Migrate database schema if needed"""
        current_version = self.data["_metadata"].get("schema_version", "1.0")
        if current_version == self.schema_version:
            return

        self.logger.info(f"Migrating schema from {current_version} to {self.schema_version}")
        
        self.data["_metadata"]["schema_history"].append({
            "from_version": current_version,
            "to_version": self.schema_version,
            "timestamp": time.time(),
            "tables_affected": list(self.data["tables"].keys())
        })

        for table_name in self.data["tables"]:
            if table_name not in self.data["schemas"]:
                self.data["schemas"][table_name] = {
                    "fields": self._infer_schema(table_name),
                    "version": "1.0",
                    "created_at": time.time(),
                    "last_modified": time.time()
                }

        self.data["_metadata"]["schema_version"] = self.schema_version
        self._commit()

    def _infer_schema(self, table_name: str) -> Dict:
        """Infer schema from existing table data"""
        table_data = self.data["tables"].get(table_name, {})
        schema = {
            "type": "dict" if isinstance(table_data, dict) else "list",
            "fields": {}
        }

        sample_items = []
        if isinstance(table_data, list):
            sample_items = table_data[:10]
        elif isinstance(table_data, dict):
            sample_items = list(table_data.values())[:10]

        for item in sample_items:
            if isinstance(item, dict):
                for key, value in item.items():
                    if key not in schema["fields"]:
                        schema["fields"][key] = {
                            "type": type(value).__name__,
                            "required": False,
                            "default": None
                        }

        return schema

    def _commit(self) -> None:
        """Commit changes to disk"""
        if self.autocommit and not self.transaction_stack:
            try:
                self.data["_metadata"]["last_modified"] = time.time()
                self.data["_metadata"]["edit_count"] += 1
                self._create_backup()
                temp_path = f"{self.file_path}.tmp"
                with open(temp_path, 'w', encoding='utf-8') as file:
                    json.dump(self.data, file, indent=4, ensure_ascii=False)
                os.replace(temp_path, self.file_path)
                
                self.logger.debug("Database committed successfully")
            except Exception as e:
                self.logger.error(f"Failed to commit database: {str(e)}")
                raise

    def _create_backup(self) -> bool:
        """Create a compressed backup of the database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"{self.name}_{timestamp}.json.gz")
            
            with open(self.file_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            self.data["_metadata"]["backups"].append({
                "path": backup_path,
                "timestamp": time.time(),
                "size": os.path.getsize(backup_path)
            })
            
            self._rotate_backups()
            
            self.logger.info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            return False

    def _rotate_backups(self) -> None:
        """Rotate backups to maintain backup_count"""
        try:
            backups = sorted(
                Path(self.backup_dir).glob(f"{self.name}_*.json.gz"),
                key=os.path.getmtime,
                reverse=True
            )
            
            for old_backup in backups[self.backup_count:]:
                try:
                    os.remove(old_backup)
                    self.logger.info(f"Rotated old backup: {old_backup}")
                except Exception as e:
                    self.logger.error(f"Failed to rotate backup {old_backup}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Backup rotation failed: {str(e)}")

    def _restore_latest_backup(self) -> Optional[Dict]:
        """Restore from the latest backup"""
        try:
            backups = sorted(
                Path(self.backup_dir).glob(f"{self.name}_*.json.gz"),
                key=os.path.getmtime,
                reverse=True
            )
            
            if backups:
                latest_backup = backups[0]
                with gzip.open(latest_backup, 'rb') as f_in:
                    data = json.load(f_in)
                    self.logger.info(f"Restored from backup: {latest_backup}")
                    return data
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {str(e)}")
        return None

    def backup(self, backup_name: str) -> bool:
        """Create a named backup"""
        try:
            backup_path = os.path.join(self.backup_dir, f"{self.name}_{backup_name}.json")
            with open(backup_path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
            
            self.data["_metadata"]["backups"].append({
                "path": backup_path,
                "timestamp": time.time(),
                "size": os.path.getsize(backup_path),
                "type": "manual"
            })
            
            self._commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to create named backup: {str(e)}")
            return False

    def restore_backup(self, backup_path: Optional[str] = None) -> bool:
        """Restore database from backup"""
        try:
            if backup_path is None:
                restored_data = self._restore_latest_backup()
                if restored_data:
                    self.data = restored_data
                    return True
                return False
            else:
                if backup_path.endswith('.gz'):
                    with gzip.open(backup_path, 'rb') as file:
                        self.data = json.load(file)
                else:
                    with open(backup_path, 'r', encoding='utf-8') as file:
                        self.data = json.load(file)
                
                self._commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {str(e)}")
            return False

    def begin_transaction(self) -> None:
        """Begin a database transaction"""
        self.transaction_stack.append(deepcopy(self.data))
        self.logger.debug("Transaction started")

    def commit_transaction(self) -> None:
        """Commit the current transaction"""
        if self.transaction_stack:
            self.transaction_stack.pop()
            self._commit()
            self.logger.debug("Transaction committed")

    def rollback_transaction(self) -> None:
        """Rollback the current transaction"""
        if self.transaction_stack:
            self.data = self.transaction_stack.pop()
            self.logger.debug("Transaction rolled back")

    def create_table(self, table_name: str, schema: Optional[Dict] = None) -> bool:
        """Create a new table with optional schema"""
        if table_name in self.data["tables"]:
            self.logger.warning(f"Table {table_name} already exists")
            return False
            
        if schema is None:
            schema = {
                "type": "list",
                "fields": {},
                "version": "1.0",
                "created_at": time.time(),
                "last_modified": time.time()
            }
        
        table_type = schema.get("type", "list")
        self.data["tables"][table_name] = [] if table_type == "list" else {}
        self.data["schemas"][table_name] = schema
        self._commit()
        self.logger.info(f"Created table {table_name}")
        return True

    def delete_table(self, table_name: str) -> bool:
        """Delete a table and all its data"""
        if table_name not in self.data["tables"]:
            self.logger.warning(f"Table {table_name} not found")
            return False
            
        del self.data["tables"][table_name]
        
        if table_name in self.data["schemas"]:
            del self.data["schemas"][table_name]
        
        for index_name in list(self.data["indexes"].keys()):
            if index_name.startswith(f"{table_name}."):
                del self.data["indexes"][index_name]
        
        self._commit()
        self.logger.info(f"Deleted table {table_name}")
        return True

    def update_table_schema(self, table_name: str, new_schema: Dict) -> bool:
        """Update a table's schema and migrate existing data"""
        if table_name not in self.data["tables"]:
            self.logger.warning(f"Table {table_name} not found")
            return False
            
        current_schema = self.data["schemas"].get(table_name, {})
        new_schema["version"] = str(float(current_schema.get("version", "1.0")) + 0.1)
        new_schema["last_modified"] = time.time()
        
        self._migrate_table_data(table_name, current_schema, new_schema)
        self.data["schemas"][table_name] = new_schema
        self._commit()
        self.logger.info(f"Updated schema for table {table_name}")
        return True

    def _migrate_table_data(self, table_name: str, old_schema: Dict, new_schema: Dict) -> None:
        """Migrate table data according to schema changes"""
        table_data = self.data["tables"][table_name]
        old_fields = old_schema.get("fields", {})
        new_fields = new_schema.get("fields", {})
        
        if isinstance(table_data, list):
            for i, item in enumerate(table_data):
                if isinstance(item, dict):
                    table_data[i] = self._migrate_item(item, old_fields, new_fields)
        elif isinstance(table_data, dict):
            for key, item in table_data.items():
                if isinstance(item, dict):
                    table_data[key] = self._migrate_item(item, old_fields, new_fields)

    def _migrate_item(self, item: Dict, old_fields: Dict, new_fields: Dict) -> Dict:
        """Migrate a single item according to schema changes"""
        migrated_item = item.copy()
        for field, field_info in new_fields.items():
            if field not in migrated_item:
                if "default" in field_info:
                    migrated_item[field] = field_info["default"]
                elif field_info.get("required", False):
                    migrated_item[field] = self._get_default_value(field_info["type"])
        for field in list(migrated_item.keys()):
            if field not in new_fields and field not in old_fields:
                del migrated_item[field]
        
        return migrated_item

    def _validate_value(self, value: Any, schema: Dict) -> bool:
        """Validate a value against its schema"""
        type_str = schema["type"]
        
        if type_str == "str":
            return isinstance(value, str)
        elif type_str == "int":
            return isinstance(value, int)
        elif type_str == "float":
            return isinstance(value, float)
        elif type_str == "bool":
            return isinstance(value, bool)
        elif type_str == "list":
            if not isinstance(value, list):
                return False
            item_schema = schema.get("item_schema")
            if item_schema is None:
                return True
            return all(self._validate_value(item, item_schema) for item in value)
        elif type_str == "dict":
            if not isinstance(value, dict):
                return False
            fields = schema.get("fields", {})
            for field, field_schema in fields.items():
                if field_schema.get("required", False) and field not in value:
                    return False
                if field in value and not self._validate_value(value[field], field_schema):
                    return False
            return True
        return False

    def _validate_item(self, item: Dict, fields: Dict) -> Dict:
        """Validate an item against its schema"""
        validated_item = {}
        for field, field_schema in fields.items():
            if field in item:
                if self._validate_value(item[field], field_schema):
                    validated_item[field] = item[field]
                else:
                    raise ValueError(f"Invalid value for field {field}: expected {field_schema['type']}")
            else:
                if field_schema.get("required", False) or "default" in field_schema:
                    default = field_schema.get("default", self._get_default_value(field_schema["type"]))
                    validated_item[field] = default
        return validated_item

    def _get_default_value(self, type_str: str) -> Any:
        """Get default value for a type"""
        defaults = {
            "str": "",
            "int": 0,
            "float": 0.0,
            "bool": False,
            "list": [],
            "dict": {}
        }
        return defaults.get(type_str, None)

    def insert(self, table_name: str, data: Any, path: Optional[str] = None) -> bool:
        """Insert data into a table"""
        if table_name not in self.data["tables"]:
            self.logger.warning(f"Table {table_name} not found")
            return False
            
        schema = self.data["schemas"].get(table_name, self._infer_schema(table_name))
        table_type = schema.get("type", "list")
        
        if not path:
            if table_type == "list":
                if isinstance(data, dict):
                    data = self._validate_item(data, schema.get("fields", {}))
                self.data["tables"][table_name].append(data)
                self._commit()
                self.logger.debug(f"Inserted item into list table {table_name}")
                return True
            elif table_type == "dict":
                if isinstance(data, dict):
                    if "id" not in data:
                        data = data.copy()
                        data["id"] = str(uuid4())
                    try:
                        data = self._validate_item(data, schema.get("fields", {}))
                        self.data["tables"][table_name][data["id"]] = data
                        self._commit()
                        self.logger.debug(f"Inserted item into dict table {table_name} with ID {data['id']}")
                        return True
                    except KeyError as e:
                        self.logger.error(f"Missing required field: {str(e)}")
                        return False
                return False

        path_parts = path.split('.')
        current = self.data["tables"][table_name]
        
        for part in path_parts[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    return False
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    if index < len(current):
                        current = current[index]
                    else:
                        return False
                except ValueError:
                    return False
            else:
                return False
        
        final_part = path_parts[-1]
        if isinstance(current, dict):
            if isinstance(data, dict):
                data = self._validate_item(data, schema.get("fields", {}))
            current[final_part] = data
            self._commit()
            return True
        elif isinstance(current, list):
            try:
                index = int(final_part)
                if index < len(current):
                    if isinstance(data, dict):
                        data = self._validate_item(data, schema.get("fields", {}))
                    current[index] = data
                    self._commit()
                    return True
            except ValueError:
                pass
        return False

    def get(self, table_name: str, path: Optional[str] = None, default: Any = None) -> Any:
        """Get data from a table"""
        if table_name not in self.data["tables"]:
            self.logger.debug(f"Table {table_name} not found")
            return default
            
        if not path:
            return deepcopy(self.data["tables"][table_name])
            
        try:
            path_parts = path.split('.')
            current = self.data["tables"][table_name]
            
            for part in path_parts:
                if isinstance(current, dict):
                    current = current.get(part, default)
                    if current is default:
                        return default
                elif isinstance(current, list):
                    try:
                        index = int(part)
                        current = current[index] if index < len(current) else default
                    except (ValueError, IndexError):
                        return default
                else:
                    return default
                    
            return deepcopy(current)
        except Exception as e:
            self.logger.error(f"Error getting data: {str(e)}")
            return default

    def update(self, table_name: str, new_data: Any, path: Optional[str] = None) -> bool:
        """Update data in a table"""
        if table_name not in self.data["tables"]:
            self.logger.warning(f"Table {table_name} not found")
            return False
            
        schema = self.data["schemas"].get(table_name, self._infer_schema(table_name))
        
        if not path:
            if isinstance(new_data, dict):
                new_data = self._validate_item(new_data, schema.get("fields", {}))
            self.data["tables"][table_name] = new_data
            self._commit()
            return True
            
        path_parts = path.split('.')
        current = self.data["tables"][table_name]
        
        for part in path_parts[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    return False
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    if index < len(current):
                        current = current[index]
                    else:
                        return False
                except ValueError:
                    return False
            else:
                return False
                
        final_part = path_parts[-1]
        if isinstance(current, dict):
            if isinstance(new_data, dict):
                new_data = self._validate_item(new_data, schema.get("fields", {}))
            current[final_part] = new_data
            self._commit()
            return True
        elif isinstance(current, list):
            try:
                index = int(final_part)
                if index < len(current):
                    if isinstance(new_data, dict):
                        new_data = self._validate_item(new_data, schema.get("fields", {}))
                    current[index] = new_data
                    self._commit()
                    return True
            except ValueError:
                pass
        return False

    def delete(self, table_name: str, path: Optional[str] = None) -> bool:
        """Delete data from a table"""
        if table_name not in self.data["tables"]:
            self.logger.warning(f"Table {table_name} not found")
            return False
            
        if not path:
            self.data["tables"][table_name] = [] if isinstance(self.data["tables"][table_name], list) else {}
            self._commit()
            return True
            
        path_parts = path.split('.')
        current = self.data["tables"][table_name]
        
        for part in path_parts[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    return False
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    if index < len(current):
                        current = current[index]
                    else:
                        return False
                except ValueError:
                    return False
            else:
                return False
                
        final_part = path_parts[-1]
        if isinstance(current, dict):
            if final_part in current:
                del current[final_part]
                self._commit()
                return True
        elif isinstance(current, list):
            try:
                index = int(final_part)
                if index < len(current):
                    del current[index]
                    self._commit()
                    return True
            except ValueError:
                pass
        return False

    def create_index(self, table_name: str, field: str) -> bool:
        """Create an index on a table field"""
        if table_name not in self.data["tables"]:
            self.logger.warning(f"Table {table_name} not found")
            return False
            
        index_name = f"{table_name}.{field}"
        if index_name in self.data["indexes"]:
            self.logger.debug(f"Index {index_name} already exists")
            return True
            
        table_data = self.data["tables"][table_name]
        index = {}
        
        if isinstance(table_data, list):
            for i, item in enumerate(table_data):
                if isinstance(item, dict) and field in item:
                    value = item[field]
                    if value not in index:
                        index[value] = []
                    index[value].append(i)
        elif isinstance(table_data, dict):
            for key, item in table_data.items():
                if isinstance(item, dict) and field in item:
                    value = item[field]
                    if value not in index:
                        index[value] = []
                    index[value].append(key)
        
        self.data["indexes"][index_name] = index
        self._commit()
        self.logger.info(f"Created index {index_name}")
        return True

    def query(
        self,
        table_name: str,
        conditions: Dict,
        use_index: bool = True,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        reverse: bool = False
    ) -> List[Any]:
        """Query data from a table with conditions"""
        if table_name not in self.data["tables"]:
            self.logger.debug(f"Table {table_name} not found")
            return []
            
        schema = self.data["schemas"].get(table_name, self._infer_schema(table_name))
        table_data = self.data["tables"][table_name]
        results = []
        if use_index and conditions:
            first_field = next(iter(conditions))
            if isinstance(conditions[first_field], dict):
                operator, value = next(iter(conditions[first_field].items()))
                if operator == "$gte":
                    index_name = f"{table_name}.{first_field}"
                    if index_name in self.data["indexes"]:
                        index = self.data["indexes"][index_name]
                        filtered_keys = [k for k in index.keys() if isinstance(k, (int, float)) and k >= value]
                        keys_or_indices = []
                        for k in filtered_keys:
                            keys_or_indices.extend(index[k])
                            
                        if isinstance(table_data, list):
                            for i in keys_or_indices:
                                if i < len(table_data):
                                    results.append(deepcopy(table_data[i]))
                        elif isinstance(table_data, dict):
                            for key in keys_or_indices:
                                if key in table_data:
                                    results.append(deepcopy(table_data[key]))
                                    
                        return results[:limit] if limit is not None else results
            else:
                index_name = f"{table_name}.{first_field}"
                if index_name in self.data["indexes"]:
                    index = self.data["indexes"][index_name]
                    first_value = conditions[first_field]
                    
                    if first_value in index:
                        keys_or_indices = index[first_value]
                        remaining_conditions = {k: v for k, v in conditions.items() if k != first_field}
                        
                        if isinstance(table_data, list):
                            for i in keys_or_indices:
                                if i < len(table_data):
                                    item = table_data[i]
                                    if all(item.get(k) == v for k, v in remaining_conditions.items()):
                                        results.append(deepcopy(item))
                        elif isinstance(table_data, dict):
                            for key in keys_or_indices:
                                if key in table_data:
                                    item = table_data[key]
                                    if all(item.get(k) == v for k, v in remaining_conditions.items()):
                                        results.append(deepcopy(item))
                                        
                        return results[:limit] if limit is not None else results
        if isinstance(table_data, list):
            for item in table_data:
                if isinstance(item, dict):
                    match = True
                    for field, condition in conditions.items():
                        if isinstance(condition, dict):
                            for op, value in condition.items():
                                if op == "$gte":
                                    if not (item.get(field, 0) >= value):
                                        match = False
                                        break
                        else:
                            if item.get(field) != condition:
                                match = False
                                break
                    if match:
                        results.append(deepcopy(item))
        elif isinstance(table_data, dict):
            for item in table_data.values():
                if isinstance(item, dict):
                    match = True
                    for field, condition in conditions.items():
                        if isinstance(condition, dict):
                            for op, value in condition.items():
                                if op == "$gte":
                                    if not (item.get(field, 0) >= value):
                                        match = False
                                        break
                        else:
                            if item.get(field) != condition:
                                match = False
                                break
                    if match:
                        results.append(deepcopy(item))
        if sort:
            results.sort(key=lambda x: x.get(sort, 0), reverse=reverse)
        if limit is not None:
            results = results[:limit]
            
        return results

    def vacuum(self) -> bool:
        """Optimize database storage"""
        try:
            for index_name in list(self.data["indexes"].keys()):
                table_name, field = index_name.split('.')
                if table_name in self.data["tables"]:
                    self.create_index(table_name, field)
            for table_name, table_data in self.data["tables"].items():
                if isinstance(table_data, list):
                    self.data["tables"][table_name] = [x for x in table_data if x is not None]
            
            self._commit()
            self.logger.info("Database vacuum completed")
            return True
        except Exception as e:
            self.logger.error(f"Vacuum failed: {str(e)}")
            return False

    def list_tables(self) -> List[str]:
        """List all tables in the database"""
        return list(self.data["tables"].keys())

    def table_info(self, table_name: str) -> Optional[Dict]:
        """Get information about a table"""
        if table_name not in self.data["tables"]:
            return None
            
        table_data = self.data["tables"][table_name]
        schema = self.data["schemas"].get(table_name, self._infer_schema(table_name))
        
        info = {
            "type": schema.get("type", "list"),
            "size": len(table_data),
            "schema": schema,
            "indexes": [idx.split('.')[1] for idx in self.data["indexes"] if idx.startswith(f"{table_name}.")]
        }
        return info

    def export_table(
        self,
        table_name: str,
        format: str = "json",
        file_path: Optional[str] = None
    ) -> Optional[Union[str, bool]]:
        """Export table data to different formats"""
        if table_name not in self.data["tables"]:
            self.logger.warning(f"Table {table_name} not found")
            return None
            
        table_data = self.data["tables"][table_name]
        
        if format == "json":
            json_data = json.dumps(table_data, indent=4, ensure_ascii=False)
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(json_data)
                return True
            return json_data
        elif format == "csv":
            try:
                import csv
                from io import StringIO
                
                if isinstance(table_data, list) and table_data and isinstance(table_data[0], dict):
                    output = StringIO()
                    writer = csv.DictWriter(output, fieldnames=table_data[0].keys())
                    writer.writeheader()
                    writer.writerows(table_data)
                    csv_data = output.getvalue()
                elif isinstance(table_data, dict) and table_data and isinstance(next(iter(table_data.values())), dict):
                    output = StringIO()
                    first_item = next(iter(table_data.values()))
                    writer = csv.DictWriter(output, fieldnames=first_item.keys())
                    writer.writeheader()
                    writer.writerows(table_data.values())
                    csv_data = output.getvalue()
                else:
                    return None
                
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(csv_data)
                    return True
                return csv_data
            except ImportError:
                self.logger.error("CSV export requires 'csv' module")
                return None
        else:
            self.logger.warning(f"Unsupported export format: {format}")
            return None

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        metadata = self.data["_metadata"]
        return {
            "database_name": self.name,
            "file_path": self.file_path,
            "schema_version": metadata.get("schema_version", "1.0"),
            "edit_count": metadata.get("edit_count", 0),
            "schema_migrations": len(metadata.get("schema_history", [])),
            "table_count": len(self.data["tables"]),
            "index_count": len(self.data["indexes"]),
            "backup_count": len(metadata.get("backups", [])),
            "created_at": datetime.fromtimestamp(metadata.get("created_at", time.time())).strftime("%Y-%m-%d %H:%M:%S"),
            "last_modified": datetime.fromtimestamp(metadata.get("last_modified", time.time())).strftime("%Y-%m-%d %H:%M:%S"),
            "backups": [
                {
                    "path": backup.get("path"),
                    "timestamp": datetime.fromtimestamp(backup.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                    "size": backup.get("size", 0)
                }
                for backup in metadata.get("backups", [])
            ]
        }