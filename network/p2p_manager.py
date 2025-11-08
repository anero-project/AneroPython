# network/p2p_manager.py - P2P Network Management

import socket
import json
import threading
import time
from typing import Dict, List, Optional
from queue import Queue
import config

class P2PMessage:
    """Represents a P2P message"""
    
    MSG_TYPE_BLOCK = "block"
    MSG_TYPE_TRANSACTION = "transaction"
    MSG_TYPE_PING = "ping"
    MSG_TYPE_PONG = "pong"
    MSG_TYPE_SYNC_REQUEST = "sync_request"
    MSG_TYPE_SYNC_RESPONSE = "sync_response"

    def __init__(self, msg_type: str, data: Dict):
        """Initialize message"""
        self.msg_type = msg_type
        self.data = data
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'type': self.msg_type,
            'data': self.data,
            'timestamp': self.timestamp,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(msg_dict: Dict) -> 'P2PMessage':
        """Create message from dictionary"""
        return P2PMessage(msg_dict['type'], msg_dict['data'])

    @staticmethod
    def from_json(msg_json: str) -> 'P2PMessage':
        """Create message from JSON"""
        return P2PMessage.from_dict(json.loads(msg_json))


class PeerConnection:
    """Represents a connection to a peer"""

    def __init__(self, peer_ip: str, peer_port: int):
        """Initialize peer connection"""
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.socket = None
        self.connected = False
        self.last_seen = time.time()
        self.messages_sent = 0
        self.messages_received = 0

    def connect(self) -> bool:
        """Connect to peer"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(config.P2P_TIMEOUT)
            self.socket.connect((self.peer_ip, self.peer_port))
            self.connected = True
            self.last_seen = time.time()
            return True
        except Exception as e:
            print(f"Failed to connect to peer {self.peer_ip}:{self.peer_port}: {e}")
            self.connected = False
            return False

    def send_message(self, message: P2PMessage) -> bool:
        """Send message to peer"""
        if not self.connected:
            return False
        
        try:
            msg_json = message.to_json()
            self.socket.sendall((msg_json + "\n").encode())
            self.messages_sent += 1
            self.last_seen = time.time()
            return True
        except Exception as e:
            print(f"Error sending message to {self.peer_ip}:{self.peer_port}: {e}")
            self.connected = False
            return False

    def receive_message(self) -> Optional[P2PMessage]:
        """Receive message from peer"""
        if not self.connected:
            return None
        
        try:
            data = self.socket.recv(65536)
            if not data:
                self.connected = False
                return None
            
            msg_json = data.decode().strip()
            self.messages_received += 1
            self.last_seen = time.time()
            
            return P2PMessage.from_json(msg_json)
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Error receiving message from {self.peer_ip}:{self.peer_port}: {e}")
            self.connected = False
            return None

    def disconnect(self):
        """Disconnect from peer"""
        try:
            if self.socket:
                self.socket.close()
            self.connected = False
        except Exception as e:
            print(f"Error disconnecting from peer: {e}")

    def is_alive(self) -> bool:
        """Check if connection is alive"""
        return self.connected and (time.time() - self.last_seen) < config.P2P_TIMEOUT


class P2PManager:
    """Manages P2P networking"""

    def __init__(self, local_ip: str, local_port: int):
        """Initialize P2P manager"""
        self.local_ip = local_ip
        self.local_port = local_port
        self.peers = {}  # (ip, port) -> PeerConnection
        self.incoming_messages = Queue(maxsize=config.P2P_MESSAGE_QUEUE_SIZE)
        self.server_socket = None
        self.running = False
        self.message_handlers = {}

    def start_server(self) -> bool:
        """Start P2P server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.local_ip, self.local_port))
            self.server_socket.listen(config.P2P_MAX_CONNECTIONS)
            self.running = True
            
            # Start server thread
            server_thread = threading.Thread(target=self._accept_connections, daemon=True)
            server_thread.start()
            
            print(f"✓ P2P server started on {self.local_ip}:{self.local_port}")
            return True
        except Exception as e:
            print(f"Error starting P2P server: {e}")
            return False

    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, (client_ip, client_port) = self.server_socket.accept()
                print(f"Incoming connection from {client_ip}:{client_port}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_ip, client_port),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")

    def _handle_client(self, client_socket: socket.socket, client_ip: str, client_port: int):
        """Handle incoming client connection"""
        try:
            while self.running:
                data = client_socket.recv(65536)
                if not data:
                    break
                
                msg_json = data.decode().strip()
                message = P2PMessage.from_json(msg_json)
                
                # Add to queue
                self.incoming_messages.put(message)
                
                # Call handler if registered
                if message.msg_type in self.message_handlers:
                    handler = self.message_handlers[message.msg_type]
                    handler(message, client_ip, client_port)
        except Exception as e:
            print(f"Error handling client {client_ip}:{client_port}: {e}")
        finally:
            client_socket.close()

    def connect_to_peer(self, peer_ip: str, peer_port: int) -> bool:
        """Connect to a peer"""
        key = (peer_ip, peer_port)
        
        if key in self.peers:
            peer = self.peers[key]
            if peer.is_alive():
                return True
        
        peer = PeerConnection(peer_ip, peer_port)
        if peer.connect():
            self.peers[key] = peer
            print(f"✓ Connected to peer {peer_ip}:{peer_port}")
            return True
        
        return False

    def send_message_to_peer(self, peer_ip: str, peer_port: int, message: P2PMessage) -> bool:
        """Send message to specific peer"""
        key = (peer_ip, peer_port)
        
        if key not in self.peers:
            if not self.connect_to_peer(peer_ip, peer_port):
                return False
        
        peer = self.peers[key]
        return peer.send_message(message)

    def broadcast_message(self, message: P2PMessage) -> int:
        """Broadcast message to all peers"""
        sent_count = 0
        
        for peer in list(self.peers.values()):
            if peer.is_alive():
                if peer.send_message(message):
                    sent_count += 1
        
        return sent_count

    def register_message_handler(self, msg_type: str, handler):
        """Register handler for message type"""
        self.message_handlers[msg_type] = handler

    def get_connected_peers(self) -> List[Dict]:
        """Get list of connected peers"""
        peers = []
        for (ip, port), peer in self.peers.items():
            if peer.is_alive():
                peers.append({
                    'ip': ip,
                    'port': port,
                    'messages_sent': peer.messages_sent,
                    'messages_received': peer.messages_received,
                })
        return peers

    def stop(self):
        """Stop P2P manager"""
        self.running = False
        
        for peer in self.peers.values():
            peer.disconnect()
        
        if self.server_socket:
            self.server_socket.close()
        
        print("✓ P2P manager stopped")
