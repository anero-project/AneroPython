# blockchain/block.py - Block structure and operations

import json
import time
from typing import Dict, List
from blockchain_utils import Utils
import config

class Block:
    """Represents a blockchain block"""

    def __init__(self, block_data: Dict = None):
        """Initialize block"""
        if block_data:
            self.version = block_data.get('version', 1)
            self.height = block_data.get('height', 0)
            self.timestamp = block_data.get('timestamp', int(time.time()))
            self.previous_hash = block_data.get('previous_hash', '0' * 64)
            self.merkle_root = block_data.get('merkle_root', '')
            self.transactions = block_data.get('transactions', [])
            self.nonce = block_data.get('nonce', 0)
            self.difficulty = block_data.get('difficulty', config.INITIAL_DIFFICULTY)
            self.miner_address = block_data.get('miner_address', '')
            self.block_hash = block_data.get('block_hash', '')
        else:
            self.version = 1
            self.height = 0
            self.timestamp = int(time.time())
            self.previous_hash = '0' * 64
            self.merkle_root = ''
            self.transactions = []
            self.nonce = 0
            self.difficulty = config.INITIAL_DIFFICULTY
            self.miner_address = ''
            self.block_hash = ''

    def add_transaction(self, transaction):
        """Add transaction to block"""
        if isinstance(transaction, dict):
            self.transactions.append(transaction)
        else:
            self.transactions.append(transaction.to_dict())

    def calculate_merkle_root(self):
        """Calculate and set merkle root"""
        self.merkle_root = Utils.calculate_merkle_root(self.transactions)
        return self.merkle_root

    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = {
            'version': self.version,
            'height': self.height,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'miner_address': self.miner_address,
        }
        self.block_hash = Utils.calculate_block_hash(block_data)
        return self.block_hash

    def mine(self, miner_address: str):
        """Mine the block (Proof of Work)"""
        self.miner_address = miner_address
        self.calculate_merkle_root()
        
        print(f"Mining block {self.height}...")
        start_time = time.time()
        nonce = 0
        
        while True:
            self.nonce = nonce
            block_hash = self.calculate_hash()
            
            if Utils.check_hash_meets_difficulty(block_hash, self.difficulty):
                mining_time = time.time() - start_time
                print(f"✓ Block {self.height} mined in {mining_time:.2f}s")
                print(f"  Hash: {block_hash}")
                print(f"  Nonce: {nonce}")
                return block_hash
            
            nonce += 1
            
            if nonce % 100000 == 0:
                elapsed = time.time() - start_time
                print(f"  Attempt {nonce} ({elapsed:.2f}s elapsed)...")

    def is_valid(self) -> bool:
        """Validate block"""
        # Check hash
        calculated_hash = self.calculate_hash()
        if calculated_hash != self.block_hash:
            return False
        
        # Check difficulty
        if not Utils.check_hash_meets_difficulty(self.block_hash, self.difficulty):
            return False
        
        # Check merkle root
        if self.calculate_merkle_root() != self.merkle_root:
            return False
        
        # Check timestamp
        if self.timestamp > int(time.time()) + 600:  # 10 minute future allowance
            return False
        
        # Check block size
        block_size = len(json.dumps(self.to_dict()))
        if block_size > config.MAX_BLOCK_SIZE:
            return False
        
        # Check transaction count
        if len(self.transactions) > config.MAX_TX_PER_BLOCK:
            return False
        
        return True

    def get_size(self) -> int:
        """Get block size in bytes"""
        return len(json.dumps(self.to_dict()))

    def get_transaction_count(self) -> int:
        """Get transaction count"""
        return len(self.transactions)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'height': self.height,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'transactions': self.transactions,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'miner_address': self.miner_address,
            'block_hash': self.block_hash,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), default=str)

    @staticmethod
    def from_dict(block_dict: Dict) -> 'Block':
        """Create block from dictionary"""
        return Block(block_dict)

    @staticmethod
    def from_json(block_json: str) -> 'Block':
        """Create block from JSON"""
        return Block(json.loads(block_json))

    @staticmethod
    def create_genesis_block(miner_address: str) -> 'Block':
        """Create genesis block with premine"""
        genesis = Block()
        genesis.version = 1
        genesis.height = 0
        genesis.timestamp = int(time.time())
        genesis.previous_hash = '0' * 64
        genesis.miner_address = miner_address
        genesis.difficulty = config.INITIAL_DIFFICULTY
        
        # Create premine transaction
        from blockchain_transaction import CoinbaseTransaction
        premine_tx = CoinbaseTransaction(miner_address, config.PREMINE, 0)
        premine_tx.calculate_hash()
        genesis.add_transaction(premine_tx)
        
        genesis.calculate_merkle_root()
        genesis.mine(miner_address)
        
        return genesis
