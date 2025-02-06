# 🔵 Based Agent

An experimental playground for autonomous onchain interactions, and the starting point of the autonomous onchain agent revolution. 

## Introduction

Based Agent helps LLM agents directly interact with the blockchain, built on top of the [Coinbase Developer Platform (CDP)](https://cdp.coinbase.com/) and OpenAI's [Swarm](https://github.com/openai/swarm). This is meant to be a template where anyone can add their own features and functions that can be autonomously executed by an agent with access to the entire onchain ecosystem.

### Key Features

- **Autonomous execution**: The agent thinks, decides, and acts onchain autonomously.
- **Token deployment**: Create and manage ERC-20 tokens.
- **NFT Deployment**: Deploy and mint NFTs. 
- **Asset transfers**: Transfer assets between addresses without manual intervention.
- **Balance checks**: Keep tabs on wallet balances.
- **ETH faucet requests**: Automatically request testnet ETH when needed.
- **Art generation via DALL-E**: Generate artwork using AI.
- **Generative Art Swarm**: Create unique art collections using onchain data.
- **Whatever you want**: Add in features and share them with us!

### Why BasedAgent?

Imagine an AI agent that not only interacts with the blockchain but does so creatively and autonomously. Whether you're a developer, an artist, or someone curious about AI, Based Agent offers a unique and exciting playground to:

- Experiment with autonomous agent capabilities.
- Explore on-chain actions without manual coding.
- Create generative art collections inspired by blockchain data.
- Understand the potential of AI onchain.

## Get Started in Minutes!

### 1️⃣ Prerequisites
- Python 3.7+
- Replit Core Account (optional, but recommended for easy setup). Contact kevin.leffew@coinbase.com for a Sponsorship

### 2️⃣ API Configuration
Add your secrets to Replit's Secret Manager or set them as environment variables:
- `CDP_API_KEY_NAME`: Your CDP API key name.
- `CDP_PRIVATE_KEY`: Your CDP private key.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `ALCHEMY_API_KEY`: Your Alchemy API key (for Web3 interactions).
- `PINATA_API_KEY` and `PINATA_SECRET_KEY`: For IPFS uploads (optional).
- `RODEO_API_KEY`: For posting collections to Rodeo.club (optional).

You can get the Coinbase Developer Platform API key here: [https://portal.cdp.coinbase.com/](https://portal.cdp.coinbase.com/projects/api-keys)
And the OpenAI key here: https://platform.openai.com/api-keys (note you will need to have a paid account)

### 3️⃣ Running the Agent

After adding your API Keys to the Secrets pane, you start the agent by pressing the green "▶ Run" Button at the top of the editor

![image](image.png)

Alternatively, you can start the based agent manually by navigating to the Replit shell and running:

```bash
python run.py
```

### Watch the Magic Happen! ✨

The Based Agent will start its autonomous loop:

- Wakes up every 10 seconds.
- Chooses an onchain action based on its capabilities.
- Executes the action onchain.
- Prints results in a human-readable format.

## 🤔 How Does BasedAgent Work?

Based Agent makes decisions and interacts with the blockchain autonomously. Here's what happens under the hood:

- **Decision making**: The agent decides what action to perform next.
- **Onchain interaction**: Executes blockchain transactions using the CDP SDK.
- **Art generation**: If needed, generates art using OpenAI's DALL-E or the generative art swarm.
- **Feedback loop**: Analyzes results and plans the next action.

## 🎨 Art Agent Swarm

The Art Agent Swarm is a multi-agent system that creates unique generative art collections:

### InspoAgent
- Uses onchain data for inspiration
- Determines collection size (1-420 pieces)
- Generates color palettes from block hashes
- Selects themes based on blockchain data

### ArtistAgent
- Creates Python scripts for art generation
- Implements different artistic styles
- Uses blockchain data for deterministic randomness
- Supports multiple themes (Geometric, Abstract, Cyberpunk, Nature)

### ImageAgent (Optional)
- Handles IPFS uploads using Pinata
- Manages image and metadata storage
- Returns IPFS hashes for NFT metadata

### RodeoAgent (Optional)
- Posts collections to Rodeo.club
- Handles collection metadata
- Creates minting interfaces

## 🔧 Available Functions

Unlock a world of possibilities with these built-in functions:

### Token Operations

- `create_token(name, symbol, initial_supply)`: Create a new ERC-20 token.
- `transfer_asset(amount, asset_id, destination_address)`: Transfer assets to a specific address.
- `get_balance(asset_id)`: Check the wallet balance of a specific asset.

### NFT Operations

- `deploy_nft(name, symbol, base_uri)`: Deploy a new ERC-721 NFT contract.
- `mint_nft(contract_address, mint_to)`: Mint an NFT to a specified address.

### Art Operations

- `create_generative_collection()`: Create a new generative art collection using blockchain data.
- `generate_art(prompt)`: Generate art using DALL-E based on a text prompt.

### Utilities

- `request_eth_from_faucet()`: Request ETH from the Base Sepolia testnet faucet.

## 🤖 Agent Functionality

### Agents.py
All of the core blockchain functionality for the Based Agent resides within `agents.py`. This is the central hub where you can add new capabilities, allowing the agent to perform a wide range of tasks. 

### Art_Agents.py
Contains the art agent swarm implementation, allowing for the creation of generative art collections inspired by blockchain data.

### Run.py
Within `run.py`, you have the flexibility to engage the agent in various ways:
1. **Chat-Based Communication**: This mode enables you to have a natural language conversation with the agent, allowing it to execute tasks on your behalf through Natural Language Processing (NLP).
2. **One-Agent Autonomous Mode**: In this mode, provide the agent with a static prompt, and it will execute tasks based on its internal decision-making processes and predefined capabilities.
3. **Two-Agent Autonomous Mode**: Here, the setup involves another instance of communication, where a second agent provides dynamic prompting to the primary agent. This setup allows more complex interactions and task executions.

## 🤖 Behind the Scenes

Based Agent uses:

- **Coinbase Developer Platform SDK**: For seamless onchain interactions.
- **OpenAI Swarm**: Powers the agent's autonomous decision-making.
- **DALL-E & PIL**: Generates and manipulates artwork.
- **Web3.py**: Interacts with blockchain data.
- **Pinata**: IPFS storage solution.

## Next Steps
- Feel free to fork this repl, and remix or extend it.
- Add more themes to the art generation.
- Implement additional art styles.
- Create your own agent types.
- Add a front-end interface.

## ⚠️ Disclaimer

This project is for educational purposes only. Do not use with real assets or in production environments. Always exercise caution when interacting with blockchain technologies.

## 🙌 Contributing

We welcome contributions! If you have ideas, suggestions, or find issues, feel free to:

- Open an issue on our main GitHub repository: [Swarm-CDP-SDK](https://github.com/murrlincoln/Swarm-CDP-SDK).
- Submit a pull request with your enhancements.

## 🤞 Contact & Support

Have questions or need assistance?

- **Lincoln Murr**: [lincoln.murr@coinbase.com](mailto:lincoln.murr@coinbase.com)
- **Kevin Leffew**: [kevin@replit.com](mailto:kevin@replit.com)

## 📚 Additional Resources

- **Coinbase Developer Platform**: [Documentation]([https://developers.coinbase.com](https://portal.cdp.coinbase.com/projects/api-keys))
- **OpenAI Swarm**: [Learn More](https://www.openai.com)
- **Base**: [Explore Base](https://base.org)

## ❤️ Acknowledgements

Based Agent is made possible thanks to:

- **Coinbase Developer Platform SDK**: [Documentation](https://docs.cdp.coinbase.com/cdp-apis/docs/welcome)
- **OpenAI Swarm (experimental)**: [Documentation](https://github.com/openai/swarm)
- **Community Contributors**

Unleash the power of AI on the blockchain with BasedAgent! 🚀

Happy Building! 👩‍💻👨‍💻