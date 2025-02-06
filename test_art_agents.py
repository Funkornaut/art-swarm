import pytest
from PIL import Image
import io
import json
from unittest.mock import patch, MagicMock
from decimal import Decimal
from art_agents import ArtistAgent, InspoAgent

def test_inspo_agent():
    # Create an instance of InspoAgent
    agent = InspoAgent()
    
    # Test getting inspiration
    inspiration = agent.get_onchain_inspiration()
    
    # Check if the inspiration has all required fields
    assert 'num_pieces' in inspiration
    assert 'color_palette' in inspiration
    assert 'theme' in inspiration
    assert 'inspiration_words' in inspiration
    assert 'timestamp' in inspiration
    assert 'balances' in inspiration
    
    # Check if color palette has exactly 5 colors
    assert len(inspiration['color_palette']) == 5
    
    # Check if number of pieces is within expected range
    assert 1 <= inspiration['num_pieces'] <= 420
    
    # Check if theme is one of the expected themes
    expected_themes = [
        "Cyberpunk", "Nature", "Abstract", "Geometric", 
        "Space", "Ocean", "Urban", "Minimal"
    ]
    assert inspiration['theme'] in expected_themes
    
    # Check if we have inspiration words
    assert isinstance(inspiration['inspiration_words'], list)
    assert 3 <= len(inspiration['inspiration_words']) <= 5

def test_get_wallet_balances():
    agent = InspoAgent()
    
    # Test balance retrieval
    balances = agent._get_wallet_balances()
    
    # Check if we have balances for all expected assets
    expected_assets = ["eth", "usdc"] + list(agent.contracts.values())
    assert all(asset in balances for asset in expected_assets)
    
    # Check if all balances are Decimal objects
    assert all(isinstance(balance, Decimal) for balance in balances.values())

def test_color_palette_generation():
    agent = InspoAgent()
    
    # Create sample balance data
    sample_balances = {
        'eth': Decimal('1.5'),
        'usdc': Decimal('100'),
        'contract1': Decimal('0'),
        'contract2': Decimal('50')
    }
    
    colors = agent._generate_color_palette_from_data(sample_balances)
    
    # Check if we get exactly 5 colors
    assert len(colors) == 5
    
    # Check if each color is a valid hex color code
    for color in colors:
        assert color.startswith('#')
        assert len(color) == 7  # #RRGGBB format
        # Verify the hex string is valid
        int(color[1:], 16)  # This will raise ValueError if invalid hex

def test_theme_determination():
    agent = InspoAgent()
    
    # Test with different balance scenarios
    test_cases = [
        {'eth': Decimal('0')},
        {'eth': Decimal('1.5'), 'usdc': Decimal('1000')},
        {'eth': Decimal('0.1'), 'usdc': Decimal('50'), 'contract1': Decimal('10')}
    ]
    
    for balances in test_cases:
        theme = agent._determine_theme_from_balances(balances)
        assert theme in [
            "Cyberpunk", "Nature", "Abstract", "Geometric", 
            "Space", "Ocean", "Urban", "Minimal"
        ]

def test_inspiration_words():
    agent = InspoAgent()
    
    # Test word generation for each theme
    sample_balances = {'eth': Decimal('1.0')}
    themes = [
        "Cyberpunk", "Nature", "Abstract", "Geometric", 
        "Space", "Ocean", "Urban", "Minimal"
    ]
    
    for theme in themes:
        words = agent._generate_inspiration_words(sample_balances, theme)
        assert isinstance(words, list)
        assert 3 <= len(words) <= 5
        # Check if words are from the theme's word list
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
        assert all(word in theme_words[theme] for word in words)

def test_error_handling():
    agent = InspoAgent()
    
    # Test with invalid contract address
    invalid_balances = {
        'eth': Decimal('1.0'),
        'invalid_contract': Decimal('0')
    }
    
    # Should not raise an exception and should return valid colors
    colors = agent._generate_color_palette_from_data(invalid_balances)
    assert len(colors) == 5
    assert all(color.startswith('#') for color in colors)
    
    # Test with empty balances
    empty_balances = {}
    theme = agent._determine_theme_from_balances(empty_balances)
    assert theme in [
        "Cyberpunk", "Nature", "Abstract", "Geometric", 
        "Space", "Ocean", "Urban", "Minimal"
    ]

