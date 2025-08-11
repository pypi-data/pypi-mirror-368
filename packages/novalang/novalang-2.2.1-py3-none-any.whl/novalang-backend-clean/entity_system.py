"""
NovaLang Entity System - SpringBoot-like Entity Management
Auto-generates database tables from entity definitions.
"""

import mysql.connector
from mysql.connector import Error
import os
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class EntityField:
    """Represents a field in an entity."""
    
    def __init__(self, name: str, field_type: str, nullable: bool = True, 
                 unique: bool = False, default: Any = None, max_length: int = None):
        self.name = name
        self.field_type = field_type
        self.nullable = nullable
        self.unique = unique
        self.default = default
        self.max_length = max_length
    
    def to_sql_definition(self) -> str:
        """Convert field to SQL column definition."""
        sql_type = self._get_sql_type()
        definition = f"`{self.name}` {sql_type}"
        
        if not self.nullable:
            definition += " NOT NULL"
        
        if self.unique:
            definition += " UNIQUE"
        
        if self.default is not None:
            if isinstance(self.default, str):
                definition += f" DEFAULT '{self.default}'"
            elif self.default == "CURRENT_TIMESTAMP":
                definition += " DEFAULT CURRENT_TIMESTAMP"
            else:
                definition += f" DEFAULT {self.default}"
        
        return definition
    
    def _get_sql_type(self) -> str:
        """Map NovaLang types to MySQL types."""
        type_map = {
            'string': f'VARCHAR({self.max_length or 255})',
            'text': 'TEXT',
            'int': 'INT',
            'bigint': 'BIGINT',
            'float': 'FLOAT',
            'double': 'DOUBLE',
            'boolean': 'BOOLEAN',
            'datetime': 'DATETIME',
            'timestamp': 'TIMESTAMP',
            'date': 'DATE',
            'json': 'JSON'
        }
        return type_map.get(self.field_type.lower(), 'VARCHAR(255)')


