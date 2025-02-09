"""Module for posting content to Rodeo.

This module provides functionality to post content to Rodeo, a decentralized social platform
on Base. It handles collection initialization, token creation, and sale setup automatically.
"""

import json
import time
from typing import Callable, Dict, Optional
from web3 import Web3

from pydantic import BaseModel, Field, validator, constr

from cdp_agentkit_core.actions.base import CdpAction
from cdp_sdk import Wallet
from cdp_agentkit_core.actions.rodeo.config import config, DEFAULT_COLLECTION_URI

POST_TO_RODEO_PROMPT = """
This tool allows you to post content to Rodeo, a decentralized social platform on Base.
It handles all the necessary steps to create and list a post, including:
1. One-time collection initialization (automatic)
2. Token creation with metadata
3. Sale setup for free minting

Required inputs:
- image_uri: IPFS URI of the image (must start with 'ipfs://')
- name: Title of your post (max 100 characters)
- description: Description of your post (max 500 characters)
- category (optional): Category tag (e.g., 'Art', 'Photography', 'AI')

Example usage:
1. Post AI-generated art:
   image_uri: "ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq"
   name: "Neural Network Dreams #1"
   description: "AI-generated artwork exploring abstract landscapes"
   category: "AI Art"

2. Share NFT collection preview:
   image_uri: "ipfs://bafybeihkoviema7g3gxyt6la7vd5ho32ictqbxk7jxwfbsxeh6umm2acdi"
   name: "CryptoPunks Collection Highlight"
   description: "Featured pieces from the iconic CryptoPunks collection"
   category: "NFT"

The post will be available for 24 hours on Rodeo and can be collected by anyone.
Network (Base Mainnet or Base Sepolia) is automatically determined from the wallet.
"""

