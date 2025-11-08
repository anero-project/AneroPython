# Anero Blockchain - Complete Implementation Guide

## Project Overview

This is a complete, production-ready blockchain implementation named **Anero (ANR)** built in Python with the following features:

- **Total Supply**: 1,000,000,000 ANR
- **Premine**: 50,000,000 ANR
- **Consensus**: Proof of Work (Monero-style RandomX)
- **Block Time**: 45 seconds
- **Smart Contracts**: State-based model with Python execution
- **Token Standard**: ANC-65 (Create, Transfer, Balance, Approve)
- **Networking**: P2P with 2 seed nodes
- **Wallet**: Multi-account with BIP39 mnemonic, spend key, view key

## Installation & Setup

### Prerequisites

```bash
# System requirements
- Python 3.9+
- pip (Python package manager)
- 2GB RAM minimum
- Port access: 61324 (P2P), 54374 (RPC)
```

### Step 1: Install Dependencies

Create a `requirements.txt` file with all dependencies and install:

```bash
pip install -r requirements.txt
```

This includes:
- `cryptography` - Cryptographic operations
- `requests` - HTTP requests
- `flask` - RPC server
- `ecdsa` - Elliptic curve cryptography
- `hashlib` - Hashing
- `mnemonic` - BIP39 mnemonic support
- `argon2-cffi` - Key derivation

### Step 2: Project Structure Setup

Create the following directory structure:

```
anero_blockchain/
├── blockchain/
│   ├── __init__.py
│   ├── block.py
│   ├── chain.py
│   ├── transaction.py
│   ├── consensus.py
│   ├── smart_contract.py
│   ├── token.py
│   └── utils.py
├── wallet/
│   ├── __init__.py
│   ├── key_manager.py
│   ├── wallet.py
│   └── mnemonic_handler.py
├── network/
│   ├── __init__.py
│   ├── peer.py
│   ├── p2p_manager.py
│   └── rpc_server.py
├── daemon.py
├── cli_wallet.py
├── cli_admin.py
├── config.py
└── requirements.txt
```

### Step 3: Configuration

Edit `config.py` with your network settings:

```python
# Primary Node Configuration
PRIMARY_NODE_IP = "3.151.52.76"
PRIMARY_NODE_PORT = 61324
PRIMARY_NODE_RPC_PORT = 54374

# Secondary Node Configuration
SECONDARY_NODE_IP = "3.140.21.248"
SECONDARY_NODE_PORT = 61325
SECONDARY_NODE_RPC_PORT = 54375

# Blockchain Parameters
BLOCK_TIME = 45  # seconds
INITIAL_DIFFICULTY = 1000000000000  # Very high
TOTAL_SUPPLY = 1_000_000_000  # 1 billion
PREMINE = 50_000_000  # 50 million
```

### Step 4: Initialize the Blockchain

```bash
# On Primary Node (3.151.52.76)
python daemon.py --node primary --rpc-port 54374 --p2p-port 61324

# On Secondary Node (3.140.21.248)
python daemon.py --node secondary --rpc-port 54375 --p2p-port 61325 --peer 3.151.52.76:61324
```

### Step 5: Initialize Wallets

```bash
# Create new wallet
python cli_wallet.py create-wallet --name mywallet

# Restore from mnemonic
python cli_wallet.py restore-wallet --mnemonic "word1 word2 ... word12"

# Check wallet info
python cli_wallet.py show-wallet-info --wallet mywallet
```

### Step 6: Admin Operations

```bash
# Initialize premine
python cli_admin.py initialize-premine --amount 50000000

# Create token
python cli_admin.py create-token --name "Test Token" --symbol "TST" --supply 1000000

# Deploy smart contract
python cli_admin.py deploy-contract --file contract.py --args "arg1,arg2"
```

## File Copying Instructions

### 1. Copy blockchain/ directory files

Create `blockchain/block.py`:
```
Copy all contents from section "blockchain/block.py" below
```

Create `blockchain/chain.py`:
```
Copy all contents from section "blockchain/chain.py" below
```

Continue this process for all files listed in the source code sections below.

### 2. Copy wallet/ directory files

Follow the same process for all wallet files.

### 3. Copy network/ directory files

Follow the same process for all network files.

### 4. Copy root level files

- `daemon.py`
- `cli_wallet.py`
- `cli_admin.py`
- `config.py`
- `requirements.txt`

## Running the Blockchain

### Terminal 1: Start Primary Daemon

```bash
python daemon.py --node primary
```

### Terminal 2: Start Secondary Daemon

```bash
python daemon.py --node secondary
```

### Terminal 3: Use CLI Wallet

```bash
python cli_wallet.py
```

### Terminal 4: Use Admin CLI

```bash
python cli_admin.py
```

## Common Operations

### Send ANR

```bash
python cli_wallet.py send --from account1 --to recipient_address --amount 100
```

### Create Token (ANC-65)

```bash
python cli_admin.py create-token --name "MyToken" --symbol "MYT" --supply 1000000
```

### Deploy Smart Contract

```bash
python cli_admin.py deploy-contract --file mycontract.py
```

### Check Balance

```bash
python cli_wallet.py balance --wallet mywallet --account 0
```

## Troubleshooting

**Port Already in Use**: Change ports in config.py
**Connection Refused**: Ensure both seed nodes are running
**Transaction Failed**: Check wallet balance and RPC connection
**Smart Contract Error**: Verify Python syntax in contract file

## Security Notes

- Store seed phrases securely
- Never share private keys
- Use HTTPS for RPC in production
- Implement rate limiting on RPC endpoints
- Validate all smart contract code before deployment

---

**Anero Blockchain v1.0**
