# blockchain/utils.py - Utility functions for blockchain

import hashlib
import json
import time
from typing import Any, Dict, List
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import config

class Utils:
    """Utility functions for blockchain operations"""

    @staticmethod
    def hash_data(data: Any) -> str:
        """Hash data using SHA3-256"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        elif not isinstance(data, bytes):
            data = str(data).encode()
        
        return hashlib.sha3_256(data).hexdigest()

    @staticmethod
    def calculate_block_hash(block_data: Dict) -> str:
        """Calculate block hash"""
        block_string = json.dumps({
            'version': block_data['version'],
            'timestamp': block_data['timestamp'],
            'previous_hash': block_data['previous_hash'],
            'merkle_root': block_data['merkle_root'],
            'nonce': block_data['nonce'],
            'difficulty': block_data['difficulty'],
            'miner_address': block_data['miner_address'],
        }, sort_keys=True)
        
        return hashlib.sha3_256(block_string.encode()).hexdigest()

    @staticmethod
    def calculate_merkle_root(transactions: List[Dict]) -> str:
        """Calculate merkle root from transactions"""
        if not transactions:
            return Utils.hash_data("genesis")
        
        tx_hashes = [Utils.hash_data(tx) for tx in transactions]
        
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hashes.append(Utils.hash_data(combined))
            
            tx_hashes = new_hashes
        
        return tx_hashes[0] if tx_hashes else Utils.hash_data("empty")

    @staticmethod
    def calculate_transaction_hash(tx_data: Dict) -> str:
        """Calculate transaction hash"""
        tx_string = json.dumps({
            'version': tx_data.get('version', 1),
            'inputs': tx_data.get('inputs', []),
            'outputs': tx_data.get('outputs', []),
            'timestamp': tx_data.get('timestamp', int(time.time())),
            'data': tx_data.get('data', ''),
        }, sort_keys=True)
        
        return hashlib.sha3_256(tx_string.encode()).hexdigest()

    @staticmethod
    def get_current_timestamp() -> int:
        """Get current timestamp"""
        return int(time.time())

    @staticmethod
    def serialize_data(data: Any) -> str:
        """Serialize data to JSON"""
        return json.dumps(data, sort_keys=True, default=str)

    @staticmethod
    def deserialize_data(data: str) -> Any:
        """Deserialize JSON data"""
        return json.loads(data)

    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate ANR address format"""
        if not isinstance(address, str):
            return False
        
        # Address should be 64 characters (32 bytes in hex)
        if len(address) != 64:
            return False
        
        try:
            int(address, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_hash(hash_value: str) -> bool:
        """Validate hash format"""
        if not isinstance(hash_value, str):
            return False
        
        if len(hash_value) != 64:
            return False
        
        try:
            int(hash_value, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def format_amount(amount: float) -> str:
        """Format amount with proper decimal places"""
        return f"{amount:.8f}"

    @staticmethod
    def parse_amount(amount: str) -> float:
        """Parse amount string to float"""
        try:
            return float(amount)
        except ValueError:
            raise ValueError(f"Invalid amount: {amount}")

    @staticmethod
    def get_difficulty_target(difficulty: int) -> str:
        """Get difficulty target from difficulty value"""
        # Convert difficulty to target (max hash / difficulty)
        max_hash = 2 ** 256 - 1
        target = max_hash // difficulty
        return hex(target)[2:].zfill(64)

    @staticmethod
    def check_hash_meets_difficulty(hash_value: str, difficulty: int) -> bool:
        """Check if hash meets difficulty requirement"""
        target = Utils.get_difficulty_target(difficulty)
        return hash_value <= target

    @staticmethod
    def calculate_block_reward(block_height: int) -> float:
        """Calculate block reward with halving"""
        halvings = block_height // config.BLOCK_REWARD_HALVING_INTERVAL
        reward = config.INITIAL_BLOCK_REWARD / (2 ** halvings)
        return max(reward, 0)

    @staticmethod
    def generate_random_bytes(length: int = 32) -> bytes:
        """Generate random bytes"""
        import os
        return os.urandom(length)

    @staticmethod
    def hex_to_bytes(hex_string: str) -> bytes:
        """Convert hex string to bytes"""
        return bytes.fromhex(hex_string)

    @staticmethod
    def bytes_to_hex(data: bytes) -> str:
        """Convert bytes to hex string"""
        return data.hex()
