from typing import Dict
from server.models.base import Vendor
from server.database.db_manager import DatabaseManager

class CiscoVendor(Vendor):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__("Cisco")
        self.db_manager = db_manager
        self.command_patterns = self.get_command_patterns()
    
    def translate_command(self, command: str, target_vendor: Vendor) -> str:
        # Try exact match in the database
        translated = self.db_manager.get_command_mapping(
            self.name,
            target_vendor.name,
            command
        )
        if translated:
            return translated
        # Pattern-based translation (simple example)
        for pattern, replacement in self.command_patterns.items():
            if pattern in command:
                return command.replace(pattern, replacement)
        return f"# No translation found for command: {command}"
    
    def get_command_patterns(self) -> Dict[str, str]:
        return {
            "show": "display",  # Basic show to display translation
            "configure terminal": "system-view",  # Enter configuration mode
            "exit": "quit",  # Exit current mode
            "interface": "interface",  # Interface configuration
            "ip address": "ip address",  # IP address configuration
            "write memory": "commit",  # Save configuration
            "no": "undo",  # Remove configuration
            "access-list": "acl",  # Access list configuration
            "router ospf": "ospf",  # OSPF configuration
            "router bgp": "bgp",  # BGP configuration
        } 