import sqlite3
from typing import Dict, List, Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "router_commands.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the database with schema"""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            with sqlite3.connect(self.db_path) as conn:
                # Create tables if they don't exist
                conn.executescript(schema)
                
                # Check if vendors exist before inserting
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM vendors")
                existing_vendors = {row[0] for row in cursor.fetchall()}
                
                # Insert vendors only if they don't exist
                vendors_to_insert = [
                    ('Huawei', 'Huawei Network Equipment'),
                    ('Cisco', 'Cisco Network Equipment'),
                    ('Juniper', 'Juniper Network Equipment'),
                    ('Nokia', 'Nokia Network Equipment')
                ]
                
                for vendor_name, description in vendors_to_insert:
                    if vendor_name not in existing_vendors:
                        cursor.execute(
                            "INSERT INTO vendors (name, description) VALUES (?, ?)",
                            (vendor_name, description)
                        )
                
                # Check if topics exist before inserting
                cursor.execute("SELECT name FROM topics")
                existing_topics = {row[0] for row in cursor.fetchall()}
                
                # Insert topics only if they don't exist
                topics_to_insert = [
                    ('BGP', 'Border Gateway Protocol'),
                    ('OSPF', 'Open Shortest Path First'),
                    ('MPLS', 'Multiprotocol Label Switching'),
                    ('SSH', 'Secure Shell'),
                    ('Interface', 'Interface Configuration'),
                    ('Routing', 'General Routing Commands'),
                    ('Security', 'Security and Access Control')
                ]
                
                for topic_name, description in topics_to_insert:
                    if topic_name not in existing_topics:
                        cursor.execute(
                            "INSERT INTO topics (name, description) VALUES (?, ?)",
                            (topic_name, description)
                        )
                
                conn.commit()
                logger.debug("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_command_mapping(self, 
                          source_vendor: str,
                          target_vendor: str,
                          source_command: str,
                          target_command: str,
                          topic: str,
                          description: Optional[str] = None) -> None:
        """Add a new command mapping to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get vendor IDs
                cursor.execute("SELECT id FROM vendors WHERE name = ?", (source_vendor,))
                source_vendor_id = cursor.fetchone()[0]
                
                cursor.execute("SELECT id FROM vendors WHERE name = ?", (target_vendor,))
                target_vendor_id = cursor.fetchone()[0]
                
                # Get topic ID
                cursor.execute("SELECT id FROM topics WHERE name = ?", (topic,))
                topic_id = cursor.fetchone()[0]
                
                # Insert mapping
                cursor.execute("""
                    INSERT INTO command_mappings 
                    (source_vendor_id, target_vendor_id, source_command, target_command, topic_id, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (source_vendor_id, target_vendor_id, source_command, target_command, topic_id, description))
                
                conn.commit()
                logger.debug(f"Added command mapping: {source_vendor} -> {target_vendor}: {source_command} -> {target_command}")
        except Exception as e:
            logger.error(f"Error adding command mapping: {str(e)}")
            raise
    
    def get_command_mapping(self,
                          source_vendor: str,
                          target_vendor: str,
                          source_command: str) -> Optional[str]:
        """Get the target command for a given source command"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT cm.target_command
                    FROM command_mappings cm
                    JOIN vendors sv ON cm.source_vendor_id = sv.id
                    JOIN vendors tv ON cm.target_vendor_id = tv.id
                    WHERE sv.name = ? AND tv.name = ? AND cm.source_command = ?
                """, (source_vendor, target_vendor, source_command))
                
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting command mapping: {str(e)}")
            raise
    
    def get_commands_by_topic(self, topic: str) -> Dict[str, List[Tuple[str, str]]]:
        """Get all command mappings for a specific topic"""
        try:
            logger.debug(f"Getting commands for topic: {topic}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sv.name, tv.name, cm.source_command, cm.target_command
                    FROM command_mappings cm
                    JOIN vendors sv ON cm.source_vendor_id = sv.id
                    JOIN vendors tv ON cm.target_vendor_id = tv.id
                    JOIN topics t ON cm.topic_id = t.id
                    WHERE t.name = ?
                """, (topic,))
                
                # Group commands by vendor pair
                commands = {}
                rows = cursor.fetchall()
                logger.debug(f"Found {len(rows)} rows for topic {topic}")
                
                for row in rows:
                    source_vendor, target_vendor, source_cmd, target_cmd = row
                    vendor_pair = f"{source_vendor}->{target_vendor}"
                    if vendor_pair not in commands:
                        commands[vendor_pair] = []
                    commands[vendor_pair].append((source_cmd, target_cmd))
                    logger.debug(f"Added command pair: {source_cmd} -> {target_cmd} for {vendor_pair}")
                
                logger.debug(f"Returning commands: {commands}")
                return commands
        except Exception as e:
            logger.error(f"Error getting commands by topic: {str(e)}")
            raise

    def get_commands_by_vendor(self, vendor: str) -> List[str]:
        """Get all unique commands for a specific vendor"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT source_command
                    FROM command_mappings cm
                    JOIN vendors v ON cm.source_vendor_id = v.id
                    WHERE v.name = ?
                    UNION
                    SELECT DISTINCT target_command
                    FROM command_mappings cm
                    JOIN vendors v ON cm.target_vendor_id = v.id
                    WHERE v.name = ?
                """, (vendor, vendor))
                
                commands = [row[0] for row in cursor.fetchall()]
                logger.debug(f"Found commands for vendor {vendor}: {commands}")
                return commands
        except Exception as e:
            logger.error(f"Error getting commands by vendor: {str(e)}")
            raise

    def close(self):
        """Close the database connection."""
        pass  # SQLite connections are automatically closed 