@patch('art_agents.art_wallet')
def test_cdp_integration(mock_wallet):
    # Mock the wallet's balance method
    mock_wallet.balance.return_value = Decimal('1.5')
    
    agent = InspoAgent()
    inspiration = agent.get_onchain_inspiration()
    
    # Verify that the wallet's balance method was called
    assert mock_wallet.balance.called
    
    # Check that we got valid inspiration despite using mocked data
    assert isinstance(inspiration, dict)
    assert all(key in inspiration for key in [
        'num_pieces', 'color_palette', 'theme', 
        'inspiration_words', 'timestamp', 'balances'
    ])

def test_generate_art_script():
    """Test that the art script is generated correctly"""
    agent = ArtistAgent()
    inspiration = {
        'num_pieces': 1,
        'color_palette': ['#000000', '#FFFFFF'],
        'theme': 'Abstract',
        'inspiration_words': ['flow', 'organic'],
        'balances': {'eth': Decimal('1.0')}
    }
    
    script = agent.generate_art_script(inspiration)
    
    # Check that the script contains all necessary components
    assert 'def create_flow_field' in script
    assert 'def create_art' in script
    assert 'def generate_collection' in script
    assert 'OpenSimplex' in script
    assert 'collection = generate_collection' in script

def test_execute_script():
    """Test that the script execution produces valid image data"""
    agent = ArtistAgent()
    inspiration = {
        'num_pieces': 1,
        'color_palette': ['#000000', '#FFFFFF'],
        'theme': 'Abstract',
        'inspiration_words': ['flow', 'organic'],
        'balances': {'eth': Decimal('1.0')}
    }
    
    script = agent.generate_art_script(inspiration)
    collection = agent.execute_script(script)
    
    # Check that we got the expected number of images
    assert len(collection) == 1
    
    # Check that each item is valid image data
    for img_data in collection:
        assert isinstance(img_data, bytes)
        # Verify it's a valid image
        img = Image.open(io.BytesIO(img_data))
        assert img.size == (2048, 2048)
        assert img.mode == 'RGB'

def test_art_generation_with_different_themes():
    """Test art generation with different themes"""
    agent = ArtistAgent()
    themes = ['Abstract', 'Geometric', 'Cyberpunk', 'Nature']
    
    for theme in themes:
        inspiration = {
            'num_pieces': 1,
            'color_palette': ['#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF'],
            'theme': theme,
            'inspiration_words': ['flow', 'organic'],
            'balances': {'eth': Decimal('1.0')}
        }
        
        script = agent.generate_art_script(inspiration)
        collection = agent.execute_script(script)
        
        assert len(collection) == 1
        img = Image.open(io.BytesIO(collection[0]))
        assert img.size == (2048, 2048)

def test_error_handling():
    """Test error handling in art generation"""
    agent = ArtistAgent()
    
    # Test with invalid color format
    inspiration = {
        'num_pieces': 1,
        'color_palette': ['invalid_color'],
        'theme': 'Abstract',
        'inspiration_words': ['flow'],
        'balances': {'eth': Decimal('1.0')}
    }
    
    script = agent.generate_art_script(inspiration)
    collection = agent.execute_script(script)
    
    # Should still produce an image (fallback to black)
    assert len(collection) == 1
    img = Image.open(io.BytesIO(collection[0]))
    assert img.size == (2048, 2048)

def test_multiple_pieces():
    """Test generating multiple pieces"""
    agent = ArtistAgent()
    inspiration = {
        'num_pieces': 3,
        'color_palette': ['#000000', '#FFFFFF'],
        'theme': 'Abstract',
        'inspiration_words': ['flow', 'organic'],
        'balances': {'eth': Decimal('1.0')}
    }
    
    script = agent.generate_art_script(inspiration)
    collection = agent.execute_script(script)
    
    assert len(collection) == 3
    for img_data in collection:
        img = Image.open(io.BytesIO(img_data))
        assert img.size == (2048, 2048)

def test_integration_with_inspo_agent():
    """Test integration between InspoAgent and ArtistAgent"""
    with patch('art_agents.InspoAgent._get_wallet_balances') as mock_balances:
        # Mock wallet balances
        mock_balances.return_value = {'eth': Decimal('1.0')}
        
        inspo_agent = InspoAgent()
        artist_agent = ArtistAgent()
        
        # Get inspiration from InspoAgent
        inspiration = inspo_agent.get_onchain_inspiration()
        
        # Generate art using the inspiration
        script = artist_agent.generate_art_script(inspiration)
        collection = artist_agent.execute_script(script)
        
        assert len(collection) > 0
        img = Image.open(io.BytesIO(collection[0]))
        assert img.size == (2048, 2048)