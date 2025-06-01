from typing import Dict
from server.models.base import Vendor
from server.database.db_manager import DatabaseManager

class HuaweiVendor(Vendor):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__("Huawei")
        self.db_manager = db_manager
        self.command_patterns = self.get_command_patterns()
    
    def translate_command(self, command: str, target_vendor: Vendor) -> str:
        """Translate a Huawei command to target vendor's format"""
        # First try exact match
        translated = self.db_manager.get_command_mapping(
            self.name,
            target_vendor.name,
            command
        )
        
        if translated:
            return translated
        
        # If no exact match, try pattern matching
        # This is a simplified example - in reality, you'd want more sophisticated pattern matching
        for pattern, replacement in self.command_patterns.items():
            if pattern in command:
                # Replace the pattern with target vendor's equivalent
                return command.replace(pattern, replacement)
        
        return f"# No translation found for command: {command}"
    
    def get_command_patterns(self) -> Dict[str, str]:
        """Get common command patterns for Huawei"""
        return {
            "display": "show",  # Basic display to show translation
            "system-view": "configure terminal",  # Enter configuration mode
            "quit": "exit",  # Exit current mode
            "interface": "interface",  # Interface configuration
            "ip address": "ip address",  # IP address configuration
            "commit": "write memory",  # Save configuration
            "undo": "no",  # Remove configuration
            "acl": "access-list",  # Access list configuration
            "ospf": "router ospf",  # OSPF configuration
            "bgp": "router bgp",  # BGP configuration
        } 