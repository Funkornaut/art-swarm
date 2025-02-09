"""Tests for the Rodeo post action."""

import pytest
from unittest.mock import patch, MagicMock
from web3 import Web3

from cdp_agentkit_core.actions.rodeo.post import (
    PostToRodeoAction,
    PostToRodeoInput,
    initialize_collection,
    create_token,
    create_sale,
    post_to_rodeo,
)
from cdp_agentkit_core.actions.rodeo.config import config, NETWORK_CONFIGS

@pytest.fixture
def mock_wallet():
    """Create a mock wallet for testing."""
    wallet = MagicMock()
    wallet.network_id = "base-sepolia"
    wallet.default_address.address_id = "0x1234567890123456789012345678901234567890"
    return wallet

@pytest.fixture
def mock_tx_receipt():
    """Create a mock transaction receipt with collection address in logs."""
    receipt = MagicMock()
    # Mock the collection creation event log
    log = MagicMock()
    log.topics = [
        "0x1234",  # Event signature
        "0x0000000000000000000000001234567890123456789012345678901234567890"  # Collection address
    ]
    receipt.logs = [log]
    return receipt

@pytest.fixture
def mock_tx():
    """Create a mock transaction."""
    tx = MagicMock()
    tx.transaction.transaction_hash = "0xabcd"
    tx.transaction.transaction_link = "https://sepolia.basescan.org/tx/0xabcd"
    return tx

def test_post_to_rodeo_input_validation():
    """Test input validation for PostToRodeoInput."""
    # Test valid input
    valid_input = PostToRodeoInput(
        image_uri="ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq",
        name="Test Post",
        description="Test Description",
        category="Art"
    )
    assert valid_input.image_uri.startswith("ipfs://")
    assert valid_input.name == "Test Post"
    assert valid_input.category == "Art"

    # Test invalid IPFS URI
    with pytest.raises(ValueError, match="Image URI must start with ipfs://"):
        PostToRodeoInput(
            image_uri="https://example.com/image.png",
            name="Test Post",
            description="Test Description"
        )

    # Test empty name
    with pytest.raises(ValueError, match="Name cannot be empty or just whitespace"):
        PostToRodeoInput(
            image_uri="ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq",
            name="   ",
            description="Test Description"
        )

    # Test name too long
    with pytest.raises(ValueError):
        PostToRodeoInput(
            image_uri="ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq",
            name="a" * 101,
            description="Test Description"
        )

def test_initialize_collection(mock_wallet, mock_tx_receipt, mock_tx):
    """Test collection initialization."""
    # Mock the contract invocations
    mock_wallet.invoke_contract.return_value.wait.return_value = mock_tx_receipt

    # Test first-time initialization
    collection_address = initialize_collection(mock_wallet)
    assert collection_address == "0x1234567890123456789012345678901234567890"
    assert mock_wallet.invoke_contract.call_count == 2  # createCollection and grantMinter

    # Test cached collection address
    collection_address = initialize_collection(mock_wallet)
    assert collection_address == "0x1234567890123456789012345678901234567890"
    assert mock_wallet.invoke_contract.call_count == 2  # Should not call again

def test_create_token(mock_wallet, mock_tx):
    """Test token creation."""
    mock_wallet.invoke_contract.return_value.wait.return_value = mock_tx

    metadata = {
        "name": "Test Post",
        "description": "Test Description",
        "image": "ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq"
    }

    token_id = create_token(
        mock_wallet,
        "0x1234567890123456789012345678901234567890",
        metadata
    )

    assert isinstance(token_id, int)
    mock_wallet.invoke_contract.assert_called_once()

def test_create_sale(mock_wallet, mock_tx):
    """Test sale creation."""
    mock_wallet.invoke_contract.return_value.wait.return_value = mock_tx

    tx_hash = create_sale(
        mock_wallet,
        "0x1234567890123456789012345678901234567890",
        123
    )

    assert tx_hash == "0xabcd"
    mock_wallet.invoke_contract.assert_called_once()

def test_post_to_rodeo_full_flow(mock_wallet, mock_tx_receipt, mock_tx):
    """Test the complete post to Rodeo flow."""
    # Mock all contract interactions
    mock_wallet.invoke_contract.return_value.wait.side_effect = [
        mock_tx_receipt,  # Collection creation
        mock_tx,         # Grant minter
        mock_tx,         # Token creation
        mock_tx          # Sale creation
    ]

    result = post_to_rodeo(
        mock_wallet,
        "ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq",
        "Test Post",
        "Test Description",
        "Art"
    )

    assert "Successfully posted to Rodeo" in result
    assert "Collection Address:" in result
    assert "Token ID:" in result
    assert "Sale Transaction:" in result
    assert "Post URL:" in result
    assert "Transaction URL:" in result
    assert mock_wallet.invoke_contract.call_count == 4

def test_post_to_rodeo_error_handling(mock_wallet):
    """Test error handling in post to Rodeo."""
    # Mock contract invocation failure
    mock_wallet.invoke_contract.side_effect = Exception("Contract call failed")

    result = post_to_rodeo(
        mock_wallet,
        "ipfs://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq",
        "Test Post",
        "Test Description"
    )

    assert "Error posting to Rodeo" in result

def test_network_config_handling():
    """Test network configuration handling."""
    # Test mainnet config
    mainnet_config = config.get_network_config("base-mainnet")
    assert mainnet_config["factory_address"] == NETWORK_CONFIGS["base-mainnet"]["factory_address"]
    assert mainnet_config["drop_market_address"] == NETWORK_CONFIGS["base-mainnet"]["drop_market_address"]

    # Test testnet config
    testnet_config = config.get_network_config("base-sepolia")
    assert testnet_config["factory_address"] == NETWORK_CONFIGS["base-sepolia"]["factory_address"]
    assert testnet_config["drop_market_address"] == NETWORK_CONFIGS["base-sepolia"]["drop_market_address"]

    # Test invalid network
    with pytest.raises(ValueError, match="Unsupported network"):
        config.get_network_config("invalid-network")

def test_integration_with_art_agents():
    """Test integration with art generation system."""
    from art_agents import InspoAgent, ArtistAgent, IpfsAgent
    
    # Create mock image data
    mock_image_data = b"fake_image_data"
    mock_ipfs_hash = "bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq"
    
    # Mock the agents
    with patch('art_agents.InspoAgent.get_onchain_inspiration') as mock_inspo, \
         patch('art_agents.ArtistAgent.execute_script') as mock_artist, \
         patch('art_agents.IpfsAgent.upload_to_ipfs') as mock_ipfs, \
         patch('cdp_sdk.Wallet.create') as mock_wallet_create:
        
        # Setup mocks
        mock_inspo.return_value = {
            'theme': 'Abstract',
            'num_pieces': 1,
            'color_palette': ['#FF0000'],
            'inspiration_words': ['flow']
        }
        mock_artist.return_value = [mock_image_data]
        mock_ipfs.return_value = mock_ipfs_hash
        
        # Create mock wallet
        mock_wallet = MagicMock()
        mock_wallet.network_id = "base-sepolia"
        mock_wallet.default_address.address_id = "0x1234"
        mock_wallet_create.return_value = mock_wallet
        
        # Create action instance
        action = PostToRodeoAction()
        
        # Test posting art
        result = action.func(
            wallet=mock_wallet,
            image_uri=f"ipfs://{mock_ipfs_hash}",
            name="Abstract Art #1",
            description="AI-generated artwork",
            category="AI Art"
        )
        
        assert "Successfully posted to Rodeo" in result
        assert "base-sepolia" in result 