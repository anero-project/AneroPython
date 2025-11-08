# EXAMPLES.md - Usage Examples for Anero Blockchain

## 📚 Complete Usage Examples

### Example 1: Create Wallet and Send Transactions

```bash
# Step 1: Create a new wallet
python cli_wallet.py create-wallet --name alice

# Output:
# ✓ Wallet 'alice' created successfully
# 
# 📝 MNEMONIC (Keep this safe!):
#    abandon ability able about above absolute absorb abstract abstract abstract ...
# 
# 📮 Primary Address: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6
# 🔑 Spend Key: spend_key_123...
# 👁️  View Key: view_key_456...

# Step 2: Show wallet info
python cli_wallet.py show-wallet-info --wallet alice

# Step 3: Check balance (starts at 0, need to mine blocks)
python cli_wallet.py balance --wallet alice --account 0

# Step 4: Create another wallet to receive funds
python cli_wallet.py create-wallet --name bob

# Step 5: Send ANR from Alice to Bob
python cli_wallet.py send \
  --wallet alice \
  --account 0 \
  --to bob_address_here \
  --amount 100
```

---

### Example 2: Create and Transfer Tokens (ANC-65)

```bash
# Step 1: Create a token
python cli_wallet.py create-token \
  --wallet alice \
  --name "AliceCoin" \
  --symbol "ALC" \
  --supply 1000000

# Output shows token ID: alice_coin_token_id_123...

# Step 2: Send token to Bob
python cli_wallet.py send-token \
  --wallet alice \
  --account 0 \
  --token-id alice_coin_token_id_123 \
  --to bob_address \
  --amount 50000

# Step 3: Check token balance via RPC
curl -X POST http://localhost:54374/api/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_token_balance",
    "params": ["alice_coin_token_id_123", "bob_address"],
    "id": 1
  }'
```

---

### Example 3: Deploy Smart Contract (Counter)

**File: counter.py**
```python
# Counter smart contract

state = {'count': 0, 'owner': ''}

def initialize(owner_address):
    """Initialize counter with owner"""
    state['owner'] = owner_address
    state['count'] = 0
    return "Counter initialized"

def increment():
    """Increment counter"""
    state['count'] += 1
    return state['count']

def decrement():
    """Decrement counter (non-negative)"""
    if state['count'] > 0:
        state['count'] -= 1
    return state['count']

def get_count():
    """Get current count"""
    return state['count']

def reset():
    """Reset counter to 0"""
    state['count'] = 0
    return "Counter reset"

def add(value):
    """Add value to counter"""
    state['count'] += value
    return state['count']
```

**Deploy and use:**
```bash
# Step 1: Deploy contract
python cli_admin.py deploy-contract --file counter.py

# Output: Contract deployed at address: counter_contract_123...

# Step 2: Initialize contract
python cli_admin.py call-contract \
  --contract counter_contract_123 \
  --function initialize \
  --args "alice_address"

# Step 3: Call functions
python cli_admin.py call-contract \
  --contract counter_contract_123 \
  --function increment

python cli_admin.py call-contract \
  --contract counter_contract_123 \
  --function increment

python cli_admin.py call-contract \
  --contract counter_contract_123 \
  --function get_count

# Result: 2
```

---

### Example 4: Deploy Smart Contract (Data Storage)

**File: storage.py**
```python
# Key-value storage contract

state = {'data': {}, 'owner': ''}

def init_storage(owner):
    state['owner'] = owner
    state['data'] = {}
    return "Storage initialized"

def set_value(key, value):
    """Store a key-value pair"""
    state['data'][key] = value
    return f"Stored {key} = {value}"

def get_value(key):
    """Retrieve a value by key"""
    return state['data'].get(key, "Key not found")

def delete_value(key):
    """Delete a value"""
    if key in state['data']:
        del state['data'][key]
        return f"Deleted {key}"
    return "Key not found"

def list_keys():
    """Get all keys"""
    return list(state['data'].keys())

def get_all():
    """Get all data"""
    return state['data']
```

**Deploy and use:**
```bash
# Deploy
python cli_admin.py deploy-contract --file storage.py

# Initialize
python cli_admin.py call-contract \
  --contract storage_contract_123 \
  --function init_storage \
  --args "alice_address"

# Set values
python cli_admin.py call-contract \
  --contract storage_contract_123 \
  --function set_value \
  --args "username,alice"

python cli_admin.py call-contract \
  --contract storage_contract_123 \
  --function set_value \
  --args "email,alice@example.com"

# Get value
python cli_admin.py call-contract \
  --contract storage_contract_123 \
  --function get_value \
  --args "username"

# Result: alice
```

---

### Example 5: Multi-Node Setup

**Terminal 1 - Start Primary Node:**
```bash
python daemon.py --node primary
```

**Terminal 2 - Start Secondary Node:**
```bash
python daemon.py --node secondary
```

**Terminal 3 - Monitor:**
```bash
# Check primary status
python cli_admin.py status

# Both nodes will sync automatically and share blocks/transactions
```

---

### Example 6: Wallet Restoration from Mnemonic

```bash
# Step 1: Save your mnemonic from initial wallet creation
# Example: "abandon ability able about above absolute absorb abstract abstract abstract abstract abstract"

# Step 2: Restore wallet
python cli_wallet.py restore-wallet \
  --name alice_restored \
  --mnemonic "abandon ability able about above absolute absorb abstract abstract abstract abstract abstract"

# Step 3: Verify accounts were restored
python cli_wallet.py show-wallet-info --wallet alice_restored

# All accounts with same balances will be restored
```

