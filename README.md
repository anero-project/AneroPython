# ANERO BLOCKCHAIN - COMPLETE SETUP & DEPLOYMENT GUIDE

## ✅ Quick Start (5 Minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Directory Structure

```bash
mkdir -p anero_blockchain
cd anero_blockchain
```

### 3. Copy All Files

Copy all the Python files into your `anero_blockchain` directory:
- `config.py`
- `blockchain_*.py` (utils, transaction, block, chain, token, smart_contract)
- `wallet_*.py` (key_manager, wallet)
- `network_*.py` (p2p_manager, rpc_server)
- `daemon.py`
- `cli_wallet.py`
- `cli_admin.py`
- `requirements.txt`

### 4. Start the Daemon (Terminal 1)

```bash
python daemon.py --node primary
```

You should see:
```
============================================================
  ANERO BLOCKCHAIN DAEMON
  Node Type: PRIMARY
  RPC Port: 54374
  P2P Port: 61324
============================================================

✓ Creating premine wallet...
✓ Genesis block created
  Premine address: [ADDRESS]
  Premine amount: 50000000 ANR
  Mnemonic: [12-WORD PHRASE]

✓ P2P server started on 3.151.52.76:61324
✓ RPC server started on port 54374
✓ Mining started
```

### 5. Create a Wallet (Terminal 2)

```bash
python cli_wallet.py create-wallet --name mywalletname
```

Output:
```
✓ Wallet 'mywalletname' created successfully

📝 MNEMONIC (Keep this safe!):
   word1 word2 word3 ... word12

📮 Primary Address: [ADDRESS]
🔑 Spend Key: [KEY]
👁️  View Key: [KEY]
```

### 6. Check Wallet Info (Terminal 2)

```bash
python cli_wallet.py show-wallet-info --wallet mywalletname
```

### 7. Check Blockchain Status (Terminal 3)

```bash
python cli_admin.py status
```

---

## 🚀 Detailed Deployment Guide

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Anero Blockchain Network            │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Primary Node    │  │ Secondary Node   │ │
│  │ 3.151.52.76:     │  │ 3.140.21.248:    │ │
│  │ RPC: 54374       │  │ RPC: 54375       │ │
│  │ P2P: 61324       │  │ P2P: 61325       │ │
│  └──────────────────┘  └──────────────────┘ │
│        ▲                      ▲              │
│        └──────────────────────┘              │
│           P2P Sync Network                   │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │      Wallet Clients (Multiple)       │  │
│  │  - CLI Wallet (cli_wallet.py)        │  │
│  │  - Admin CLI (cli_admin.py)          │  │
│  └──────────────────────────────────────┘  │
│                                              │
└─────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **Blockchain Core** (`blockchain_*.py`)
- **Block**: Block structure with PoW mining
- **Chain**: Main blockchain with state management
- **Transaction**: Standard & special transaction types
- **Token**: ANC-65 token standard implementation
- **SmartContract**: Python-based contract execution
- **Utils**: Cryptographic functions

#### 2. **Wallet** (`wallet_*.py`)
- **KeyManager**: Cryptographic key derivation (Monero-style)
- **Wallet**: Multi-account wallet with BIP39 mnemonics
- Supports spend key, view key, and multiple accounts

#### 3. **Network** (`network_*.py`)
- **P2PManager**: Peer-to-peer networking
- **RPC Server**: JSON-RPC API for external clients
- Block and transaction broadcasting
- Blockchain synchronization

#### 4. **Entry Points**
- **daemon.py**: Blockchain node (mining + P2P)
- **cli_wallet.py**: User wallet interface
- **cli_admin.py**: Administrator functions

---

## 📋 Complete File List & Copy Instructions

### Step 1: Create Project Directory

```bash
mkdir anero_blockchain
cd anero_blockchain
```

### Step 2: Copy Configuration

Create `config.py` - [COPY FROM: config.py]

### Step 3: Copy Dependencies

Create `requirements.txt` - [COPY FROM: requirements.txt]

### Step 4: Copy Blockchain Core

Create these files in a `blockchain/` subdirectory (optional):

**Option A:** Files at root level
- `blockchain_utils.py` - [COPY FROM: blockchain_utils.py]
- `blockchain_transaction.py` - [COPY FROM: blockchain_transaction.py]
- `blockchain_block.py` - [COPY FROM: blockchain_block.py]
- `blockchain_chain.py` - [COPY FROM: blockchain_chain.py]
- `blockchain_token.py` - [COPY FROM: blockchain_token.py]
- `blockchain_smart_contract.py` - [COPY FROM: blockchain_smart_contract.py]

**Option B:** In `blockchain/` directory
Create `blockchain/__init__.py` with imports

### Step 5: Copy Wallet

- `wallet_key_manager.py` - [COPY FROM: wallet_key_manager.py]
- `wallet_wallet.py` - [COPY FROM: wallet_wallet.py]

### Step 6: Copy Network

- `network_p2p_manager.py` - [COPY FROM: network_p2p_manager.py]
- `network_rpc_server.py` - [COPY FROM: network_rpc_server.py]

### Step 7: Copy Entry Points

- `daemon.py` - [COPY FROM: daemon.py]
- `cli_wallet.py` - [COPY FROM: cli_wallet.py]
- `cli_admin.py` - [COPY FROM: cli_admin.py]

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Network
PRIMARY_NODE_IP = "3.151.52.76"
PRIMARY_NODE_PORT = 61324