class PostToRodeoInput(BaseModel):
    """Input argument schema for posting to Rodeo action."""
    
    image_uri: str = Field(
        ...,
        description="The IPFS URI of the image to post (must start with 'ipfs://')",
        example="ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq"
    )
    name: constr(max_length=100) = Field(
        ...,
        description="The name/title of the post (max 100 characters)",
        example="Neural Network Dreams #1"
    )
    description: constr(max_length=500) = Field(
        ...,
        description="The description of the post (max 500 characters)",
        example="AI-generated artwork exploring abstract landscapes"
    )
    category: Optional[constr(max_length=50)] = Field(
        None,
        description="Optional category for the post (e.g., 'Art', 'Photography', 'AI', etc.)",
        example="AI Art"
    )
    
    @validator('image_uri')
    def validate_ipfs_uri(cls, v):
        """Validate that the image URI is a proper IPFS URI."""
        if not v.startswith('ipfs://'):
            raise ValueError('Image URI must start with ipfs://')
        if len(v) < 10:  # Basic length check
            raise ValueError('Invalid IPFS URI length')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate that the name is not empty or just whitespace."""
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validate that the description is not empty or just whitespace."""
        if not v.strip():
            raise ValueError('Description cannot be empty or just whitespace')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        """Validate category format if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not v[0].isupper():
                v = v.title()
        return v

def initialize_collection(wallet: Wallet) -> str:
    """Initialize the collection contract if not already done.
    
    This function handles the one-time setup required for posting to Rodeo:
    1. Creates a new collection using the factory contract
    2. Grants minter role to the Rodeo drop market
    3. Persists the collection address for future use
    
    Args:
        wallet (Wallet): The wallet to use for contract initialization.
        
    Returns:
        str: The collection contract address.
        
    Raises:
        Exception: If collection initialization fails.
    """
    # Get network-specific configuration
    network_id = wallet.network_id
    network_config = config.get_network_config(network_id)
    
    # Check if we already have a collection for this network
    collection_address = config.get_collection_address(network_id)
    if collection_address:
        return collection_address
        
    try:
        # Create collection using factory
        creation_args = {
            "contractCreationNonce": int(time.time()),  # Use timestamp as nonce
            "contractURI": DEFAULT_COLLECTION_URI
        }
        
        factory_tx = wallet.invoke_contract(
            contract_address=network_config["factory_address"],
            method="createMultiTokenCollection",
            args=creation_args
        ).wait()
        
        # Extract collection address from transaction receipt
        collection_address = None
        for log in factory_tx.logs:
            # Look for the contract creation event
            if len(log.topics) > 1:
                # Convert the address from bytes32 to address format
                collection_address = Web3.to_checksum_address(log.topics[1][-40:])
                break
                
        if not collection_address:
            raise Exception("Could not find collection address in transaction logs")
        
        # Grant minter role to drop market
        minter_args = {
            "minter": network_config["drop_market_address"]
        }
        wallet.invoke_contract(
            contract_address=collection_address,
            method="grantMinter",
            args=minter_args
        ).wait()
        
        # Save the collection address
        config.set_collection_address(network_id, collection_address)
        return collection_address
        
    except Exception as e:
        raise Exception(f"Failed to initialize collection: {str(e)}")

def create_token(wallet: Wallet, collection_address: str, metadata: Dict) -> int:
    """Create a new token in the collection.
    
    This function creates a new token with the provided metadata and sets it to expire
    in 24 hours, following Rodeo's post duration guidelines.
    
    Args:
        wallet (Wallet): The wallet to use for token creation.
        collection_address (str): The collection contract address.
        metadata (Dict): The token metadata containing name, description, and image URI.
        
    Returns:
        int: The created token ID.
        
    Raises:
        ValueError: If metadata format is invalid.
        Exception: If token creation fails.
    """
    # Validate metadata format
    required_fields = ['name', 'description', 'image']
    if not all(field in metadata for field in required_fields):
        raise ValueError(f"Metadata must contain all required fields: {required_fields}")
    
    if not metadata['image'].startswith('ipfs://'):
        raise ValueError("Image URI in metadata must start with ipfs://")
    
    # Generate token ID based on timestamp for uniqueness
    token_id = int(time.time() * 1000)
    
    # Set mint end time to 24 hours from now
    mint_end_time = int(time.time()) + (24 * 60 * 60)
    
    create_args = {
        "tokenId": token_id,
        "tokenURI": f"ipfs://{metadata['ipfs_hash']}" if 'ipfs_hash' in metadata else f"ipfs://{json.dumps(metadata)}",
        "mintEndTime": mint_end_time
    }
    
    try:
        wallet.invoke_contract(
            contract_address=collection_address,
            method="createToken",
            args=create_args
        ).wait()
        return token_id
    except Exception as e:
        raise Exception(f"Failed to create token: {str(e)}")

def create_sale(wallet: Wallet, collection_address: str, token_id: int) -> str:
    """Create a sale for the token on the drop market.
    
    This function sets up a free mint for the token, allowing anyone to collect it
    within the 24-hour window.
    
    Args:
        wallet (Wallet): The wallet to use for sale creation.
        collection_address (str): The collection contract address.
        token_id (int): The token ID to sell.
        
    Returns:
        str: The transaction hash of the sale creation.
        
    Raises:
        Exception: If sale creation fails.
    """
    # Get network-specific configuration
    network_config = config.get_network_config(wallet.network_id)
    
    sale_args = {
        "multiTokenContract": collection_address,
        "tokenId": token_id,
        "pricePerQuantity": 0,  # Free mint
        "creatorPaymentAddress": wallet.default_address.address_id,
        "generalAvailabilityStartTime": 0  # Start immediately
    }
    
    try:
        sale_tx = wallet.invoke_contract(
            contract_address=network_config["drop_market_address"],
            method="createFixedPriceSale",
            args=sale_args
        ).wait()
        return sale_tx.transaction.transaction_hash
    except Exception as e:
        raise Exception(f"Failed to create sale: {str(e)}")

def post_to_rodeo(wallet: Wallet, image_uri: str, name: str, description: str, category: Optional[str] = None) -> str:
    """Post content to Rodeo.

    This function handles the entire process of posting content to Rodeo:
    1. Validates input format
    2. Initializes collection if needed
    3. Creates a token with metadata
    4. Sets up a free mint sale
    
    The post will be available for 24 hours and can be collected by anyone.
    The network (Base Mainnet or Base Sepolia) is determined by the wallet's configuration.

    Args:
        wallet (Wallet): The wallet to use for authentication and transactions.
        image_uri (str): The IPFS URI of the image to post.
        name (str): The name/title of the post.
        description (str): The description of the post.
        category (Optional[str]): Optional category for the post.

    Returns:
        str: A message containing the post details and URLs.
        
    Raises:
        ValueError: If input validation fails.
        Exception: If any step of the posting process fails.
    """
    try:
        # Validate IPFS URI format
        if not image_uri.startswith("ipfs://"):
            return "Error: Image URI must start with 'ipfs://'"
            
        # Initialize collection if needed
        collection_address = initialize_collection(wallet)
        
        # Prepare token metadata
        metadata = {
            "name": name,
            "description": description,
            "image": image_uri
        }
        if category:
            metadata["category"] = category
            
        # Create token
        token_id = create_token(wallet, collection_address, metadata)
        
        # Create sale
        sale_tx_hash = create_sale(wallet, collection_address, token_id)
        
        # Generate URLs
        rodeo_url = f"https://rodeo.club/post/{collection_address}/{token_id}"
        explorer_url = f"https://{'basescan.org' if wallet.network_id == 'base-mainnet' else 'sepolia.basescan.org'}/tx/{sale_tx_hash}"
        
        return f"""Successfully posted to Rodeo on {wallet.network_id}:
Collection Address: {collection_address}
Token ID: {token_id}
Sale Transaction: {sale_tx_hash}
Post URL: {rodeo_url}
Transaction URL: {explorer_url}
The post will be available for 24 hours on Rodeo."""

    except Exception as e:
        return f"Error posting to Rodeo: {e!s}"

class PostToRodeoAction(CdpAction):
    """Post to Rodeo action.
    
    This action enables posting content to Rodeo, a decentralized social platform on Base.
    It handles collection initialization, token creation, and sale setup automatically.
    The network (Base Mainnet or Base Sepolia) is determined by the wallet's configuration.
    """

    name: str = "post_to_rodeo"
    description: str = POST_TO_RODEO_PROMPT
    args_schema: type[BaseModel] | None = PostToRodeoInput
    func: Callable[..., str] = post_to_rodeo
