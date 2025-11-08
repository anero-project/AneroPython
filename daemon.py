# daemon.py - Anero Blockchain Daemon

import argparse
import time
import threading
import signal
import sys
from blockchain_chain import Blockchain
from blockchain_block import Block
from blockchain_transaction import CoinbaseTransaction
from blockchain_token import TokenManager
from blockchain_smart_contract import SmartContractManager
from network_p2p_manager import P2PManager, P2PMessage
from network_rpc_server import RPCServer
from wallet_wallet import Wallet
import config

class BlockchainDaemon:
    """Main blockchain daemon"""

    def __init__(self, node_type: str = "primary", rpc_port: int = None, p2p_port: int = None):
        """Initialize daemon"""
        self.node_type = node_type
        self.running = True
        
        # Setup ports
        if node_type == "primary":
            self.rpc_port = rpc_port or config.PRIMARY_NODE_RPC_PORT
            self.p2p_port = p2p_port or config.PRIMARY_NODE_PORT
            self.node_ip = config.PRIMARY_NODE_IP
        else:
            self.rpc_port = rpc_port or config.SECONDARY_NODE_RPC_PORT
            self.p2p_port = p2p_port or config.SECONDARY_NODE_PORT
            self.node_ip = config.SECONDARY_NODE_IP
        
        # Initialize components
        self.blockchain = Blockchain(node_type)
        self.token_manager = TokenManager()
        self.contract_manager = SmartContractManager()
        
        # Set references
        self.blockchain.token_manager = self.token_manager
        self.blockchain.contract_manager = self.contract_manager
        
        # Network components
        self.p2p_manager = P2PManager(self.node_ip, self.p2p_port)
        self.rpc_server = RPCServer("0.0.0.0", self.rpc_port, self.blockchain, None)
        
        # Initialize premine wallet
        self.premine_wallet = None
        self._setup_premine()
        
        # Register message handlers
        self._register_handlers()

    def _setup_premine(self):
        """Setup premine wallet"""
        premine_wallet_path = config.WALLET_DIR / "premine.json"
        
        if premine_wallet_path.exists():
            print("Premine wallet already exists")
            self.premine_wallet = Wallet("premine")
            self.premine_wallet.load_from_file("")
        else:
            print("Creating premine wallet...")
            self.premine_wallet = Wallet("premine")
            mnemonic = self.premine_wallet.create_new()
            self.premine_wallet.save_to_file("")
            
            # Initialize blockchain with premine
            primary_account = self.premine_wallet.get_primary_account()
            if not self.blockchain.chain:
                genesis_block = Block.create_genesis_block(primary_account.public_address)
                self.blockchain.add_block(genesis_block)
                primary_account.balance = config.PREMINE
                
                print(f"✓ Genesis block created")
                print(f"  Premine address: {primary_account.public_address}")
                print(f"  Premine amount: {config.PREMINE} ANR")
                print(f"  Mnemonic: {mnemonic}")

    def _register_handlers(self):
        """Register P2P message handlers"""
        self.p2p_manager.register_message_handler(
            P2PMessage.MSG_TYPE_BLOCK, self._handle_block
        )
        self.p2p_manager.register_message_handler(
            P2PMessage.MSG_TYPE_TRANSACTION, self._handle_transaction
        )
        self.p2p_manager.register_message_handler(
            P2PMessage.MSG_TYPE_PING, self._handle_ping
        )
        self.p2p_manager.register_message_handler(
            P2PMessage.MSG_TYPE_SYNC_REQUEST, self._handle_sync_request
        )

    def _handle_block(self, message: P2PMessage, peer_ip: str, peer_port: int):
        """Handle incoming block"""
        try:
            block_dict = message.data
            block = Block.from_dict(block_dict)
            self.blockchain.add_block(block)
            
            # Broadcast to other peers
            self.p2p_manager.broadcast_message(message)
        except Exception as e:
            print(f"Error handling block: {e}")

    def _handle_transaction(self, message: P2PMessage, peer_ip: str, peer_port: int):
        """Handle incoming transaction"""
        try:
            from blockchain_transaction import Transaction
            tx_dict = message.data
            tx = Transaction.from_dict(tx_dict)
            self.blockchain.add_pending_transaction(tx)
            
            # Broadcast to other peers
            self.p2p_manager.broadcast_message(message)
        except Exception as e:
            print(f"Error handling transaction: {e}")

    def _handle_ping(self, message: P2PMessage, peer_ip: str, peer_port: int):
        """Handle ping message"""
        pong = P2PMessage(P2PMessage.MSG_TYPE_PONG, {'node_id': self.node_type})
        self.p2p_manager.send_message_to_peer(peer_ip, peer_port, pong)

    def _handle_sync_request(self, message: P2PMessage, peer_ip: str, peer_port: int):
        """Handle blockchain sync request"""
        try:
            start_height = message.data.get('start_height', 0)
            blocks = []
            
            for i in range(start_height, min(start_height + config.P2P_SYNC_BATCH_SIZE, 
                                            len(self.blockchain.chain))):
                block = self.blockchain.get_block_by_height(i)
                if block:
                    blocks.append(block.to_dict())
            
            response = P2PMessage(P2PMessage.MSG_TYPE_SYNC_RESPONSE, {
                'blocks': blocks,
                'total_height': self.blockchain.get_chain_height(),
            })
            self.p2p_manager.send_message_to_peer(peer_ip, peer_port, response)
        except Exception as e:
            print(f"Error handling sync request: {e}")

    def connect_to_seed_nodes(self):
        """Connect to seed nodes"""
        for seed_node in config.SEED_NODES:
            if seed_node['ip'] == self.node_ip:
                continue  # Skip self
            
            print(f"Connecting to seed node {seed_node['ip']}:{seed_node['p2p_port']}...")
            self.p2p_manager.connect_to_peer(seed_node['ip'], seed_node['p2p_port'])

    def mining_loop(self):
        """Main mining loop"""
        while self.running:
            try:
                # Create block from pending transactions
                premine_account = self.premine_wallet.get_primary_account()
                block = self.blockchain.create_block_from_pending_transactions(
                    premine_account.public_address
                )
                
                print(f"\nMining block {block.height}...")
                
                # Mine the block
                block.mine(premine_account.public_address)
                
                # Add to blockchain
                if self.blockchain.add_block(block):
                    # Update premine balance
                    premine_account.balance += config.INITIAL_BLOCK_REWARD
                    
                    # Broadcast block
                    msg = P2PMessage(P2PMessage.MSG_TYPE_BLOCK, block.to_dict())
                    self.p2p_manager.broadcast_message(msg)
                    
                    print(f"✓ Block {block.height} added to chain")
                
                # Wait before mining next block
                time.sleep(1)
            except Exception as e:
                print(f"Error in mining loop: {e}")
                time.sleep(5)

    def start(self):
        """Start daemon"""
        print(f"\n{'='*60}")
        print(f"  ANERO BLOCKCHAIN DAEMON")
        print(f"  Node Type: {self.node_type.upper()}")
        print(f"  RPC Port: {self.rpc_port}")
        print(f"  P2P Port: {self.p2p_port}")
        print(f"{'='*60}\n")
        
        # Start P2P server
        self.p2p_manager.start_server()
        
        # Connect to seed nodes
        if self.node_type == "secondary":
            self.connect_to_seed_nodes()
        
        # Start RPC server in thread
        self.rpc_server.start_in_thread()
        print(f"✓ RPC server started on port {self.rpc_port}")
        
        # Start mining loop in thread
        mining_thread = threading.Thread(target=self.mining_loop, daemon=True)
        mining_thread.start()
        print(f"✓ Mining started\n")
        
        # Keep daemon running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop daemon"""
        print("\n\nShutting down...")
        self.running = False
        self.p2p_manager.stop()
        print("✓ Daemon stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Anero Blockchain Daemon')
    parser.add_argument('--node', type=str, choices=['primary', 'secondary'], 
                       default='primary', help='Node type')
    parser.add_argument('--rpc-port', type=int, default=None, help='RPC port')
    parser.add_argument('--p2p-port', type=int, default=None, help='P2P port')
    parser.add_argument('--peer', type=str, default=None, 
                       help='Peer to connect to (ip:port)')
    
    args = parser.parse_args()
    
    # Start daemon
    daemon = BlockchainDaemon(args.node, args.rpc_port, args.p2p_port)
    daemon.start()


if __name__ == '__main__':
    main()