# Blockchain
BLOCK_TIME = 45  # seconds
INITIAL_DIFFICULTY = 1000000000000  # Very high
TOTAL_SUPPLY = 1_000_000_000  # 1 billion
PREMINE = 50_000_000  # 50 million
```

---

## 🔑 Wallet Operations

### Create New Wallet

```bash
python cli_wallet.py create-wallet --name mywallet --password mypassword
```

**Output:**
- Wallet file saved to `~/.anero/wallets/mywallet.json`
- Mnemonic displayed (SAVE THIS!)
- Account details shown

### Restore Wallet from Mnemonic

```bash
python cli_wallet.py restore-wallet --name restored --mnemonic "word1 word2 ... word12"
```

### Show Wallet Information

```bash
python cli_wallet.py show-wallet-info --wallet mywallet
```

### Export Keys (DANGEROUS!)

```bash
python cli_wallet.py export-keys --wallet mywallet --account 0
```

### Send ANR

```bash
python cli_wallet.py send \
  --wallet mywallet \
  --account 0 \
  --to recipient_address \
  --amount 100
```

### Check Balance

```bash
python cli_wallet.py balance --wallet mywallet --account 0
```

---

## 🪙 Token (ANC-65) Operations

### Create Token

```bash
python cli_wallet.py create-token \
  --wallet mywallet \
  --name "MyToken" \
  --symbol "MYT" \
  --supply 1000000
```

### Send Token

```bash
python cli_wallet.py send-token \
  --wallet mywallet \
  --account 0 \
  --token-id token_id_here \
  --to recipient_address \
  --amount 100
```

### Check Token Balance (via RPC)

```bash
curl -X POST http://localhost:54374/api/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_token_balance",
    "params": ["token_id", "address"],
    "id": 1
  }'
```

---

## 🤖 Smart Contracts

### Create Contract File (`mycontract.py`)

```python
def hello():
    return "Hello, Anero!"

def add(a, b):
    return a + b

def get_state():
    return state
```

### Deploy Contract

```bash
python cli_admin.py deploy-contract --file mycontract.py
```

### Call Contract Function

```bash
python cli_admin.py call-contract \
  --contract contract_address \
  --function hello
```

---

## 📊 Admin Operations

### Get Blockchain Status

```bash
python cli_admin.py status
```

### Get Specific Block

```bash
python cli_admin.py get-block --height 0
```

### Get Account Balance

```bash
python cli_admin.py get-balance --address address_here
```

### List All Accounts

```bash
python cli_admin.py list-accounts
```

---

## 🌐 JSON-RPC API Reference

### Blockchain Status

```bash
curl http://localhost:54374/api/status
```

### Get Balance

```bash
curl http://localhost:54374/api/balance/address_here
```

### Send Transaction (RPC)

```bash
curl -X POST http://localhost:54374/api/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "send_transaction",
    "params": [{...transaction_data...}],
    "id": 1
  }'
```

---

## 🔗 Multi-Node Setup

### Start Primary Node

```bash
python daemon.py --node primary
```

### Start Secondary Node (in another terminal)

```bash
python daemon.py --node secondary
```

Both nodes will:
- Connect to each other automatically
- Sync blockchain state
- Broadcast blocks and transactions
- Participate in consensus

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Change port in config.py |
| Connection refused | Ensure both nodes are running |
| Import errors | Run `pip install -r requirements.txt` |
| Wallet not found | Use `cli_wallet.py list-wallets` first |
| Transaction failed | Check wallet balance with `balance` command |
| Contract deployment error | Verify Python syntax in contract file |

---

## 📈 Performance Tuning

```python
# In config.py

# Increase block time for slower systems
BLOCK_TIME = 60  # instead of 45

# Reduce difficulty for testing
INITIAL_DIFFICULTY = 1000000  # instead of 1000000000000

# Adjust mining parameters
MAX_TX_PER_BLOCK = 1000  # lower for less memory
```

---

## 🔐 Security Recommendations

1. **Backup Mnemonics**: Store wallet mnemonics securely
2. **Use Passwords**: Always use wallet passwords in production
3. **Firewall Rules**: Restrict RPC access to trusted IPs
4. **Private Keys**: Never share spend/view keys
5. **HTTPS**: Use HTTPS for remote RPC in production
6. **Rate Limiting**: Implement rate limiting on RPC endpoints

---

## 📝 Smart Contract Example

```python
# counter_contract.py

# Initialize state
state = {'count': 0}

def increment():
    state['count'] += 1
    return state['count']

def decrement():
    if state['count'] > 0:
        state['count'] -= 1
    return state['count']

def get_count():
    return state['count']
```

Deploy:
```bash
python cli_admin.py deploy-contract --file counter_contract.py
```

Call:
```bash
python cli_admin.py call-contract --contract <address> --function increment
```

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Copy all files
3. ✅ Start daemon
4. ✅ Create wallet
5. ✅ Create token (ANC-65)
6. ✅ Deploy smart contract
7. ✅ Send transactions
8. ✅ Monitor blockchain status

For updates and support, check the daemon logs in `~/.anero/logs/`.

---

**Anero Blockchain v1.0 - Complete Implementation**
