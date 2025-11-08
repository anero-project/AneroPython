# config.py - Configuration file for Anero Blockchain

import os
from pathlib import Path

# ============================================================================
# NETWORK CONFIGURATION
# ============================================================================

# Primary Node (Self)
PRIMARY_NODE_IP = "3.151.52.76"
PRIMARY_NODE_PORT = 61324
PRIMARY_NODE_RPC_PORT = 54374

# Secondary Node
SECONDARY_NODE_IP = "3.140.21.248"
SECONDARY_NODE_PORT = 61325
SECONDARY_NODE_RPC_PORT = 54375

# Seed Nodes List
SEED_NODES = [
    {"ip": PRIMARY_NODE_IP, "p2p_port": PRIMARY_NODE_PORT, "rpc_port": PRIMARY_NODE_RPC_PORT},
    {"ip": SECONDARY_NODE_IP, "p2p_port": SECONDARY_NODE_PORT, "rpc_port": SECONDARY_NODE_RPC_PORT},
]

# ============================================================================
# BLOCKCHAIN PARAMETERS
# ============================================================================

BLOCK_TIME = 45  # seconds
INITIAL_DIFFICULTY = 1000000000000  # Very high difficulty
DIFFICULTY_ADJUSTMENT_INTERVAL = 100  # blocks
TOTAL_SUPPLY = 1_000_000_000  # 1 billion ANR
PREMINE = 50_000_000  # 50 million ANR (premine amount)

# Mining parameters
MAX_BLOCK_SIZE = 10_000_000  # 10 MB
MAX_TX_PER_BLOCK = 5000
BLOCK_REWARD_HALVING_INTERVAL = 1_000_000  # blocks
INITIAL_BLOCK_REWARD = 0.5  # ANR per block

# ============================================================================
# WALLET CONFIGURATION
# ============================================================================

WALLET_DIR = Path.home() / ".anero" / "wallets"
WALLET_KEYS_DIR = Path.home() / ".anero" / "keys"
BLOCKCHAIN_DATA_DIR = Path.home() / ".anero" / "blockchain"

# Create directories if they don't exist
WALLET_DIR.mkdir(parents=True, exist_ok=True)
WALLET_KEYS_DIR.mkdir(parents=True, exist_ok=True)
BLOCKCHAIN_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Wallet parameters
MNEMONIC_LANGUAGE = "english"
MNEMONIC_STRENGTH = 128  # 12-word phrase
KEY_DERIVATION_PATH = "m/44'/128'/0'/0"  # BIP44-style path for Monero

# ============================================================================
# CRYPTOGRAPHY CONFIGURATION
# ============================================================================

# EdDSA curve (Monero-style)
CURVE = "ed25519"

# Hash algorithm
HASH_ALGORITHM = "sha3_256"

# ============================================================================
# TRANSACTION CONFIGURATION
# ============================================================================

TX_VERSION = 1
MIXIN_LEVELS = [2, 4, 8, 16]  # Ring size options for privacy
DEFAULT_MIXIN = 8

# ============================================================================
# SMART CONTRACT CONFIGURATION
# ============================================================================

SMART_CONTRACT_VERSION = 1
MAX_CONTRACT_SIZE = 1_000_000  # 1 MB
MAX_CONTRACT_EXECUTION_TIME = 30  # seconds
GAS_LIMIT_PER_BLOCK = 100_000_000
GAS_PRICE_MIN = 0.0001  # Minimum gas price in ANR

# ============================================================================
# TOKEN (ANC-65) CONFIGURATION
# ============================================================================

ANC65_VERSION = 1
MAX_TOKENS_PER_ADDRESS = 1000
TOKEN_PRECISION = 8  # decimal places

# ============================================================================
# P2P NETWORK CONFIGURATION
# ============================================================================

P2P_TIMEOUT = 30  # seconds
P2P_MAX_CONNECTIONS = 100
P2P_MESSAGE_QUEUE_SIZE = 1000
P2P_SYNC_BATCH_SIZE = 50  # blocks per sync request

# ============================================================================
# RPC CONFIGURATION
# ============================================================================

RPC_TIMEOUT = 30
RPC_MAX_CONNECTIONS = 50
RPC_THREAD_POOL_SIZE = 10

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_DIR = Path.home() / ".anero" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_RETENTION = 30  # days

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DB_DIR = BLOCKCHAIN_DATA_DIR / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_TYPE = "sqlite"  # sqlite or leveldb
DB_NAME = "anero_blockchain.db"
DB_PATH = DB_DIR / DB_NAME

# ============================================================================
# PERFORMANCE CONFIGURATION
# ============================================================================

CACHE_SIZE = 1000  # number of blocks to keep in memory
SYNC_BATCH_SIZE = 100  # blocks
VERIFICATION_THREADS = 4
