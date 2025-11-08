# wallet/key_manager.py - Cryptographic key management

import hashlib
import json
from typing import Tuple, Dict
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from mnemonic import Mnemonic
import config

class KeyManager:
    """Manages cryptographic keys for wallets"""

    def __init__(self):
        """Initialize key manager"""
        self.mnemonic_handler = Mnemonic(config.MNEMONIC_LANGUAGE)

    def generate_mnemonic(self) -> str:
        """Generate 12-word BIP39 mnemonic"""
        mnemonic = self.mnemonic_handler.generate(strength=config.MNEMONIC_STRENGTH)
        return mnemonic

    def mnemonic_to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """Convert mnemonic to seed"""
        try:
            seed = self.mnemonic_handler.to_seed(mnemonic, passphrase)
            return seed
        except Exception as e:
            raise ValueError(f"Invalid mnemonic: {e}")

    def derive_keys_from_seed(self, seed: bytes, account_index: int = 0) -> Dict[str, str]:
        """Derive spend key, view key and address from seed"""
        # Use SHA3-256 for key derivation (Monero-style)
        
        # Derive spend key
        spend_key_data = seed + bytes(f"spend_key_{account_index}", 'utf-8')
        spend_key_hash = hashlib.sha3_256(spend_key_data).digest()
        spend_key = spend_key_hash[:32].hex()
        
        # Derive view key
        view_key_data = seed + bytes(f"view_key_{account_index}", 'utf-8')
        view_key_hash = hashlib.sha3_256(view_key_data).digest()
        view_key = view_key_hash[:32].hex()
        
        # Generate address from spend key and view key
        address_data = bytes.fromhex(spend_key) + bytes.fromhex(view_key)
        address = hashlib.sha3_256(address_data).hexdigest()
        
        return {
            'spend_key': spend_key,
            'view_key': view_key,
            'public_address': address,
        }

    def generate_keypair(self) -> Tuple[str, str]:
        """Generate Ed25519 keypair"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return private_bytes.hex(), public_bytes.hex()

    def sign_message(self, message: str, private_key_hex: str) -> str:
        """Sign message with private key"""
        try:
            private_key_bytes = bytes.fromhex(private_key_hex)
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
            
            message_bytes = message.encode() if isinstance(message, str) else message
            signature = private_key.sign(message_bytes)
            
            return signature.hex()
        except Exception as e:
            raise ValueError(f"Error signing message: {e}")

    def verify_signature(self, message: str, signature_hex: str, public_key_hex: str) -> bool:
        """Verify message signature with public key"""
        try:
            public_key_bytes = bytes.fromhex(public_key_hex)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            message_bytes = message.encode() if isinstance(message, str) else message
            signature_bytes = bytes.fromhex(signature_hex)
            
            public_key.verify(signature_bytes, message_bytes)
            return True
        except Exception:
            return False

    def validate_mnemonic(self, mnemonic: str) -> bool:
        """Validate mnemonic phrase"""
        try:
            return self.mnemonic_handler.check(mnemonic)
        except Exception:
            return False

    def derive_multiple_accounts(self, mnemonic: str, num_accounts: int = 5, 
                                passphrase: str = "") -> list:
        """Derive multiple accounts from single mnemonic"""
        seed = self.mnemonic_to_seed(mnemonic, passphrase)
        accounts = []
        
        for i in range(num_accounts):
            account = self.derive_keys_from_seed(seed, i)
            accounts.append(account)
        
        return accounts

    def hash_password(self, password: str) -> str:
        """Hash password for wallet encryption"""
        return hashlib.sha3_256(password.encode()).hexdigest()

    @staticmethod
    def generate_view_key_from_spend_key(spend_key: str) -> str:
        """Generate view key from spend key (simplified)"""
        data = bytes.fromhex(spend_key) + b"view_key_derivation"
        return hashlib.sha3_256(data).hexdigest()

    @staticmethod
    def generate_address_from_keys(spend_key: str, view_key: str) -> str:
        """Generate address from spend and view keys"""
        address_data = bytes.fromhex(spend_key) + bytes.fromhex(view_key)
        return hashlib.sha3_256(address_data).hexdigest()
