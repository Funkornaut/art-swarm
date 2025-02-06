import json
import random
from swarm import Agent
from cdp import *
from typing import List, Dict, Any, Optional
import os
from openai import OpenAI
from web3 import Web3
import requests
import base64
from PIL import Image
import io
import time
from decimal import Decimal

# Get configuration from environment variables
API_KEY_NAME = os.environ.get("CDP_API_KEY_NAME")
PRIVATE_KEY = os.environ.get("CDP_PRIVATE_KEY", "").replace('\\n', '\n')
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Configure CDP with environment variables
Cdp.configure(API_KEY_NAME, PRIVATE_KEY)

# Create a new wallet on the Base Sepolia testnet
art_wallet = Wallet.create()

# Request funds from the faucet (only works on testnet)
faucet = art_wallet.faucet()
print(f"Art wallet address: {art_wallet.default_address.address_id}")
# the insop agent should grab onchain data through the CDP
# use the onchain data api and or data from smart contract data.
# i have configured 3 contracts from Aerodrome: 
# Pool factory: 0x420dd381b31aef6683db6b902084cb0ffece40da 
# AERO token: 0x940181a94a35a4569e4529a3cdfb74e38fd98631 
# Aero Position MAnager NFT: 0x827922686190790b37229fd06084350e74485b72
# this inspirations should aslo give some words or a phrase to inspire the generative art. 
class InspoAgent:
    def __init__(self):
        # Initialize with CDP configuration
        self.network = "base-sepolia"
        # Contract addresses for inspiration
        self.contracts = {
            "pool_factory": "0x420dd381b31aef6683db6b902084cb0ffece40da",
            "aero_token": "0x940181a94a35a4569e4529a3cdfb74e38fd98631",
            "position_manager": "0x827922686190790b37229fd06084350e74485b72"
        }
        # List of assets to check balances for
        self.assets = ["eth", "usdc"] + list(self.contracts.values())
    
    def get_onchain_inspiration(self) -> Dict:
        """Use the CDP to get wallet balances and use that data for inspiration.
        Generate a color palette and theme based on the balances and addresses.
        """
        try:
            # Get balances for various assets
            balances = self._get_wallet_balances()
            
            # Use balance data for randomness
            balance_str = ''.join([str(b) for b in balances.values()])
            random.seed(balance_str)
            
            # Generate collection parameters
            num_pieces = random.randint(1, 420)
            
            # Generate color palette from contract addresses and balances
            color_palette = self._generate_color_palette_from_data(balances)
            
            # Determine theme based on balances
            theme = self._determine_theme_from_balances(balances)
            
            # Generate inspiration words based on the data
            words = self._generate_inspiration_words(balances, theme)
            
            inspiration = {
                'num_pieces': num_pieces,
                'color_palette': color_palette,
                'theme': theme,
                'inspiration_words': words,
                'timestamp': int(time.time()),
                'balances': balances  # Include balances for context
            }
            
            print(f"Generated inspiration from onchain data: {json.dumps(inspiration, indent=2)}")
            return inspiration
            
        except Exception as e:
            print(f"Error getting inspiration: {str(e)}")
            # Return default inspiration if CDP access fails
            return {
                'num_pieces': 10,
                'color_palette': ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'],
                'theme': 'Abstract',
                'inspiration_words': ['digital', 'flow', 'energy', 'motion', 'balance'],
                'timestamp': int(time.time()),
                'balances': {}
            }
    
    def _get_wallet_balances(self) -> Dict[str, Decimal]:
        """Get wallet balances for various assets"""
        balances = {}
        for asset_id in self.assets:
            try:
                balance = art_wallet.balance(asset_id)
                balances[asset_id] = balance
            except Exception as e:
                print(f"Error getting balance for {asset_id}: {str(e)}")
                balances[asset_id] = Decimal('0')
        return balances
    
    def _generate_color_palette_from_data(self, balances: Dict[str, Decimal]) -> List[str]:
        """Generate color palette from balance data and contract addresses"""
        colors = []
        # Use contract addresses for initial colors
        for address in self.contracts.values():
            if len(colors) < 5:  # We want exactly 5 colors
                color = f"#{address[2:8]}"  # Use first 6 chars after '0x'
                colors.append(color)
        
        # If we need more colors, generate from balance values
        while len(colors) < 5:
            # Convert decimals to integers for color generation
            # Multiply by 1M to get significant digits and handle decimals
            balance_ints = [int(v * 1000000) for v in balances.values()]
            # Sum the last 6 digits of each balance
            balance_sum = sum(abs(b % 1000000) for b in balance_ints) or random.randint(0, 0xFFFFFF)
            color = f"#{balance_sum % 0xFFFFFF:06x}"
            if color not in colors:  # Avoid duplicate colors
                colors.append(color)
            else:
                # If we got a duplicate, generate a random variation
                hue = random.random()
                color = f"#{int(hue * 0xFFFFFF):06x}"
                colors.append(color)
        
        return colors[:5]  # Ensure exactly 5 colors
    
    def _determine_theme_from_balances(self, balances: Dict[str, Decimal]) -> str:
        """Determine theme based on wallet balances"""
        themes = [
            "Cyberpunk", "Nature", "Abstract", "Geometric", 
            "Space", "Ocean", "Urban", "Minimal"
        ]
        
        # Use total balance to influence theme selection
        total_balance = sum(balances.values())
        balance_hash = hash(str(total_balance))
        theme_index = abs(balance_hash) % len(themes)
        
        return themes[theme_index]
    
    def _generate_inspiration_words(self, balances: Dict[str, Decimal], theme: str) -> List[str]:
        """Generate inspiration words based on the data"""
        # Base words for each theme
        theme_words = {
            "Cyberpunk": ["neon", "digital", "future", "tech", "grid"],
            "Nature": ["organic", "flow", "growth", "life", "bloom"],
            "Abstract": ["form", "chaos", "harmony", "motion", "space"],
            "Geometric": ["pattern", "structure", "order", "shape", "line"],
            "Space": ["cosmic", "void", "star", "nebula", "galaxy"],
            "Ocean": ["wave", "depth", "fluid", "current", "float"],
            "Urban": ["city", "street", "pulse", "rhythm", "edge"],
            "Minimal": ["simple", "clean", "pure", "essence", "void"]
        }
        
        # Get base words for the theme
        base_words = theme_words.get(theme, ["energy", "form", "motion", "space", "time"])
        
        # Use balance data to select and modify words
        total_balance = sum(balances.values())
        random.seed(str(total_balance))
        
        # Select 3-5 words
        num_words = random.randint(3, 5)
        selected_words = random.sample(base_words, num_words)
        
        return selected_words

