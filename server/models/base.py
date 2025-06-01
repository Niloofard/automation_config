from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class Vendor(ABC):
    """Base class for vendor-specific implementations"""
    
    def __init__(self, name: str):
        self.name = name
        self.command_patterns: Dict[str, str] = {}
    
    @abstractmethod
    def translate_command(self, command: str, target_vendor: 'Vendor') -> str:
        """Translate a command to target vendor's format"""
        pass
    
    @abstractmethod
    def get_command_patterns(self) -> Dict[str, str]:
        """Get command patterns for this vendor"""
        pass

class CommandTranslator:
    """Main translator class that handles command translation between vendors"""
    
    def __init__(self):
        self.vendors: Dict[str, Vendor] = {}
    
    def register_vendor(self, vendor: Vendor) -> None:
        """Register a vendor implementation"""
        self.vendors[vendor.name] = vendor
    
    def translate(self, command: str, source_vendor: str, target_vendor: str) -> str:
        """Translate a command from source vendor to target vendor"""
        if source_vendor not in self.vendors:
            raise ValueError(f"Source vendor {source_vendor} not registered")
        if target_vendor not in self.vendors:
            raise ValueError(f"Target vendor {target_vendor} not registered")
        
        return self.vendors[source_vendor].translate_command(
            command, 
            self.vendors[target_vendor]
        )
    
    def get_commands_by_topic(self, topic: str) -> Dict[str, List[str]]:
        """Get commands for a specific topic across all vendors"""
        # This will be implemented to query the database
        pass 