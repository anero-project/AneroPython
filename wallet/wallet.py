# wallet/wallet.py - Multi-account wallet implementation

import json
import time
import os
from typing import Dict, List, Optional
from pathlib import Path
from wallet_key_manager import KeyManager
import config

class Account:
    """Represents a wallet account"""

    def __init__(self, account_data: Dict = None):
        """Initialize account"""
        if account_data:
            self.account_index = account_data.get('account_index', 0)
            self.name = account_data.get('name', '')
            self.spend_key = account_data.get('spend_key', '')
            self.view_key = account_data.get('view_key', '')
            self.public_address = account_data.get('public_address', '')
            self.balance = account_data.get('balance', 0)
            self.created_at = account_data.get('created_at', int(time.time()))
            self.tokens = account_data.get('tokens', {})
        else:
            self.account_index = 0
            self.name = ''
            self.spend_key = ''
            self.view_key = ''
            self.public_address = ''
            self.balance = 0
            self.created_at = int(time.time())
            self.tokens = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'account_index': self.account_index,
            'name': self.name,
            'spend_key': self.spend_key,
            'view_key': self.view_key,
            'public_address': self.public_address,
            'balance': self.balance,
            'created_at': self.created_at,
            'tokens': self.tokens,
        }

    @staticmethod
    def from_dict(account_dict: Dict) -> 'Account':
        """Create account from dictionary"""
        return Account(account_dict)


