# blockchain/token.py - ANC-65 Token Standard Implementation

import json
import time
from typing import Dict, List, Optional
from blockchain_utils import Utils

class Token:
    """Represents an ANC-65 token"""

    def __init__(self, token_data: Dict = None):
        """Initialize token"""
        if token_data:
            self.token_id = token_data.get('token_id', '')
            self.name = token_data.get('name', '')
            self.symbol = token_data.get('symbol', '')
            self.decimals = token_data.get('decimals', 8)
            self.total_supply = token_data.get('total_supply', 0)
            self.creator_address = token_data.get('creator_address', '')
            self.created_at = token_data.get('created_at', int(time.time()))
            self.balances = token_data.get('balances', {})
            self.allowances = token_data.get('allowances', {})
            self.metadata = token_data.get('metadata', {})
        else:
            self.token_id = ''
            self.name = ''
            self.symbol = ''
            self.decimals = 8
            self.total_supply = 0
            self.creator_address = ''
            self.created_at = int(time.time())
            self.balances = {}
            self.allowances = {}
            self.metadata = {}

    def generate_token_id(self) -> str:
        """Generate unique token ID"""
        data = f"{self.creator_address}{self.name}{self.symbol}{self.created_at}"
        self.token_id = Utils.hash_data(data)
        return self.token_id

    def mint(self, to_address: str, amount: float) -> bool:
        """Mint tokens to address"""
        if amount <= 0:
            return False
        
        if not Utils.validate_address(to_address):
            return False
        
        # Check total supply limit
        if self.total_supply + amount > 2**63 - 1:
            return False
        
        # Add balance
        if to_address not in self.balances:
            self.balances[to_address] = 0
        
        self.balances[to_address] += amount
        self.total_supply += amount
        
        return True

    def burn(self, from_address: str, amount: float) -> bool:
        """Burn tokens from address"""
        if amount <= 0:
            return False
        
        if from_address not in self.balances:
            return False
        
        if self.balances[from_address] < amount:
            return False
        
        self.balances[from_address] -= amount
        self.total_supply -= amount
        
        if self.balances[from_address] == 0:
            del self.balances[from_address]
        
        return True

    def transfer(self, from_address: str, to_address: str, amount: float) -> bool:
        """Transfer tokens between addresses"""
        if amount <= 0:
            return False
        
        if not Utils.validate_address(from_address) or not Utils.validate_address(to_address):
            return False
        
        if from_address not in self.balances or self.balances[from_address] < amount:
            return False
        
        self.balances[from_address] -= amount
        
        if to_address not in self.balances:
            self.balances[to_address] = 0
        
        self.balances[to_address] += amount
        
        return True

    def approve(self, owner_address: str, spender_address: str, amount: float) -> bool:
        """Approve spender to spend tokens on behalf of owner"""
        if amount < 0:
            return False
        
        if not Utils.validate_address(owner_address) or not Utils.validate_address(spender_address):
            return False
        
        key = f"{owner_address}:{spender_address}"
        self.allowances[key] = amount
        
        return True

    def transfer_from(self, spender_address: str, from_address: str, to_address: str, amount: float) -> bool:
        """Transfer tokens on behalf of another address"""
        if amount <= 0:
            return False
        
        key = f"{from_address}:{spender_address}"
        
        if key not in self.allowances or self.allowances[key] < amount:
            return False
        
        if not self.transfer(from_address, to_address, amount):
            return False
        
        self.allowances[key] -= amount
        
        return True

    def get_balance(self, address: str) -> float:
        """Get token balance of address"""
        return self.balances.get(address, 0)

    def get_allowance(self, owner_address: str, spender_address: str) -> float:
        """Get allowance for spender"""
        key = f"{owner_address}:{spender_address}"
        return self.allowances.get(key, 0)

    def is_valid(self) -> bool:
        """Validate token"""
        if not self.token_id:
            return False
        
        if not self.name or not self.symbol:
            return False
        
        if self.decimals < 0 or self.decimals > 18:
            return False
        
        if self.total_supply < 0:
            return False
        
        if not Utils.validate_address(self.creator_address):
            return False
        
        # Verify total supply matches sum of balances
        balance_sum = sum(self.balances.values())
        if balance_sum != self.total_supply:
            return False
        
        return True

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'token_id': self.token_id,
            'name': self.name,
            'symbol': self.symbol,
            'decimals': self.decimals,
            'total_supply': self.total_supply,
            'creator_address': self.creator_address,
            'created_at': self.created_at,
            'balances': self.balances,
            'allowances': self.allowances,
            'metadata': self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), default=str)

    @staticmethod
    def from_dict(token_dict: Dict) -> 'Token':
        """Create token from dictionary"""
        return Token(token_dict)

    @staticmethod
    def from_json(token_json: str) -> 'Token':
        """Create token from JSON"""
        return Token(json.loads(token_json))


class TokenManager:
    """Manages all tokens in the blockchain"""

    def __init__(self):
        """Initialize token manager"""
        self.tokens = {}  # token_id -> Token

    def create_token(self, name: str, symbol: str, total_supply: float, 
                    creator_address: str, decimals: int = 8) -> Optional[str]:
        """Create new token"""
        if not name or not symbol:
            return None
        
        if total_supply <= 0:
            return None
        
        if not Utils.validate_address(creator_address):
            return None
        
        token = Token()
        token.name = name
        token.symbol = symbol
        token.decimals = decimals
        token.creator_address = creator_address
        token.created_at = int(time.time())
        
        # Generate token ID
        token_id = token.generate_token_id()
        
        # Mint initial supply to creator
        token.mint(creator_address, total_supply)
        
        # Store token
        self.tokens[token_id] = token
        
        return token_id

    def get_token(self, token_id: str) -> Optional[Token]:
        """Get token by ID"""
        return self.tokens.get(token_id)

    def token_exists(self, token_id: str) -> bool:
        """Check if token exists"""
        return token_id in self.tokens

    def transfer_token(self, token_id: str, from_address: str, to_address: str, amount: float) -> bool:
        """Transfer tokens"""
        token = self.get_token(token_id)
        if not token:
            return False
        
        return token.transfer(from_address, to_address, amount)

    def get_token_balance(self, token_id: str, address: str) -> float:
        """Get token balance"""
        token = self.get_token(token_id)
        if not token:
            return 0
        
        return token.get_balance(address)

    def approve_token(self, token_id: str, owner_address: str, spender_address: str, amount: float) -> bool:
        """Approve token transfer"""
        token = self.get_token(token_id)
        if not token:
            return False
        
        return token.approve(owner_address, spender_address, amount)

    def list_tokens(self) -> List[str]:
        """Get list of all token IDs"""
        return list(self.tokens.keys())

    def get_token_info(self, token_id: str) -> Optional[Dict]:
        """Get token information"""
        token = self.get_token(token_id)
        if not token:
            return None
        
        return {
            'token_id': token.token_id,
            'name': token.name,
            'symbol': token.symbol,
            'decimals': token.decimals,
            'total_supply': token.total_supply,
            'creator_address': token.creator_address,
            'created_at': token.created_at,
        }
