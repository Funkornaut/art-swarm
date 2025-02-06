import pytest
from art_agents import InspoAgent
from decimal import Decimal
from unittest.mock import patch, MagicMock

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