class ArtistAgent:
    def generate_art_script(self, inspiration: Dict) -> str:
        """Generate Python script for art collection based on inspiration"""
        script = f'''
import random
from PIL import Image, ImageDraw
import colorsys
import math
import io

def create_art(token_id, block_hash, colors, theme="{inspiration['theme']}"):
    # Create base image
    img = Image.new('RGB', (1024, 1024), colors[0])
    draw = ImageDraw.Draw(img)
    
    # Use block hash for consistent randomness
    random.seed(block_hash + str(token_id))
    
    # Theme-specific generation
    if theme == "Geometric":
        for _ in range(50):
            x1 = random.randint(0, 1024)
            y1 = random.randint(0, 1024)
            x2 = random.randint(0, 1024)
            y2 = random.randint(0, 1024)
            color = random.choice(colors[1:])
            draw.line([(x1, y1), (x2, y2)], fill=color, width=5)
            
    elif theme == "Abstract":
        for _ in range(30):
            x = random.randint(0, 1024)
            y = random.randint(0, 1024)
            size = random.randint(50, 200)
            color = random.choice(colors[1:])
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
            
    elif theme == "Cyberpunk":
        # Grid pattern
        for x in range(0, 1024, 50):
            color = random.choice(colors[1:])
            draw.line([(x, 0), (x, 1024)], fill=color, width=2)
        for y in range(0, 1024, 50):
            color = random.choice(colors[1:])
            draw.line([(0, y), (1024, y)], fill=color, width=2)
        # Glitch effects
        for _ in range(20):
            x = random.randint(0, 924)
            y = random.randint(0, 924)
            w = random.randint(50, 100)
            h = random.randint(10, 30)
            color = random.choice(colors[1:])
            draw.rectangle([x, y, x+w, y+h], fill=color)
            
    elif theme == "Nature":
        # Draw organic shapes
        for _ in range(40):
            points = []
            center_x = random.randint(0, 1024)
            center_y = random.randint(0, 1024)
            for i in range(random.randint(3, 8)):
                angle = (i / 8) * 2 * math.pi
                radius = random.randint(20, 100)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            color = random.choice(colors[1:])
            draw.polygon(points, fill=color)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def generate_collection(num_pieces, block_hash, colors, theme):
    collection = []
    for i in range(num_pieces):
        img_bytes = create_art(i, block_hash, colors, theme)
        collection.append(img_bytes)
    return collection

# Collection parameters
NUM_PIECES = {inspiration['num_pieces']}
BLOCK_HASH = "{inspiration['block_hash']}"
COLORS = {inspiration['color_palette']}
THEME = "{inspiration['theme']}"

# Generate collection
collection = generate_collection(NUM_PIECES, BLOCK_HASH, COLORS, THEME)
'''
        return script

    def execute_script(self, script: str) -> List[bytes]:
        """Execute the generated art script and return the collection"""
        try:
            # Create a temporary namespace
            namespace = {}
            # Execute the script in the namespace
            exec(script, namespace)
            # Return the generated collection
            return namespace['collection']
        except Exception as e:
            print(f"Error executing art script: {str(e)}")
            return []