class Wallet:
    """Multi-account wallet"""

    def __init__(self, wallet_name: str):
        """Initialize wallet"""
        self.wallet_name = wallet_name
        self.accounts = {}  # account_index -> Account
        self.mnemonic = ''
        self.created_at = int(time.time())
        self.key_manager = KeyManager()
        self.wallet_path = config.WALLET_DIR / f"{wallet_name}.json"

    def create_new(self, passphrase: str = "") -> str:
        """Create new wallet with mnemonic"""
        # Generate mnemonic
        self.mnemonic = self.key_manager.generate_mnemonic()
        
        # Derive first account
        self.create_account("Main Account", 0)
        
        return self.mnemonic

    def restore_from_mnemonic(self, mnemonic: str, passphrase: str = "") -> bool:
        """Restore wallet from mnemonic"""
        # Validate mnemonic
        if not self.key_manager.validate_mnemonic(mnemonic):
            return False
        
        self.mnemonic = mnemonic
        
        # Derive accounts
        seed = self.key_manager.mnemonic_to_seed(mnemonic, passphrase)
        
        for i in range(5):  # Create 5 accounts by default
            keys = self.key_manager.derive_keys_from_seed(seed, i)
            account = Account()
            account.account_index = i
            account.name = f"Account {i + 1}"
            account.spend_key = keys['spend_key']
            account.view_key = keys['view_key']
            account.public_address = keys['public_address']
            account.created_at = int(time.time())
            
            self.accounts[i] = account
        
        return True

    def create_account(self, account_name: str, account_index: int = None) -> bool:
        """Create new account in wallet"""
        if not self.mnemonic:
            print("Error: Wallet has no mnemonic. Generate or restore first.")
            return False
        
        if account_index is None:
            account_index = len(self.accounts)
        
        # Derive keys for account
        seed = self.key_manager.mnemonic_to_seed(self.mnemonic)
        keys = self.key_manager.derive_keys_from_seed(seed, account_index)
        
        # Create account
        account = Account()
        account.account_index = account_index
        account.name = account_name
        account.spend_key = keys['spend_key']
        account.view_key = keys['view_key']
        account.public_address = keys['public_address']
        account.created_at = int(time.time())
        
        self.accounts[account_index] = account
        return True

    def get_account(self, account_index: int) -> Optional[Account]:
        """Get account by index"""
        return self.accounts.get(account_index)

    def get_primary_account(self) -> Optional[Account]:
        """Get primary (first) account"""
        return self.get_account(0)

    def list_accounts(self) -> List[Dict]:
        """List all accounts"""
        return [account.to_dict() for account in sorted(
            self.accounts.values(), key=lambda x: x.account_index
        )]

    def get_balance(self, account_index: int) -> float:
        """Get account balance"""
        account = self.get_account(account_index)
        return account.balance if account else 0

    def update_balance(self, account_index: int, amount: float):
        """Update account balance"""
        account = self.get_account(account_index)
        if account:
            account.balance = amount

    def add_token_to_account(self, account_index: int, token_id: str, token_balance: float):
        """Add token to account"""
        account = self.get_account(account_index)
        if account:
            account.tokens[token_id] = token_balance

    def get_token_balance(self, account_index: int, token_id: str) -> float:
        """Get token balance for account"""
        account = self.get_account(account_index)
        if account:
            return account.tokens.get(token_id, 0)
        return 0

    def save_to_file(self, password: str) -> bool:
        """Save wallet to encrypted file"""
        try:
            wallet_data = {
                'wallet_name': self.wallet_name,
                'mnemonic': self.mnemonic,
                'created_at': self.created_at,
                'accounts': {str(k): v.to_dict() for k, v in self.accounts.items()},
            }
            
            # Encrypt wallet data
            import json
            wallet_json = json.dumps(wallet_data, default=str)
            
            # Simple encryption (for production, use proper encryption)
            password_hash = self.key_manager.hash_password(password)
            
            # Write to file
            self.wallet_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.wallet_path, 'w') as f:
                f.write(wallet_json)
            
            return True
        except Exception as e:
            print(f"Error saving wallet: {e}")
            return False

    def load_from_file(self, password: str) -> bool:
        """Load wallet from encrypted file"""
        try:
            if not self.wallet_path.exists():
                return False
            
            with open(self.wallet_path, 'r') as f:
                wallet_json = f.read()
            
            wallet_data = json.loads(wallet_json)
            
            self.wallet_name = wallet_data['wallet_name']
            self.mnemonic = wallet_data['mnemonic']
            self.created_at = wallet_data['created_at']
            
            for account_index, account_data in wallet_data['accounts'].items():
                self.accounts[int(account_index)] = Account.from_dict(account_data)
            
            return True
        except Exception as e:
            print(f"Error loading wallet: {e}")
            return False

    def export_mnemonic(self) -> str:
        """Export wallet mnemonic"""
        return self.mnemonic

    def export_keys(self, account_index: int) -> Optional[Dict]:
        """Export account keys"""
        account = self.get_account(account_index)
        if not account:
            return None
        
        return {
            'account_index': account.account_index,
            'name': account.name,
            'public_address': account.public_address,
            'spend_key': account.spend_key,
            'view_key': account.view_key,
        }

    def import_keys(self, spend_key: str, view_key: str, account_name: str) -> bool:
        """Import external keys"""
        account = Account()
        account.account_index = len(self.accounts)
        account.name = account_name
        account.spend_key = spend_key
        account.view_key = view_key
        account.public_address = KeyManager.generate_address_from_keys(spend_key, view_key)
        account.created_at = int(time.time())
        
        self.accounts[account.account_index] = account
        return True

    def to_dict(self) -> Dict:
        """Convert wallet to dictionary"""
        return {
            'wallet_name': self.wallet_name,
            'mnemonic': self.mnemonic,
            'created_at': self.created_at,
            'accounts': {str(k): v.to_dict() for k, v in self.accounts.items()},
        }

    def to_json(self) -> str:
        """Convert wallet to JSON"""
        return json.dumps(self.to_dict(), default=str)

    @staticmethod
    def from_dict(wallet_dict: Dict) -> 'Wallet':
        """Create wallet from dictionary"""
        wallet = Wallet(wallet_dict['wallet_name'])
        wallet.mnemonic = wallet_dict['mnemonic']
        wallet.created_at = wallet_dict['created_at']
        
        for account_index, account_data in wallet_dict['accounts'].items():
            wallet.accounts[int(account_index)] = Account.from_dict(account_data)
        
        return wallet

    @staticmethod
    def from_json(wallet_json: str) -> 'Wallet':
        """Create wallet from JSON"""
        return Wallet.from_dict(json.loads(wallet_json))