class Entity:
    """Represents a database entity/table."""
    
    def __init__(self, name: str, table_name: str = None):
        self.name = name
        self.table_name = table_name or name.lower() + 's'
        self.fields: Dict[str, EntityField] = {}
        self.primary_key: str = 'id'
        
        # Add default ID field
        self.add_field('id', 'int', nullable=False, auto_increment=True)
    
    def add_field(self, name: str, field_type: str, nullable: bool = True,
                  unique: bool = False, default: Any = None, max_length: int = None,
                  auto_increment: bool = False):
        """Add a field to the entity."""
        field = EntityField(name, field_type, nullable, unique, default, max_length)
        field.auto_increment = auto_increment
        self.fields[name] = field
        return self
    
    def add_timestamps(self):
        """Add created_at and updated_at timestamp fields."""
        self.add_field('created_at', 'timestamp', nullable=False, default='CURRENT_TIMESTAMP')
        self.add_field('updated_at', 'timestamp', nullable=False, 
                      default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
        return self
    
    def to_create_table_sql(self) -> str:
        """Generate CREATE TABLE SQL statement."""
        field_definitions = []
        
        for field in self.fields.values():
            definition = field.to_sql_definition()
            if hasattr(field, 'auto_increment') and field.auto_increment:
                definition += " AUTO_INCREMENT"
            field_definitions.append(definition)
        
        # Add primary key
        field_definitions.append(f"PRIMARY KEY (`{self.primary_key}`)")
        
        sql = f"""CREATE TABLE IF NOT EXISTS `{self.table_name}` (
    {',\n    '.join(field_definitions)}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"""
        
        return sql


class EntityManager:
    """Manages entities and database operations."""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.connection = None
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME', 'novalang_backend'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    def register_entity(self, entity: Entity):
        """Register an entity with the manager."""
        self.entities[entity.name] = entity
        print(f"📋 Registered entity: {entity.name} -> table: {entity.table_name}")
    
    def connect(self) -> bool:
        """Connect to MySQL database."""
        try:
            print(f"🔗 Connecting to MySQL: {self.config['host']}:{self.config['port']}")
            print(f"📂 Database: {self.config['database']}")
            
            self.connection = mysql.connector.connect(**self.config)
            
            if self.connection.is_connected():
                print("✅ Connected to MySQL database successfully!")
                return True
            else:
                print("❌ Failed to connect to MySQL database")
                return False
                
        except Error as e:
            print(f"❌ MySQL connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MySQL database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Disconnected from MySQL database")
    
    def create_all_tables(self):
        """Create all registered entity tables."""
        if not self.connection or not self.connection.is_connected():
            print("❌ Not connected to database")
            return False
        
        cursor = self.connection.cursor()
        success_count = 0
        
        try:
            for entity_name, entity in self.entities.items():
                try:
                    sql = entity.to_create_table_sql()
                    print(f"\n🏗️  Creating table '{entity.table_name}' for entity '{entity_name}'...")
                    print(f"SQL: {sql[:100]}..." if len(sql) > 100 else f"SQL: {sql}")
                    
                    cursor.execute(sql)
                    print(f"✅ Table '{entity.table_name}' created successfully!")
                    success_count += 1
                    
                except Error as e:
                    print(f"❌ Error creating table '{entity.table_name}': {e}")
            
            print(f"\n🎉 Database setup complete! Created {success_count}/{len(self.entities)} tables.")
            return success_count == len(self.entities)
            
        except Error as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            cursor.close()
    
    def insert(self, entity_name: str, data: Dict[str, Any]) -> Optional[int]:
        """Insert data into an entity table."""
        if entity_name not in self.entities:
            raise RuntimeError(f"Entity '{entity_name}' not found")
        
        entity = self.entities[entity_name]
        cursor = self.connection.cursor()
        
        try:
            # Remove id from data if it's auto-increment
            insert_data = {k: v for k, v in data.items() if k != 'id'}
            
            columns = list(insert_data.keys())
            values = list(insert_data.values())
            placeholders = ', '.join(['%s'] * len(values))
            
            sql = f"INSERT INTO `{entity.table_name}` ({', '.join(f'`{col}`' for col in columns)}) VALUES ({placeholders})"
            
            cursor.execute(sql, values)
            self.connection.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            print(f"❌ Error inserting into '{entity.table_name}': {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()
    
    def find_all(self, entity_name: str) -> List[Dict[str, Any]]:
        """Find all records for an entity."""
        if entity_name not in self.entities:
            raise RuntimeError(f"Entity '{entity_name}' not found")
        
        entity = self.entities[entity_name]
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            sql = f"SELECT * FROM `{entity.table_name}`"
            cursor.execute(sql)
            return cursor.fetchall()
            
        except Error as e:
            print(f"❌ Error querying '{entity.table_name}': {e}")
            return []
        finally:
            cursor.close()
    
    def find_by_id(self, entity_name: str, entity_id: int) -> Optional[Dict[str, Any]]:
        """Find a record by ID."""
        if entity_name not in self.entities:
            raise RuntimeError(f"Entity '{entity_name}' not found")
        
        entity = self.entities[entity_name]
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            sql = f"SELECT * FROM `{entity.table_name}` WHERE id = %s"
            cursor.execute(sql, (entity_id,))
            return cursor.fetchone()
            
        except Error as e:
            print(f"❌ Error querying '{entity.table_name}': {e}")
            return None
        finally:
            cursor.close()


# Global entity manager instance
entity_manager = EntityManager()


def create_entity(name: str, table_name: str = None) -> Entity:
    """Create a new entity (SpringBoot @Entity equivalent)."""
    entity = Entity(name, table_name)
    entity_manager.register_entity(entity)
    return entity


def startup_database():
    """Initialize database connection and create tables (SpringBoot startup equivalent)."""
    print("\n🚀 NovaLang Entity System Starting...")
    print("=" * 50)
    
    if entity_manager.connect():
        entity_manager.create_all_tables()
        return True
    return False


def shutdown_database():
    """Cleanup database connection."""
    entity_manager.disconnect()
