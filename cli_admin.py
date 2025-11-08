# cli_admin.py - Admin CLI for Blockchain Management

import argparse
import requests
from pathlib import Path
from wallet_wallet import Wallet
import config

class AdminCLI:
    """Administrator command-line interface"""

    def __init__(self, rpc_endpoint: str = "http://localhost:54374"):
        """Initialize admin CLI"""
        self.rpc_endpoint = rpc_endpoint

    def initialize_premine(self, amount: float):
        """Initialize premine"""
        # Premine is initialized in daemon.py during genesis block creation
        print(f"✓ Premine initialization is handled by the daemon")
        print(f"  Check daemon logs for premine address and amount")

    def get_blockchain_status(self):
        """Get blockchain status"""
        try:
            response = requests.get(f"{self.rpc_endpoint}/api/status")
            status = response.json()
            
            print(f"\n{'='*60}")
            print(f"  BLOCKCHAIN STATUS")
            print(f"{'='*60}\n")
            
            print(f"Height: {status.get('height')}")
            print(f"Total Blocks: {status.get('total_blocks')}")
            print(f"Pending Transactions: {status.get('pending_txs')}")
            print(f"Current Difficulty: {status.get('difficulty')}\n")
        except Exception as e:
            print(f"✗ Error getting blockchain status: {e}")

    def get_balance(self, address: str):
        """Get account balance"""
        try:
            response = requests.get(f"{self.rpc_endpoint}/api/balance/{address}")
            data = response.json()
            
            print(f"\n{'='*60}")
            print(f"  ACCOUNT BALANCE")
            print(f"{'='*60}\n")
            
            print(f"Address: {data.get('address')}")
            print(f"Balance: {data.get('balance')} ANR\n")
        except Exception as e:
            print(f"✗ Error getting balance: {e}")

    def get_block(self, height: int):
        """Get block by height"""
        try:
            response = requests.post(
                f"{self.rpc_endpoint}/api/rpc",
                json={
                    'jsonrpc': '2.0',
                    'method': 'get_block',
                    'params': [height],
                    'id': 1,
                }
            )
            result = response.json()
            
            if 'result' in result and result['result']:
                block = result['result']
                
                print(f"\n{'='*60}")
                print(f"  BLOCK #{height}")
                print(f"{'='*60}\n")
                
                print(f"Hash: {block.get('block_hash')}")
                print(f"Previous Hash: {block.get('previous_hash')}")
                print(f"Timestamp: {block.get('timestamp')}")
                print(f"Nonce: {block.get('nonce')}")
                print(f"Difficulty: {block.get('difficulty')}")
                print(f"Miner: {block.get('miner_address')}")
                print(f"Transactions: {len(block.get('transactions', []))}\n")
            else:
                print(f"✗ Block {height} not found")
        except Exception as e:
            print(f"✗ Error getting block: {e}")

    def create_token(self, name: str, symbol: str, supply: float, creator_address: str):
        """Create token (ANC-65)"""
        try:
            response = requests.post(
                f"{self.rpc_endpoint}/api/rpc",
                json={
                    'jsonrpc': '2.0',
                    'method': 'create_token',
                    'params': [name, symbol, supply, creator_address],
                    'id': 1,
                }
            )
            result = response.json()
            
            if 'result' in result:
                token_id = result['result'].get('token_id')
                
                print(f"\n{'='*60}")
                print(f"  TOKEN CREATED (ANC-65)")
                print(f"{'='*60}\n")
                
                print(f"Name: {name}")
                print(f"Symbol: {symbol}")
                print(f"Total Supply: {supply}")
                print(f"Creator: {creator_address}")
                print(f"Token ID: {token_id}\n")
            else:
                print(f"✗ Token creation failed: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f"✗ Error creating token: {e}")

    def deploy_contract(self, code_file: str):
        """Deploy smart contract"""
        try:
            with open(code_file, 'r') as f:
                code = f.read()
            
            # Get creator address from premine wallet
            premine_wallet = Wallet("premine")
            if not premine_wallet.load_from_file():
                print("✗ Failed to load premine wallet")
                return
            
            creator = premine_wallet.get_primary_account().public_address
            
            response = requests.post(
                f"{self.rpc_endpoint}/api/rpc",
                json={
                    'jsonrpc': '2.0',
                    'method': 'deploy_contract',
                    'params': [creator, code],
                    'id': 1,
                }
            )
            result = response.json()
            
            if 'result' in result:
                contract_address = result['result'].get('contract_address')
                
                print(f"\n{'='*60}")
                print(f"  SMART CONTRACT DEPLOYED")
                print(f"{'='*60}\n")
                
                print(f"Creator: {creator}")
                print(f"Contract Address: {contract_address}")
                print(f"File: {code_file}\n")
            else:
                print(f"✗ Contract deployment failed: {result.get('error', {}).get('message')}")
        except FileNotFoundError:
            print(f"✗ File not found: {code_file}")
        except Exception as e:
            print(f"✗ Error deploying contract: {e}")

    def call_contract(self, contract_address: str, function_name: str, args: list = None):
        """Call contract function"""
        try:
            if args is None:
                args = []
            
            response = requests.post(
                f"{self.rpc_endpoint}/api/rpc",
                json={
                    'jsonrpc': '2.0',
                    'method': 'call_contract',
                    'params': [contract_address, function_name, args],
                    'id': 1,
                }
            )
            result = response.json()
            
            if 'result' in result:
                output = result['result'].get('result')
                
                print(f"\n{'='*60}")
                print(f"  CONTRACT CALL RESULT")
                print(f"{'='*60}\n")
                
                print(f"Contract: {contract_address}")
                print(f"Function: {function_name}")
                print(f"Result: {output}\n")
            else:
                print(f"✗ Contract call failed: {result.get('error', {}).get('message')}")
        except Exception as e:
            print(f"✗ Error calling contract: {e}")

    def list_accounts(self):
        """List all accounts in premine wallet"""
        try:
            premine_wallet = Wallet("premine")
            if not premine_wallet.load_from_file():
                print("✗ Failed to load premine wallet")
                return
            
            print(f"\n{'='*60}")
            print(f"  ACCOUNTS")
            print(f"{'='*60}\n")
            
            for account in premine_wallet.list_accounts():
                print(f"Account {account['account_index']}: {account['name']}")
                print(f"  Address: {account['public_address']}")
                print(f"  Balance: {account['balance']} ANR\n")
        except Exception as e:
            print(f"✗ Error listing accounts: {e}")


def main():
    """Main admin CLI entry point"""
    parser = argparse.ArgumentParser(description='Anero Blockchain Admin CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Initialize premine
    premine = subparsers.add_parser('initialize-premine', help='Initialize premine')
    premine.add_argument('--amount', type=float, default=config.PREMINE, help='Premine amount')
    
    # Get blockchain status
    subparsers.add_parser('status', help='Get blockchain status')
    
    # Get balance
    balance = subparsers.add_parser('get-balance', help='Get account balance')
    balance.add_argument('--address', required=True, help='Account address')
    
    # Get block
    block = subparsers.add_parser('get-block', help='Get block by height')
    block.add_argument('--height', type=int, required=True, help='Block height')
    
    # Create token
    token = subparsers.add_parser('create-token', help='Create token (ANC-65)')
    token.add_argument('--name', required=True, help='Token name')
    token.add_argument('--symbol', required=True, help='Token symbol')
    token.add_argument('--supply', type=float, required=True, help='Total supply')
    token.add_argument('--creator', default='', help='Creator address')
    
    # Deploy contract
    deploy = subparsers.add_parser('deploy-contract', help='Deploy smart contract')
    deploy.add_argument('--file', required=True, help='Python contract file')
    
    # Call contract
    call = subparsers.add_parser('call-contract', help='Call contract function')
    call.add_argument('--contract', required=True, help='Contract address')
    call.add_argument('--function', required=True, help='Function name')
    call.add_argument('--args', default='', help='Function arguments (comma-separated)')
    
    # List accounts
    subparsers.add_parser('list-accounts', help='List all accounts')
    
    args = parser.parse_args()
    cli = AdminCLI()
    
    if args.command == 'initialize-premine':
        cli.initialize_premine(args.amount)
    elif args.command == 'status':
        cli.get_blockchain_status()
    elif args.command == 'get-balance':
        cli.get_balance(args.address)
    elif args.command == 'get-block':
        cli.get_block(args.height)
    elif args.command == 'create-token':
        creator = args.creator or "0" * 64
        cli.create_token(args.name, args.symbol, args.supply, creator)
    elif args.command == 'deploy-contract':
        cli.deploy_contract(args.file)
    elif args.command == 'call-contract':
        func_args = [x.strip() for x in args.args.split(',')] if args.args else []
        cli.call_contract(args.contract, args.function, func_args)
    elif args.command == 'list-accounts':
        cli.list_accounts()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
