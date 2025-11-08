# blockchain/transaction.py - Transaction handling

import json
import time
from typing import Dict, List, Any
import hashlib
from blockchain_utils import Utils
import config

class Transaction:
    """Represents a blockchain transaction"""

    def __init__(self, tx_data: Dict = None):
        """Initialize transaction"""
        if tx_data:
            self.version = tx_data.get('version', 1)
            self.timestamp = tx_data.get('timestamp', int(time.time()))
            self.inputs = tx_data.get('inputs', [])
            self.outputs = tx_data.get('outputs', [])
            self.data = tx_data.get('data', '')
            self.signatures = tx_data.get('signatures', [])
            self.tx_hash = tx_data.get('tx_hash', '')
        else:
            self.version = 1
            self.timestamp = int(time.time())
            self.inputs = []
            self.outputs = []
            self.data = ''
            self.signatures = []
            self.tx_hash = ''

    def add_input(self, prev_tx_hash: str, output_index: int, amount: float, sender_address: str):
        """Add input to transaction"""
        self.inputs.append({
            'prev_tx_hash': prev_tx_hash,
            'output_index': output_index,
            'amount': amount,
            'sender_address': sender_address,
        })

    def add_output(self, recipient_address: str, amount: float, metadata: Dict = None):
        """Add output to transaction"""
        self.outputs.append({
            'recipient_address': recipient_address,
            'amount': amount,
            'metadata': metadata or {},
        })

    def calculate_hash(self) -> str:
        """Calculate transaction hash"""
        tx_dict = {
            'version': self.version,
            'timestamp': self.timestamp,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'data': self.data,
        }
        self.tx_hash = Utils.calculate_transaction_hash(tx_dict)
        return self.tx_hash

    def get_total_input(self) -> float:
        """Get total input amount"""
        return sum(inp['amount'] for inp in self.inputs)

    def get_total_output(self) -> float:
        """Get total output amount"""
        return sum(out['amount'] for out in self.outputs)

    def get_fee(self) -> float:
        """Calculate transaction fee"""
        return self.get_total_input() - self.get_total_output()

    def is_valid(self) -> bool:
        """Validate transaction"""
        # Check hash
        if not self.tx_hash:
            self.calculate_hash()
        
        # Check inputs and outputs exist
        if not self.inputs or not self.outputs:
            return False
        
        # Check amounts are positive
        for inp in self.inputs:
            if inp['amount'] <= 0:
                return False
        
        for out in self.outputs:
            if out['amount'] <= 0:
                return False
        
        # Check input >= output (accounting for fee)
        if self.get_total_input() < self.get_total_output():
            return False
        
        # Check addresses are valid
        for inp in self.inputs:
            if not Utils.validate_address(inp['sender_address']):
                return False
        
        for out in self.outputs:
            if not Utils.validate_address(out['recipient_address']):
                return False
        
        return True

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'timestamp': self.timestamp,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'data': self.data,
            'signatures': self.signatures,
            'tx_hash': self.tx_hash,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), default=str)

    @staticmethod
    def from_dict(tx_dict: Dict) -> 'Transaction':
        """Create transaction from dictionary"""
        return Transaction(tx_dict)

    @staticmethod
    def from_json(tx_json: str) -> 'Transaction':
        """Create transaction from JSON"""
        return Transaction(json.loads(tx_json))


class CoinbaseTransaction(Transaction):
    """Special transaction for mining rewards and premine"""

    def __init__(self, miner_address: str, amount: float, block_height: int):
        """Initialize coinbase transaction"""
        super().__init__()
        self.miner_address = miner_address
        self.block_height = block_height
        self.data = f"Coinbase reward for block {block_height}"
        
        # Coinbase has no inputs
        self.inputs = []
        
        # Add mining reward as output
        self.add_output(miner_address, amount)

    def is_valid(self) -> bool:
        """Validate coinbase transaction"""
        # Coinbase must have no inputs
        if self.inputs:
            return False
        
        # Must have exactly one output
        if len(self.outputs) != 1:
            return False
        
        # Output must be positive
        if self.outputs[0]['amount'] <= 0:
            return False
        
        return True


class TokenTransaction(Transaction):
    """Transaction for token operations"""

    def __init__(self, tx_type: str, token_id: str, from_address: str, to_address: str, amount: float):
        """Initialize token transaction"""
        super().__init__()
        self.tx_type = tx_type  # 'transfer', 'approve', 'mint', 'burn'
        self.token_id = token_id
        self.from_address = from_address
        self.to_address = to_address
        self.token_amount = amount
        
        self.data = f"Token {tx_type}: {token_id}"
        
        # Add metadata
        self.add_output(to_address, 0, {
            'token_id': token_id,
            'token_amount': amount,
            'token_type': tx_type,
        })

    def is_valid(self) -> bool:
        """Validate token transaction"""
        if not super().is_valid():
            return False
        
        if not Utils.validate_address(self.from_address):
            return False
        
        if not Utils.validate_address(self.to_address):
            return False
        
        if self.token_amount <= 0:
            return False
        
        if self.tx_type not in ['transfer', 'approve', 'mint', 'burn']:
            return False
        
        return True


class SmartContractTransaction(Transaction):
    """Transaction for smart contract operations"""

    def __init__(self, sender_address: str, contract_address: str, method: str, args: List, gas_limit: int):
        """Initialize smart contract transaction"""
        super().__init__()
        self.sender_address = sender_address
        self.contract_address = contract_address
        self.method = method
        self.args = args
        self.gas_limit = gas_limit
        self.gas_used = 0
        
        self.data = f"Contract call: {contract_address}.{method}({', '.join(map(str, args))})"
        
        self.add_output(contract_address, 0, {
            'contract_method': method,
            'contract_args': args,
            'gas_limit': gas_limit,
        })

    def is_valid(self) -> bool:
        """Validate smart contract transaction"""
        if not Utils.validate_address(self.sender_address):
            return False
        
        if not Utils.validate_address(self.contract_address):
            return False
        
        if self.gas_limit <= 0 or self.gas_limit > config.GAS_LIMIT_PER_BLOCK:
            return False
        
        if not isinstance(self.method, str) or not self.method:
            return False
        
        return True