---

### Example 7: Blockchain Status Monitoring

```bash
# Check blockchain status
python cli_admin.py status

# Output:
# ============================================================
#   BLOCKCHAIN STATUS
# ============================================================
# 
# Height: 42
# Total Blocks: 43
# Pending Transactions: 2
# Current Difficulty: 1000000000000

# Get specific block
python cli_admin.py get-block --height 0

# Output shows genesis block details
```

---

### Example 8: Batch Operations Script

**File: batch_operations.sh**
```bash
#!/bin/bash

echo "=== Anero Blockchain Batch Operations ==="

# Create wallets
echo "Creating wallets..."
python cli_wallet.py create-wallet --name wallet1
python cli_wallet.py create-wallet --name wallet2
python cli_wallet.py create-wallet --name wallet3

# Check status
echo "Checking blockchain status..."
python cli_admin.py status

# List wallets
echo "Listing all wallets..."
python cli_wallet.py list-wallets

# Create token
echo "Creating token..."
python cli_wallet.py create-token \
  --wallet wallet1 \
  --name "MyToken" \
  --symbol "MYT" \
  --supply 5000000

echo "=== Operations Complete ==="
```

**Run:**
```bash
chmod +x batch_operations.sh
./batch_operations.sh
```

---

### Example 9: Using RPC API Directly

```bash
# Get blockchain height
curl -X POST http://localhost:54374/api/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_blockchain_height",
    "params": [],
    "id": 1
  }'

# Get balance
curl -X POST http://localhost:54374/api/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_balance",
    "params": ["address_here"],
    "id": 1
  }'

# Get block
curl -X POST http://localhost:54374/api/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_block",
    "params": [5],
    "id": 1
  }'
```

---

### Example 10: Smart Contract - Voting System

**File: voting.py**
```python
# Simple voting contract

state = {
    'proposals': {},  # proposal_id -> {title, yes_votes, no_votes}
    'voters': {},      # voter_address -> [proposal_ids_voted]
    'owner': ''
}

def initialize_voting(owner_address):
    """Initialize voting system"""
    state['owner'] = owner_address
    return "Voting system initialized"

def create_proposal(proposal_id, title):
    """Create a new proposal"""
    if proposal_id in state['proposals']:
        return "Proposal already exists"
    
    state['proposals'][proposal_id] = {
        'title': title,
        'yes_votes': 0,
        'no_votes': 0
    }
    return f"Proposal '{title}' created"

def vote(voter_address, proposal_id, vote_yes):
    """Cast a vote on a proposal"""
    if proposal_id not in state['proposals']:
        return "Proposal not found"
    
    if voter_address not in state['voters']:
        state['voters'][voter_address] = []
    
    if proposal_id in state['voters'][voter_address]:
        return "Already voted on this proposal"
    
    if vote_yes:
        state['proposals'][proposal_id]['yes_votes'] += 1
    else:
        state['proposals'][proposal_id]['no_votes'] += 1
    
    state['voters'][voter_address].append(proposal_id)
    return "Vote recorded"

def get_proposal_results(proposal_id):
    """Get voting results"""
    if proposal_id not in state['proposals']:
        return "Proposal not found"
    
    prop = state['proposals'][proposal_id]
    return {
        'title': prop['title'],
        'yes_votes': prop['yes_votes'],
        'no_votes': prop['no_votes'],
        'passed': prop['yes_votes'] > prop['no_votes']
    }

def list_proposals():
    """List all proposals"""
    return list(state['proposals'].keys())
```

**Use it:**
```bash
# Deploy
python cli_admin.py deploy-contract --file voting.py

# Initialize
python cli_admin.py call-contract \
  --contract voting_address \
  --function initialize_voting \
  --args "alice_address"

# Create proposal
python cli_admin.py call-contract \
  --contract voting_address \
  --function create_proposal \
  --args "prop1,Increase block time to 60s"

# Vote
python cli_admin.py call-contract \
  --contract voting_address \
  --function vote \
  --args "alice_address,prop1,true"

# Get results
python cli_admin.py call-contract \
  --contract voting_address \
  --function get_proposal_results \
  --args "prop1"
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Create wallet | `python cli_wallet.py create-wallet --name name` |
| Restore wallet | `python cli_wallet.py restore-wallet --name name --mnemonic "..."` |
| Show wallet info | `python cli_wallet.py show-wallet-info --wallet name` |
| Check balance | `python cli_wallet.py balance --wallet name --account 0` |
| Send ANR | `python cli_wallet.py send --wallet name --account 0 --to address --amount 100` |
| Create token | `python cli_wallet.py create-token --wallet name --name "Token" --symbol "TKN" --supply 1000000` |
| Send token | `python cli_wallet.py send-token --wallet name --account 0 --token-id id --to address --amount 100` |
| Deploy contract | `python cli_admin.py deploy-contract --file contract.py` |
| Call contract | `python cli_admin.py call-contract --contract address --function name --args "arg1,arg2"` |
| Get status | `python cli_admin.py status` |
| Get block | `python cli_admin.py get-block --height 0` |

---

**Ready to start? See SETUP_GUIDE.md for installation instructions!**
