# cli_wallet.py - CLI Wallet Interface

import argparse
import json
import os
from pathlib import Path
from wallet_wallet import Wallet
from wallet_key_manager import KeyManager
from blockchain_transaction import Transaction
import config
import requests

class WalletCLI:
    """Command-line wallet interface"""

    def __init__(self, rpc_endpoint: str = "http://localhost:54374"):
        """Initialize wallet CLI"""
        self.rpc_endpoint = rpc_endpoint
        self.wallets = {}
        self.current_wallet = None

    def create_wallet(self, wallet_name: str, password: str = "") -> str:
        """Create new wallet"""
        wallet = Wallet(wallet_name)
        mnemonic = wallet.create_new()
        wallet.save_to_file(password)
        
        print(f"✓ Wallet '{wallet_name}' created successfully")
        print(f"\n📝 MNEMONIC (Keep this safe!):")
        print(f"   {mnemonic}\n")
        
        account = wallet.get_primary_account()
        print(f"📮 Primary Address: {account.public_address}")
        print(f"🔑 Spend Key: {account.spend_key}")
        print(f"👁️  View Key: {account.view_key}\n")
        
        return mnemonic

    def restore_wallet(self, wallet_name: str, mnemonic: str, password: str = "") -> bool:
        """Restore wallet from mnemonic"""
        wallet = Wallet(wallet_name)
        
        if not wallet.restore_from_mnemonic(mnemonic):
            print("✗ Failed to restore wallet - invalid mnemonic")
            return False
        
        wallet.save_to_file(password)
        print(f"✓ Wallet '{wallet_name}' restored successfully")
        
        for account in wallet.list_accounts():
            print(f"  Account {account['account_index']}: {account['public_address']}")
        
        return True

    def load_wallet(self, wallet_name: str, password: str = "") -> bool:
        """Load wallet from file"""
        wallet = Wallet(wallet_name)
        
        if not wallet.load_from_file(password):
            print(f"✗ Failed to load wallet '{wallet_name}'")
            return False
        
        self.current_wallet = wallet
        self.wallets[wallet_name] = wallet
        print(f"✓ Wallet '{wallet_name}' loaded")
        
        return True

    def show_wallet_info(self, wallet_name: str):
        """Show wallet information"""
        if not self.load_wallet(wallet_name):
            return
        
        wallet = self.current_wallet
        
        print(f"\n{'='*60}")
        print(f"  WALLET: {wallet.wallet_name}")
        print(f"{'='*60}\n")
        
        print(f"Total Accounts: {len(wallet.accounts)}\n")
        
        for account in wallet.list_accounts():
            print(f"Account {account['account_index']}: {account['name']}")
            print(f"  Public Address: {account['public_address']}")
            print(f"  Balance: {account['balance']} ANR")
            
            if account['tokens']:
                print(f"  Tokens:")
                for token_id, token_balance in account['tokens'].items():
                    print(f"    {token_id}: {token_balance}")
            print()

    def list_wallets(self):
        """List all wallets"""
        wallets = list(config.WALLET_DIR.glob("*.json"))
        
        if not wallets:
            print("No wallets found")
            return
        
        print(f"\n{'='*60}")
        print(f"  WALLETS")
        print(f"{'='*60}\n")
        
        for wallet_file in wallets:
            wallet_name = wallet_file.stem
            print(f"  • {wallet_name}")

    def send_transaction(self, wallet_name: str, account_index: int, to_address: str, 
                        amount: float, password: str = ""):
        """Send ANR transaction"""
        if not self.load_wallet(wallet_name, password):
            return
        
        wallet = self.current_wallet
        account = wallet.get_account(account_index)
        
        if not account:
            print(f"✗ Account {account_index} not found")
            return
        
        if account.balance < amount:
            print(f"✗ Insufficient balance. Have {account.balance}, need {amount}")
            return
        
        # Create transaction
        tx = Transaction()
        tx.add_input(
            prev_tx_hash='0' * 64,
            output_index=0,
            amount=amount,
            sender_address=account.public_address
        )
        tx.add_output(to_address, amount)
        tx.calculate_hash()
        
        # Send to network via RPC
        try:
            response = requests.post(
                f"{self.rpc_endpoint}/api/rpc",
                json={
                    'jsonrpc': '2.0',
                    'method': 'send_transaction',
                    'params': [tx.to_dict()],
                    'id': 1,
                }
            )
            result = response.json()
            
            if 'result' in result:
                print(f"✓ Transaction sent: {tx.tx_hash}")
            else:
                print(f"✗ Transaction failed: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f"✗ Error sending transaction: {e}")

    def show_balance(self, wallet_name: str, account_index: int, password: str = ""):
        """Show account balance"""
        if not self.load_wallet(wallet_name, password):
            return
        
        wallet = self.current_wallet
        account = wallet.get_account(account_index)
        
        if not account:
            print(f"✗ Account {account_index} not found")
            return
        
        print(f"\n{'='*60}")
        print(f"  ACCOUNT {account_index}: {account['name']}")
        print(f"{'='*60}\n")
        
        print(f"Address: {account['public_address']}")
        print(f"Balance: {account['balance']} ANR\n")

    def export_keys(self, wallet_name: str, account_index: int, password: str = ""):
        """Export account keys"""
        if not self.load_wallet(wallet_name, password):
            return
        
        wallet = self.current_wallet
        keys = wallet.export_keys(account_index)
        
        if not keys:
            print(f"✗ Account {account_index} not found")
            return
        
        print(f"\n{'='*60}")
        print(f"  ACCOUNT KEYS (KEEP SAFE!)")
        print(f"{'='*60}\n")
        
        print(f"Public Address: {keys['public_address']}")
        print(f"Spend Key: {keys['spend_key']}")
        print(f"View Key: {keys['view_key']}\n")

    def create_token(self, wallet_name: str, token_name: str, symbol: str, 
                    supply: float, password: str = ""):
        """Create token"""
        if not self.load_wallet(wallet_name, password):
            return
        
        account = self.current_wallet.get_primary_account()
        
        try:
            response = requests.post(
                f"{self.rpc_endpoint}/api/rpc",
                json={
                    'jsonrpc': '2.0',
                    'method': 'create_token',
                    'params': [token_name, symbol, supply, account.public_address],
                    'id': 1,
                }
            )
            result = response.json()
            
            if 'result' in result:
                token_id = result['result'].get('token_id')
                print(f"✓ Token created: {token_id}")
            else:
                print(f"✗ Token creation failed: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f"✗ Error creating token: {e}")

    def send_token(self, wallet_name: str, account_index: int, token_id: str,
                  to_address: str, amount: float, password: str = ""):
        """Send token"""
        if not self.load_wallet(wallet_name, password):
            return
        
        wallet = self.current_wallet
        account = wallet.get_account(account_index)
        
        if not account:
            print(f"✗ Account {account_index} not found")
            return
        
        from blockchain_transaction import TokenTransaction
        tx = TokenTransaction('transfer', token_id, account.public_address, to_address, amount)
        tx.calculate_hash()
        
        try:
            response = requests.post(
                f"{self.rpc_endpoint}/api/rpc",
                json={
                    'jsonrpc': '2.0',
                    'method': 'send_transaction',
                    'params': [tx.to_dict()],
                    'id': 1,
                }
            )
            result = response.json()
            
            if 'result' in result:
                print(f"✓ Token transferred: {tx.tx_hash}")
            else:
                print(f"✗ Token transfer failed: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f"✗ Error sending token: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Anero Blockchain Wallet CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create wallet
    create = subparsers.add_parser('create-wallet', help='Create new wallet')
    create.add_argument('--name', required=True, help='Wallet name')
    create.add_argument('--password', default='', help='Wallet password')
    
    # Restore wallet
    restore = subparsers.add_parser('restore-wallet', help='Restore wallet from mnemonic')
    restore.add_argument('--name', required=True, help='Wallet name')
    restore.add_argument('--mnemonic', required=True, help='Mnemonic phrase')
    restore.add_argument('--password', default='', help='Wallet password')
    
    # Show wallet info
    show = subparsers.add_parser('show-wallet-info', help='Show wallet information')
    show.add_argument('--wallet', required=True, help='Wallet name')
    show.add_argument('--password', default='', help='Wallet password')
    
    # List wallets
    subparsers.add_parser('list-wallets', help='List all wallets')
    
    # Send transaction
    send = subparsers.add_parser('send', help='Send ANR')
    send.add_argument('--wallet', required=True, help='Wallet name')
    send.add_argument('--account', type=int, default=0, help='Account index')
    send.add_argument('--to', required=True, help='Recipient address')
    send.add_argument('--amount', type=float, required=True, help='Amount to send')
    send.add_argument('--password', default='', help='Wallet password')
    
    # Show balance
    balance = subparsers.add_parser('balance', help='Show account balance')
    balance.add_argument('--wallet', required=True, help='Wallet name')
    balance.add_argument('--account', type=int, default=0, help='Account index')
    balance.add_argument('--password', default='', help='Wallet password')
    
    # Export keys
    export = subparsers.add_parser('export-keys', help='Export account keys')
    export.add_argument('--wallet', required=True, help='Wallet name')
    export.add_argument('--account', type=int, default=0, help='Account index')
    export.add_argument('--password', default='', help='Wallet password')
    
    # Create token
    token = subparsers.add_parser('create-token', help='Create token')
    token.add_argument('--wallet', required=True, help='Wallet name')
    token.add_argument('--name', required=True, help='Token name')
    token.add_argument('--symbol', required=True, help='Token symbol')
    token.add_argument('--supply', type=float, required=True, help='Initial supply')
    token.add_argument('--password', default='', help='Wallet password')
    
    # Send token
    send_token = subparsers.add_parser('send-token', help='Send token')
    send_token.add_argument('--wallet', required=True, help='Wallet name')
    send_token.add_argument('--account', type=int, default=0, help='Account index')
    send_token.add_argument('--token-id', required=True, help='Token ID')
    send_token.add_argument('--to', required=True, help='Recipient address')
    send_token.add_argument('--amount', type=float, required=True, help='Amount to send')
    send_token.add_argument('--password', default='', help='Wallet password')
    
    args = parser.parse_args()
    cli = WalletCLI()
    
    if args.command == 'create-wallet':
        cli.create_wallet(args.name, args.password)
    elif args.command == 'restore-wallet':
        cli.restore_wallet(args.name, args.mnemonic, args.password)
    elif args.command == 'show-wallet-info':
        cli.show_wallet_info(args.wallet)
    elif args.command == 'list-wallets':
        cli.list_wallets()
    elif args.command == 'send':
        cli.send_transaction(args.wallet, args.account, args.to, args.amount, args.password)
    elif args.command == 'balance':
        cli.show_balance(args.wallet, args.account, args.password)
    elif args.command == 'export-keys':
        cli.export_keys(args.wallet, args.account, args.password)
    elif args.command == 'create-token':
        cli.create_token(args.wallet, args.name, args.symbol, args.supply, args.password)
    elif args.command == 'send-token':
        cli.send_token(args.wallet, args.account, args.token_id, args.to, args.amount, args.password)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
