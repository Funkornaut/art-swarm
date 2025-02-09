"""Configuration module for Rodeo actions."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

# Network configurations
NETWORK_CONFIGS = {
    "base-mainnet": {
        "factory_address": "0xf1814213A5Ef856aAa1fdb0F7f375569168d8E73",
        "drop_market_address": "0x132363a3bbf47E06CF642dd18E9173E364546C99",
    },
    "base-sepolia": {
        "factory_address": "0x0D0c39Ad9f93ea8e775Eaa1d2Fd410f5534dFaFE",
        "drop_market_address": "0xE750E597bFcDbe1C27322e729f1796B52DFCddDb",
    }
}

# Default collection metadata URI that sets collection name as "Rodeo posts"
DEFAULT_COLLECTION_URI = "https://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq.ipfs.dweb.link/metadata.json"

class RodeoConfig:
    """Configuration manager for Rodeo actions."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = Path.home() / ".rodeo"
        self.collections_file = self.config_dir / "collections.json"
        self._collections: Dict[str, Dict[str, str]] = {}
        self._load_collections()
    
    def _load_collections(self) -> None:
        """Load collection addresses from disk."""
        try:
            if not self.config_dir.exists():
                self.config_dir.mkdir(parents=True)
            
            if self.collections_file.exists():
                with open(self.collections_file, 'r') as f:
                    self._collections = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load collections file: {e}")
            self._collections = {}
    
    def _save_collections(self) -> None:
        """Save collection addresses to disk."""
        try:
            if not self.config_dir.exists():
                self.config_dir.mkdir(parents=True)
            
            with open(self.collections_file, 'w') as f:
                json.dump(self._collections, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save collections file: {e}")
    
    def get_network_config(self, network_id: str) -> Dict[str, str]:
        """Get the configuration for a specific network.
        
        Args:
            network_id (str): The network ID (e.g., 'base-mainnet' or 'base-sepolia')
            
        Returns:
            Dict[str, str]: The network configuration
            
        Raises:
            ValueError: If the network is not supported
        """
        if network_id not in NETWORK_CONFIGS:
            raise ValueError(f"Unsupported network: {network_id}. Supported networks: {list(NETWORK_CONFIGS.keys())}")
        return NETWORK_CONFIGS[network_id]
    
    def get_collection_address(self, network_id: str) -> Optional[str]:
        """Get the collection address for a specific network.
        
        Args:
            network_id (str): The network ID
            
        Returns:
            Optional[str]: The collection address or None if not initialized
        """
        return self._collections.get(network_id)
    
    def set_collection_address(self, network_id: str, address: str) -> None:
        """Set the collection address for a specific network.
        
        Args:
            network_id (str): The network ID
            address (str): The collection address
        """
        self._collections[network_id] = address
        self._save_collections()
    
    def clear_collection_address(self, network_id: str) -> None:
        """Clear the collection address for a specific network.
        
        Args:
            network_id (str): The network ID
        """
        if network_id in self._collections:
            del self._collections[network_id]
            self._save_collections()

# Global instance
config = RodeoConfig() 