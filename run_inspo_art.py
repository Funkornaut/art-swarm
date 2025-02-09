"""Script for generating and posting AI art to Rodeo."""

from art_agents import InspoAgent, ArtistAgent
from PIL import Image
import io
from cdp_agentkit_core.actions.rodeo.post import PostToRodeoAction
from cdp_sdk import Wallet
import logging
from typing import Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_image(img_data: bytes, filename: str) -> Path:
    """Save image data to a file.
    
    Args:
        img_data (bytes): The image data to save.
        filename (str): The filename to save to.
        
    Returns:
        Path: The path to the saved file.
    """
    try:
        img = Image.open(io.BytesIO(img_data))
        filepath = Path(filename)
        img.save(filepath)
        logger.info(f"Saved image as '{filepath}'")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        raise

def post_art_to_rodeo(
    wallet: Wallet,
    ipfs_hash: str,
    name: str,
    description: str,
    category: Optional[str] = None
) -> Optional[str]:
    """Post art to Rodeo.
    
    Args:
        wallet (Wallet): The wallet to use for posting.
        ipfs_hash (str): The IPFS hash of the image.
        name (str): The name of the post.
        description (str): The description of the post.
        category (Optional[str]): Optional category for the post.
        
    Returns:
        Optional[str]: The result message if successful, None if failed.
    """
    try:
        rodeo_action = PostToRodeoAction()
        result = rodeo_action.func(
            wallet=wallet,
            image_uri=f"ipfs://{ipfs_hash}",
            name=name,
            description=description,
            category=category
        )
        logger.info(f"Posted to Rodeo: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to post to Rodeo: {e}")
        return None

def run_art_generation():
    """Run the art generation and posting process."""
    try:
        # Create instances of agents
        logger.info("Initializing agents...")
        inspo_agent = InspoAgent()
        artist_agent = ArtistAgent()
        
        # Get inspiration from InspoAgent
        logger.info("Getting onchain inspiration...")
        inspiration = inspo_agent.get_onchain_inspiration()
        logger.info(f"Generated inspiration: {inspiration}")
        
        # Generate art script using ArtistAgent
        logger.info("Generating art script...")
        script = artist_agent.generate_art_script(inspiration)
        
        # Execute the script to create art
        logger.info("Executing art script...")
        collection = artist_agent.execute_script(script)
        logger.info(f"Generated {len(collection)} pieces")
        
        # Get wallet for posting to Rodeo
        logger.info("Creating wallet...")
        wallet = Wallet.create()  # Or use your existing wallet management
        
        # Save and post each piece
        if collection:
            for i, piece_bytes in enumerate(collection[:3]):  # Post first 3 pieces
                try:
                    # Save locally
                    filename = f'generated_art_{i+1}.png'
                    save_image(piece_bytes, filename)
                    
                    # Upload to IPFS using your existing image_agent
                    metadata = {
                        'name': f"{inspiration['theme']} #{i+1}",
                        'description': (
                            f"AI-generated art inspired by {inspiration['theme']} "
                            f"and onchain data. Created with themes: {', '.join(inspiration['inspiration_words'])}"
                        ),
                        'attributes': [
                            {'trait_type': 'Theme', 'value': inspiration['theme']},
                            {'trait_type': 'Piece Number', 'value': i+1},
                            {'trait_type': 'Inspiration', 'value': inspiration['inspiration_words'][0]}
                        ]
                    }
                    
                    logger.info(f"Uploading piece {i+1} to IPFS...")
                    ipfs_hash = image_agent.upload_to_ipfs(piece_bytes, metadata)
                    
                    if ipfs_hash:
                        # Post to Rodeo
                        result = post_art_to_rodeo(
                            wallet=wallet,
                            ipfs_hash=ipfs_hash,
                            name=metadata['name'],
                            description=metadata['description'],
                            category="AI Art"
                        )
                        
                        if not result:
                            logger.error(f"Failed to post piece {i+1} to Rodeo")
                    else:
                        logger.error(f"Failed to upload piece {i+1} to IPFS")
                
                except Exception as e:
                    logger.error(f"Error processing piece {i+1}: {e}")
                    continue
        else:
            logger.error("No art pieces were generated")
    
    except Exception as e:
        logger.error(f"Error in art generation process: {e}")
        raise

if __name__ == "__main__":
    try:
        run_art_generation()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise