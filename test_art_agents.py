import pytest
from PIL import Image
import io
import json
from unittest.mock import patch, MagicMock
from decimal import Decimal
from art_agents import ArtistAgent, InspoAgent, IpfsAgent

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

@pytest.fixture
def mock_ipfs_agent():
    """Create a mock IPFS agent with mocked responses"""
    with patch('art_agents.IpfsAgent') as mock_agent:
        # Mock successful image upload response
        mock_agent.return_value.pinata_api_endpoint = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        mock_agent.return_value.pinata_json_endpoint = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        return mock_agent.return_value

@pytest.fixture
def sample_image_bytes():
    """Create a sample image for testing"""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_ipfs_agent_initialization():
    """Test IPFS agent initialization and environment variable checking"""
    with patch.dict('os.environ', {'PINATA_JWT': 'test_jwt'}):
        agent = IpfsAgent()
        assert agent.pinata_jwt == 'test_jwt'
        assert agent.pinata_api_endpoint == "https://api.pinata.cloud/pinning/pinFileToIPFS"
        assert agent.pinata_json_endpoint == "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    # Test missing JWT
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="PINATA_JWT environment variable is required"):
            IpfsAgent()

@patch('requests.post')
def test_ipfs_image_upload(mock_post, sample_image_bytes):
    """Test uploading an image to IPFS"""
    # Mock successful image upload response
    mock_post.return_value.json.return_value = {'IpfsHash': 'test_image_hash'}
    mock_post.return_value.raise_for_status = lambda: None

    with patch.dict('os.environ', {'PINATA_JWT': 'test_jwt'}):
        agent = IpfsAgent()
        metadata = {
            'name': 'Test Art #1',
            'description': 'Test art piece',
            'attributes': [{'trait_type': 'Theme', 'value': 'Abstract'}]
        }
        
        result = agent.upload_to_ipfs(sample_image_bytes, metadata)
        
        # Verify the image upload request
        assert mock_post.call_count == 2  # One for image, one for metadata
        image_call = mock_post.call_args_list[0]
        assert image_call[0][0] == agent.pinata_api_endpoint
        assert 'file' in image_call[1]['files']
        assert image_call[1]['files']['file'][0] == 'art.png'
        assert image_call[1]['files']['file'][1] == sample_image_bytes
        assert image_call[1]['headers'] == {'Authorization': 'Bearer test_jwt'}

@patch('requests.post')
def test_ipfs_metadata_upload(mock_post, sample_image_bytes):
    """Test uploading metadata to IPFS"""
    # Mock successful upload responses
    mock_post.side_effect = [
        type('Response', (), {
            'json': lambda: {'IpfsHash': 'test_image_hash'},
            'raise_for_status': lambda: None
        }),
        type('Response', (), {
            'json': lambda: {'IpfsHash': 'test_metadata_hash'},
            'raise_for_status': lambda: None
        })
    ]

    with patch.dict('os.environ', {'PINATA_JWT': 'test_jwt'}):
        agent = IpfsAgent()
        metadata = {
            'name': 'Test Art #1',
            'description': 'Test art piece',
            'attributes': [{'trait_type': 'Theme', 'value': 'Abstract'}]
        }
        
        result = agent.upload_to_ipfs(sample_image_bytes, metadata)
        
        # Verify the metadata upload request
        metadata_call = mock_post.call_args_list[1]
        assert metadata_call[0][0] == agent.pinata_json_endpoint
        uploaded_metadata = metadata_call[1]['json']
        
        # Verify metadata format matches Rodeo requirements
        assert 'name' in uploaded_metadata
        assert 'description' in uploaded_metadata
        assert 'image' in uploaded_metadata
        assert uploaded_metadata['image'] == f"ipfs://test_image_hash"
        assert result == 'test_metadata_hash'

@patch('requests.post')
def test_ipfs_upload_error_handling(mock_post):
    """Test error handling during IPFS uploads"""
    # Mock failed upload
    mock_post.side_effect = Exception("Upload failed")

    with patch.dict('os.environ', {'PINATA_JWT': 'test_jwt'}):
        agent = IpfsAgent()
        metadata = {
            'name': 'Test Art #1',
            'description': 'Test art piece'
        }
        
        result = agent.upload_to_ipfs(b'fake_image_data', metadata)
        assert result is None

def test_ipfs_integration_with_art_generation():
    """Test integration between ArtistAgent and IpfsAgent"""
    artist_agent = ArtistAgent()
    inspiration = {
        'num_pieces': 1,
        'color_palette': ['#000000', '#FFFFFF'],
        'theme': 'Abstract',
        'inspiration_words': ['flow', 'organic'],
        'balances': {'eth': Decimal('1.0')}
    }
    
    # Generate art
    script = artist_agent.generate_art_script(inspiration)
    collection = artist_agent.execute_script(script)
    
    # Mock IPFS upload
    with patch('requests.post') as mock_post:
        mock_post.side_effect = [
            type('Response', (), {
                'json': lambda: {'IpfsHash': 'test_image_hash'},
                'raise_for_status': lambda: None
            }),
            type('Response', (), {
                'json': lambda: {'IpfsHash': 'test_metadata_hash'},
                'raise_for_status': lambda: None
            })
        ]
        
        with patch.dict('os.environ', {'PINATA_JWT': 'test_jwt'}):
            agent = IpfsAgent()
            metadata = {
                'name': 'Abstract #1',
                'description': 'Piece #1 from Abstract Collection',
                'attributes': [
                    {'trait_type': 'Theme', 'value': 'Abstract'},
                    {'trait_type': 'Piece Number', 'value': 1}
                ]
            }
            
            result = agent.upload_to_ipfs(collection[0], metadata)
            
            # Verify the upload process
            assert mock_post.call_count == 2
            assert result == 'test_metadata_hash'
            
            # Verify the uploaded metadata format
            metadata_call = mock_post.call_args_list[1]
            uploaded_metadata = metadata_call[1]['json']
            assert uploaded_metadata['image'] == 'ipfs://test_image_hash'
            assert 'name' in uploaded_metadata
            assert 'description' in uploaded_metadata
            assert 'attributes' in uploaded_metadata