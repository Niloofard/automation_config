from typing import Dict
from ..base import Vendor
from ...database.db_manager import DatabaseManager

class NokiaVendor(Vendor):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__("Nokia")
        self.db_manager = db_manager
        self.command_patterns = self.get_command_patterns()
    
    def translate_command(self, command: str, target_vendor: Vendor) -> str:
        translated = self.db_manager.get_command_mapping(
            self.name,
            target_vendor.name,
            command
        )
        if translated:
            return translated
        for pattern, replacement in self.command_patterns.items():
            if pattern in command:
                return command.replace(pattern, replacement)
        return f"# No translation found for command: {command}"
    
    def get_command_patterns(self) -> Dict[str, str]:
        return {
            "show": "display",  # show to display
            "configure": "system-view",  # config mode
            "exit all": "quit",  # exit mode
            "interface": "interface",  # interface config
            "ip address": "ip address",  # IP address
            "admin save": "commit",  # save config
            "no": "undo",  # remove config
            "access-list": "acl",  # access list
            "ospf": "ospf",  # OSPF
            "bgp": "bgp",  # BGP
        } 