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
import noise
import math
from opensimplex import OpenSimplex

# Get configuration from environment variables
API_KEY_NAME = os.environ.get("CDP_API_KEY_NAME")
PRIVATE_KEY = os.environ.get("CDP_PRIVATE_KEY", "").replace('\\n', '\n')
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Configure CDP with environment variables
Cdp.configure(API_KEY_NAME, PRIVATE_KEY)

# Create a new wallet on the Base Sepolia testnet
art_wallet = None

def get_art_wallet():
    global art_wallet
    if art_wallet is None:
        art_wallet = Wallet.create()
        # Request funds from the faucet (only works on testnet)
        art_wallet.faucet()
        print(f"Art wallet address: {art_wallet.default_address.address_id}")
    return art_wallet

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
        self.network = "base-mainnet"
        # Contract addresses for inspiration
        # TODO we need to come back to this and get some events from these contracts to use as data for the artist
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
        wallet = get_art_wallet()
        for asset_id in self.assets:
            try:
                balance = wallet.balance(asset_id)
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
        # Format the inspiration data for the script
        num_pieces = inspiration.get('num_pieces', 1)
        colors = inspiration.get('color_palette', ['#000000'])
        theme = inspiration.get('theme', 'Abstract')
        
        # Convert Decimal values to strings for JSON serialization
        inspiration_copy = inspiration.copy()
        if 'balances' in inspiration_copy:
            balances_dict = {}
            for k, v in inspiration_copy['balances'].items():
                balances_dict[k] = str(v)
            inspiration_copy['balances'] = balances_dict
        
        inspiration_json = json.dumps(inspiration_copy)
        
        script = '''
import random
from PIL import Image, ImageDraw
import colorsys
import math
import io
import json
from decimal import Decimal
from opensimplex import OpenSimplex
from typing import List, Tuple

def create_flow_field(width: int, height: int, scale: float, octaves: int, seed: int) -> List[List[float]]:
    """Create a flow field using OpenSimplex noise"""
    field = []
    noise_gen = OpenSimplex(seed=seed)
    
    for y in range(height):
        row = []
        for x in range(width):
            # Use multiple layers of noise for more organic flow
            noise_val = 0
            for i in range(octaves):
                freq = 1 * 2**i
                noise_val += noise_gen.noise2(
                    x=x * scale * freq,
                    y=y * scale * freq
                ) * (1 / 2**i)
            angle = noise_val * math.pi  # Scale to [-π, π]
            row.append(angle)
        field.append(row)
    return field

def create_art(token_id: int, inspiration_data: dict, colors: List[str], theme: str) -> bytes:
    """Create generative art inspired by flow field techniques"""
    try:
        # Initialize canvas
        width, height = 2048, 2048  # Higher resolution for better detail
        img = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(img)
        
        # Use inspiration data for parameters
        words = inspiration_data.get('inspiration_words', [])
        balances = dict()
        for k, v in inspiration_data.get('balances', {}).items():
            balances[k] = Decimal(str(v))
        
        # Convert balance values to parameters
        total_balance = sum(balances.values())
        balance_factor = math.log(float(total_balance) + 1) + 1  # Prevent log(0)
        
        # Parameters influenced by onchain data
        num_curves = int(50 * balance_factor)
        curve_length = int(200 * balance_factor)
        flow_scale = 0.005 * balance_factor
        line_width_base = max(1, min(5, balance_factor))
        
        # Create flow field
        seed = abs(hash(str(token_id) + str(balances)) % (2**32))
        flow_field = create_flow_field(width//20, height//20, flow_scale, 4, seed)
        
        # Theme-specific parameters
        if theme == "Geometric":
            num_curves *= 2
            curve_length //= 2
            flow_scale *= 1.5
            
        elif theme == "Abstract":
            num_curves = int(num_curves * 1.5)
            curve_length = int(curve_length * 1.2)
            
        elif theme == "Cyberpunk":
            # Add a subtle grid underlay
            grid_spacing = int(width / (10 * balance_factor))
            for x in range(0, width, grid_spacing):
                alpha = int(25 + abs(math.sin(x * 0.01)) * 25)
                grid_color = f"#{colors[1][1:3]}{colors[2][3:5]}{colors[3][5:7]}{alpha:02x}"
                draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
            for y in range(0, height, grid_spacing):
                alpha = int(25 + abs(math.sin(y * 0.01)) * 25)
                grid_color = f"#{colors[2][1:3]}{colors[3][3:5]}{colors[1][5:7]}{alpha:02x}"
                draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
        # Generate curves based on flow field
        for _ in range(num_curves):
            # Random starting position
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            
            # Select color based on position and theme
            color_index = (int(x/width * len(colors)) + int(y/height * len(colors))) % len(colors)
            color = colors[color_index]
            
            # Create curve points
            points = []
            for _ in range(curve_length):
                points.append((x, y))
                
                # Get flow field angle
                field_x, field_y = int((x/width) * len(flow_field[0])), int((y/height) * len(flow_field))
                angle = flow_field[field_y][field_x]
                
                # Move in flow direction
                step_length = random.uniform(1, 3) * balance_factor
                x += math.cos(angle) * step_length
                y += math.sin(angle) * step_length
                
                # Bounce off edges
                x = max(0, min(width-1, x))
                y = max(0, min(height-1, y))
            
            # Draw curve with varying width
            if len(points) > 1:
                for i in range(len(points)-1):
                    # Vary line width based on position and data
                    progress = i / len(points)
                    width_var = math.sin(progress * math.pi)
                    line_width = max(1, int(line_width_base * (1 + width_var)))
                    
                    # Add slight transparency for layering effect
                    alpha = int(200 + 55 * width_var)
                    line_color = f"#{color[1:7]}{alpha:02x}"
                    
                    draw.line([points[i], points[i+1]], fill=line_color, width=line_width)
        
        # Add texture overlay based on theme
        if theme in ["Nature", "Abstract"]:
            for _ in range(1000):
                x = random.randint(0, width-1)
                y = random.randint(0, height-1)
                size = random.randint(1, 3)
                alpha = random.randint(10, 40)
                texture_color = f"#{colors[-1][1:7]}{alpha:02x}"
                draw.ellipse([x-size, y-size, x+size, y+size], fill=texture_color)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=95)
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr
    except Exception as e:
        print(f"Error creating art: {str(e)}")
        # Return a simple colored square as fallback
        img = Image.new('RGB', (2048, 2048), colors[0])
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

def generate_collection(num_pieces: int, inspiration_data: dict, colors: List[str], theme: str) -> List[bytes]:
    """Generate a collection of art pieces"""
    collection = []
    for i in range(max(1, num_pieces)):  # Ensure at least 1 piece
        img_bytes = create_art(i, inspiration_data, colors, theme)
        collection.append(img_bytes)
    return collection

# Collection parameters
NUM_PIECES = ''' + str(num_pieces) + '''
COLORS = ''' + str(colors) + '''
THEME = ''' + json.dumps(theme) + '''
INSPIRATION_DATA = ''' + inspiration_json + '''

# Generate collection
collection = generate_collection(NUM_PIECES, INSPIRATION_DATA, COLORS, THEME)
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
inspo_agent = InspoAgent()
artist_agent = ArtistAgent()
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
        
        # 3. Upload all pieces and collection metadata to IPFS
        collection_metadata = {
            'name': f"{inspiration['theme']} Collection",
            'description': f"A generative art collection inspired by {inspiration['theme']}",
            'attributes': [
                {'trait_type': 'Theme', 'value': inspiration['theme']},
                {'trait_type': 'Collection Size', 'value': inspiration['num_pieces']}
            ],
            'pieces': []  # Will store metadata for each piece
        }
        
        # Upload each piece and store its metadata
        piece_hashes = []
        for i, piece in enumerate(collection):
            piece_metadata = {
                'name': f"{inspiration['theme']} #{i+1}",
                'description': f"Piece #{i+1} from {inspiration['theme']} Collection",
                'attributes': [
                    {'trait_type': 'Theme', 'value': inspiration['theme']},
                    {'trait_type': 'Piece Number', 'value': i+1}
                ]
            }
            piece_hash = image_agent.upload_to_ipfs(piece, piece_metadata)
            if not piece_hash:
                raise Exception(f"Failed to upload piece #{i+1} to IPFS")
            piece_hashes.append(piece_hash)
            collection_metadata['pieces'].append({
                'piece_number': i+1,
                'ipfs_hash': piece_hash,
                'metadata': piece_metadata
            })
        
        # Use first piece as collection cover
        collection_metadata['image'] = f"ipfs://{piece_hashes[0]}"
        
        # 4. Post to Rodeo
        collection_id = rodeo_agent.post_to_rodeo(collection_metadata)
        if not collection_id:
            raise Exception("Failed to post to Rodeo")
        
        rodeo_url = f"https://rodeo.club/collection/{collection_id}"
        print(f"Posted to Rodeo: {rodeo_url}")
        
        return {
            'inspiration': inspiration,
            'collection_id': collection_id,
            'rodeo_url': rodeo_url,
            'cover_hash': piece_hashes[0],
            'piece_hashes': piece_hashes,
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