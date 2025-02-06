import pytest
from PIL import Image
import io
import json
from unittest.mock import patch, MagicMock
from decimal import Decimal
from art_agents import ArtistAgent, InspoAgent
import math

# Mock the CDP wallet and configuration
@pytest.fixture(autouse=True)
def mock_cdp():
    with patch('art_agents.Cdp.configure') as mock_configure, \
         patch('art_agents.Wallet.create') as mock_create, \
         patch('art_agents.art_wallet') as mock_wallet:
        
        mock_wallet.balance.return_value = Decimal('1.0')
        mock_wallet.default_address = MagicMock()
        mock_wallet.default_address.address_id = "0x123"
        yield mock_wallet

def create_mock_inspiration():
    """Create mock inspiration data for testing"""
    return {
        'num_pieces': 2,  # Small number for faster tests
        'color_palette': ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'],
        'theme': 'Abstract',
        'inspiration_words': ['flow', 'energy', 'motion'],
        'timestamp': 1234567890,
        'balances': {
            'eth': Decimal('1.5'),
            'usdc': Decimal('100'),
            '0x420dd381b31aef6683db6b902084cb0ffece40da': Decimal('0'),
            '0x940181a94a35a4569e4529a3cdfb74e38fd98631': Decimal('50'),
            '0x827922686190790b37229fd06084350e74485b72': Decimal('10')
        }
    }

def test_art_script_generation():
    """Test that the art script is generated correctly"""
    artist = ArtistAgent()
    inspiration = create_mock_inspiration()
    
    script = artist.generate_art_script(inspiration)
    
    # Check that the script contains essential components
    assert 'create_flow_field' in script
    assert 'create_art' in script
    assert 'generate_collection' in script
    assert inspiration['theme'] in script
    assert str(inspiration['num_pieces']) in script
    assert all(color in script for color in inspiration['color_palette'])

def test_art_generation():
    # Create instances of both agents
    inspo_agent = InspoAgent()
    artist_agent = ArtistAgent()
    
    # Get inspiration from InspoAgent
    inspiration = inspo_agent.get_onchain_inspiration()
    print("Generated inspiration:", inspiration)
    
    # Generate art script using ArtistAgent
    script = artist_agent.generate_art_script(inspiration)
    print("\nGenerated art script")
    
    # Execute the script to create art
    collection = artist_agent.execute_script(script)
    print(f"\nGenerated {len(collection)} pieces")
    
    # Save the first piece to see the result
    if collection:
        img = Image.open(io.BytesIO(collection[0]))
        img.save('generated_art.png')
        print("\nSaved first piece as 'generated_art.png'")

def test_theme_variations():
    """Test that different themes produce different results"""
    artist = ArtistAgent()
    inspiration = create_mock_inspiration()
    
    # Test each theme
    themes = ["Cyberpunk", "Nature", "Abstract", "Geometric"]
    results = {}
    
    for theme in themes:
        inspiration['theme'] = theme
        script = artist.generate_art_script(inspiration)
        collection = artist.execute_script(script)
        results[theme] = collection[0]  # Store first image from each theme
    
    # Check that themes produce different images
    image_hashes = set()
    for theme, img_bytes in results.items():
        img_hash = hash(img_bytes)
        assert img_hash not in image_hashes, f"Theme {theme} produced duplicate image"
        image_hashes.add(img_hash)

def test_balance_influence():
    """Test that different balance values influence the art"""
    artist = ArtistAgent()
    inspiration = create_mock_inspiration()
    
    # Test with different balance scenarios
    balance_scenarios = [
        {'eth': Decimal('0.1'), 'usdc': Decimal('10')},
        {'eth': Decimal('10'), 'usdc': Decimal('1000')},
    ]
    
    results = []
    for balances in balance_scenarios:
        inspiration['balances'] = balances
        script = artist.generate_art_script(inspiration)
        collection = artist.execute_script(script)
        results.append(collection[0])
    
    # Check that different balances produce different images
    assert hash(results[0]) != hash(results[1]), "Different balances should produce different art"

def test_error_handling():
    """Test error handling in art generation"""
    artist = ArtistAgent()
    
    # Test with invalid inspiration data
    invalid_inspiration = {
        'num_pieces': -1,  # Invalid number
        'color_palette': ['#FF0000'],  # Not enough colors
        'theme': 'InvalidTheme',
        'inspiration_words': [],
        'timestamp': 0,
        'balances': {}
    }
    
    script = artist.generate_art_script(invalid_inspiration)
    collection = artist.execute_script(script)
    
    # Should handle errors gracefully and still produce a fallback image
    assert isinstance(collection, list)
    assert len(collection) == 1  # Should produce one fallback image
    
    # Verify the fallback image is valid
    img = Image.open(io.BytesIO(collection[0]))
    assert img.size == (2048, 2048)
    assert img.mode == 'RGB'
    assert img.getpixel((0, 0)) == (255, 0, 0)  # Should be red (#FF0000)

def test_flow_field_generation():
    """Test the flow field generation specifically"""
    artist = ArtistAgent()
    inspiration = create_mock_inspiration()
    
    script = artist.generate_art_script(inspiration)
    
    # Extract and test the flow field function
    namespace = {}
    exec(script, namespace)
    
    # Create a small flow field
    flow_field = namespace['create_flow_field'](20, 20, 0.1, 2, 42)
    
    # Check flow field properties
    assert len(flow_field) == 20  # Height
    assert len(flow_field[0]) == 20  # Width
    assert all(isinstance(angle, float) for row in flow_field for angle in row)
    assert all(-2*math.pi <= angle <= 2*math.pi for row in flow_field for angle in row)

def test_art_determinism():
    """Test that the same inputs produce the same art"""
    artist = ArtistAgent()
    inspiration = create_mock_inspiration()
    
    # Generate art twice with same inspiration
    script1 = artist.generate_art_script(inspiration)
    collection1 = artist.execute_script(script1)
    
    script2 = artist.generate_art_script(inspiration)
    collection2 = artist.execute_script(script2)
    
    # Check that both generations produced identical results
    assert len(collection1) == len(collection2)
    for img1, img2 in zip(collection1, collection2):
        assert hash(img1) == hash(img2), "Art generation should be deterministic"

if __name__ == '__main__':
    pytest.main([__file__]) 