# class ImageAgent:
#     def __init__(self):
#         self.ipfs_endpoint = "https://api.pinata.cloud/pinning/pinFileToIPFS"
#         self.ipfs_api_key = os.environ.get("PINATA_API_KEY")
#         self.ipfs_secret = os.environ.get("PINATA_SECRET_KEY")
        
#         if not self.ipfs_api_key or not self.ipfs_secret:
#             raise ValueError("PINATA_API_KEY and PINATA_SECRET_KEY environment variables are required")
    
#     def upload_to_ipfs(self, image_data: bytes, metadata: Dict) -> str:
#         """Upload image and metadata to IPFS"""
#         try:
#             headers = {
#                 'pinata_api_key': self.ipfs_api_key,
#                 'pinata_secret_api_key': self.ipfs_secret
#             }
            
#             # Upload image
#             files = {'file': ('art.png', image_data)}
#             response = requests.post(self.ipfs_endpoint, files=files, headers=headers)
#             response.raise_for_status()  # Raise exception for bad status codes
#             image_hash = response.json()['IpfsHash']
            
#             # Upload metadata
#             metadata['image'] = f"ipfs://{image_hash}"
#             metadata_response = requests.post(
#                 self.ipfs_endpoint,
#                 files={'file': ('metadata.json', json.dumps(metadata))},
#                 headers=headers
#             )
#             metadata_response.raise_for_status()
#             return metadata_response.json()['IpfsHash']
#         except Exception as e:
#             print(f"Error uploading to IPFS: {str(e)}")
#             return None

# class RodeoAgent:
#     def __init__(self):
#         self.rodeo_api = "https://api.rodeo.club"
#         self.api_key = os.environ.get("RODEO_API_KEY")
        
#         if not self.api_key:
#             raise ValueError("RODEO_API_KEY environment variable is required")
    
#     def post_to_rodeo(self, collection_data: Dict) -> str:
#         """Post collection to Rodeo.club"""
#         try:
#             headers = {
#                 'Authorization': f'Bearer {self.api_key}',
#                 'Content-Type': 'application/json'
#             }
            
#             payload = {
#                 'name': collection_data['name'],
#                 'description': collection_data['description'],
#                 'image': collection_data['image'],
#                 'external_url': collection_data.get('external_url'),
#                 'attributes': collection_data.get('attributes', [])
#             }
            
#             response = requests.post(f"{self.rodeo_api}/collections", json=payload, headers=headers)
#             response.raise_for_status()
#             return response.json()['id']
#         except Exception as e:
#             print(f"Error posting to Rodeo: {str(e)}")
#             return None

# # Create agent instances
# inspo_agent = InspoAgent()
# artist_agent = ArtistAgent()
# image_agent = ImageAgent()
# rodeo_agent = RodeoAgent()

# Function to orchestrate the entire process
def create_generative_collection():
    """Orchestrate the creation and deployment of a generative art collection"""
    try:
        # 1. Get inspiration
        inspiration = inspo_agent.get_onchain_inspiration()
        print(f"Generated inspiration: {inspiration}")
        
        # 2. Generate and execute art script
        art_script = artist_agent.generate_art_script(inspiration)
        print("Generated art script")
        collection = artist_agent.execute_script(art_script)
        print(f"Generated {len(collection)} pieces")
        
        if not collection:
            raise Exception("Failed to generate art collection")
        
        # 3. Upload first piece and collection metadata to IPFS
        collection_metadata = {
            'name': f"{inspiration['theme']} Collection",
            'description': f"A generative art collection inspired by {inspiration['theme']}",
            'attributes': [
                {'trait_type': 'Theme', 'value': inspiration['theme']},
                {'trait_type': 'Collection Size', 'value': inspiration['num_pieces']}
            ]
        }
        
        # Upload first piece as collection cover
        cover_hash = image_agent.upload_to_ipfs(collection[0], collection_metadata)
        if not cover_hash:
            raise Exception("Failed to upload to IPFS")
        
        # 4. Post to Rodeo
        collection_metadata['image'] = f"ipfs://{cover_hash}"
        collection_id = rodeo_agent.post_to_rodeo(collection_metadata)
        if not collection_id:
            raise Exception("Failed to post to Rodeo")
        
        rodeo_url = f"https://rodeo.club/collection/{collection_id}"
        print(f"Posted to Rodeo: {rodeo_url}")
        
        return {
            'inspiration': inspiration,
            'collection_id': collection_id,
            'rodeo_url': rodeo_url,
            'ipfs_hash': cover_hash,
            'num_pieces': len(collection)
        }
    
    except Exception as e:
        print(f"Error creating collection: {str(e)}")
        return None

# Create the main agent that orchestrates everything
art_swarm_agent = Agent(
    name="Art Swarm Agent",
    instructions="""You are an AI art curator that creates and deploys generative art collections.
    You use onchain data for inspiration, create Python scripts for art generation,
    handle deployment to IPFS and Rodeo.club. You can create new collections and
    check their status. Each collection is unique, using blockchain data for
    randomness and inspiration.""",
    functions=[create_generative_collection]
) 