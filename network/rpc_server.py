# network/rpc_server.py - JSON-RPC API Server

import json
import threading
from typing import Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import config

class RPCServer:
    """JSON-RPC Server for blockchain interaction"""

    def __init__(self, host: str, port: int, blockchain, wallet_manager):
        """Initialize RPC server"""
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.wallet_manager = wallet_manager
        self.app = Flask(__name__)
        CORS(self.app)
        
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/rpc', methods=['POST'])
        def handle_rpc():
            """Handle JSON-RPC requests"""
            try:
                data = request.get_json()
                method = data.get('method')
                params = data.get('params', [])
                rpc_id = data.get('id')
                
                result = self._dispatch_method(method, params)
                
                return jsonify({
                    'jsonrpc': '2.0',
                    'result': result,
                    'id': rpc_id,
                })
            except Exception as e:
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -1, 'message': str(e)},
                    'id': rpc_id,
                })

        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get blockchain status"""
            return jsonify({
                'height': self.blockchain.get_chain_height(),
                'total_blocks': self.blockchain.get_chain_length(),
                'pending_txs': self.blockchain.get_pending_transaction_count(),
                'difficulty': self.blockchain.get_current_difficulty(),
            })

        @self.app.route('/api/balance/<address>', methods=['GET'])
        def get_balance(address):
            """Get account balance"""
            balance = self.blockchain.get_balance(address)
            return jsonify({'address': address, 'balance': balance})

    def _dispatch_method(self, method: str, params: list) -> Any:
        """Dispatch RPC method call"""
        
        # Blockchain methods
        if method == 'get_blockchain_height':
            return self.blockchain.get_chain_height()
        
        elif method == 'get_block':
            block_height = params[0]
            block = self.blockchain.get_block_by_height(block_height)
            return block.to_dict() if block else None
        
        elif method == 'get_balance':
            address = params[0]
            return self.blockchain.get_balance(address)
        
        elif method == 'get_difficulty':
            return self.blockchain.get_current_difficulty()
        
        # Transaction methods
        elif method == 'send_transaction':
            from blockchain_transaction import Transaction
            tx_data = params[0]
            tx = Transaction.from_dict(tx_data)
            success = self.blockchain.add_pending_transaction(tx)
            return {'success': success, 'tx_hash': tx.tx_hash}
        
        elif method == 'get_transaction':
            tx_hash = params[0]
            tx = self.blockchain.get_transaction_by_hash(tx_hash)
            return tx.to_dict() if tx else None
        
        # Wallet methods
        elif method == 'create_wallet':
            wallet_name = params[0]
            wallet = self.wallet_manager.create_wallet(wallet_name)
            return {'success': True, 'wallet': wallet_name}
        
        elif method == 'get_wallet_info':
            wallet_name = params[0]
            wallet = self.wallet_manager.get_wallet(wallet_name)
            if wallet:
                return {'accounts': wallet.list_accounts()}
            return None
        
        # Token methods
        elif method == 'create_token':
            name = params[0]
            symbol = params[1]
            supply = params[2]
            creator = params[3]
            token_id = self.blockchain.token_manager.create_token(
                name, symbol, supply, creator
            )
            return {'token_id': token_id}
        
        elif method == 'get_token_balance':
            token_id = params[0]
            address = params[1]
            balance = self.blockchain.token_manager.get_token_balance(token_id, address)
            return {'token_id': token_id, 'address': address, 'balance': balance}
        
        # Smart contract methods
        elif method == 'deploy_contract':
            creator = params[0]
            code = params[1]
            contract_address = self.blockchain.contract_manager.deploy_contract(creator, code)
            return {'contract_address': contract_address}
        
        elif method == 'call_contract':
            contract_address = params[0]
            function_name = params[1]
            args = params[2] if len(params) > 2 else []
            result = self.blockchain.contract_manager.call_contract(
                contract_address, function_name, args
            )
            return {'result': result}
        
        else:
            raise ValueError(f"Unknown method: {method}")

    def start(self):
        """Start RPC server"""
        print(f"✓ RPC server starting on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True)

    def start_in_thread(self):
        """Start RPC server in background thread"""
        server_thread = threading.Thread(target=self.start, daemon=True)
        server_thread.start()
        return server_thread
