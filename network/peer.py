# network/peer.py - Peer Connection Management

import socket
import time
import json
from typing import Optional, Dict, Any
import config

class Peer:
    """Represents a connection to a peer node"""

    def __init__(self, peer_ip: str, peer_port: int):
        """
        Initialize peer connection
        
        Args:
            peer_ip: IP address of the peer
            peer_port: Port of the peer
        """
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.socket = None
        self.connected = False
        self.last_seen = time.time()
        self.messages_sent = 0
        self.messages_received = 0
        self.connection_attempts = 0
        self.last_attempt = None

    def connect(self) -> bool:
        """
        Establish connection to peer
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(config.P2P_TIMEOUT)
            self.socket.connect((self.peer_ip, self.peer_port))
            self.connected = True
            self.last_seen = time.time()
            self.connection_attempts = 0
            print(f"✓ Connected to peer {self.peer_ip}:{self.peer_port}")
            return True
        except socket.timeout:
            print(f"✗ Connection timeout to {self.peer_ip}:{self.peer_port}")
            self.connected = False
            self.connection_attempts += 1
            self.last_attempt = time.time()
            return False
        except ConnectionRefusedError:
            print(f"✗ Connection refused by {self.peer_ip}:{self.peer_port}")
            self.connected = False
            self.connection_attempts += 1
            self.last_attempt = time.time()
            return False
        except Exception as e:
            print(f"✗ Error connecting to {self.peer_ip}:{self.peer_port}: {e}")
            self.connected = False
            self.connection_attempts += 1
            self.last_attempt = time.time()
            return False

    def send_message(self, message: str) -> bool:
        """
        Send message to peer
        
        Args:
            message: Message to send (JSON string)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # Add newline delimiter
            msg_bytes = (message + "\n").encode('utf-8')
            self.socket.sendall(msg_bytes)
            self.messages_sent += 1
            self.last_seen = time.time()
            return True
        except socket.timeout:
            print(f"✗ Send timeout to {self.peer_ip}:{self.peer_port}")
            self.connected = False
            return False
        except BrokenPipeError:
            print(f"✗ Broken pipe to {self.peer_ip}:{self.peer_port}")
            self.connected = False
            return False
        except Exception as e:
            print(f"✗ Error sending to {self.peer_ip}:{self.peer_port}: {e}")
            self.connected = False
            return False

    def send_json(self, data: Dict[str, Any]) -> bool:
        """
        Send JSON data to peer
        
        Args:
            data: Dictionary to send as JSON
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            json_str = json.dumps(data)
            return self.send_message(json_str)
        except Exception as e:
            print(f"✗ Error serializing JSON: {e}")
            return False

    def receive_message(self) -> Optional[str]:
        """
        Receive message from peer
        
        Returns:
            Message string if received, None otherwise
        """
        if not self.connected:
            return None
        
        try:
            data = self.socket.recv(65536)
            
            if not data:
                print(f"✗ Peer {self.peer_ip}:{self.peer_port} disconnected")
                self.connected = False
                return None
            
            self.messages_received += 1
            self.last_seen = time.time()
            
            return data.decode('utf-8').strip()
        except socket.timeout:
            # Timeout is normal, just means no data available
            return None
        except UnicodeDecodeError:
            print(f"✗ Invalid UTF-8 from {self.peer_ip}:{self.peer_port}")
            self.connected = False
            return None
        except Exception as e:
            print(f"✗ Error receiving from {self.peer_ip}:{self.peer_port}: {e}")
            self.connected = False
            return None

    def receive_json(self) -> Optional[Dict[str, Any]]:
        """
        Receive and parse JSON from peer
        
        Returns:
            Parsed JSON dictionary if received, None otherwise
        """
        try:
            message = self.receive_message()
            if message:
                return json.loads(message)
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON from {self.peer_ip}:{self.peer_port}")
        except Exception as e:
            print(f"✗ Error parsing JSON: {e}")
        
        return None

    def disconnect(self):
        """Disconnect from peer"""
        try:
            if self.socket:
                self.socket.close()
            self.connected = False
            print(f"✓ Disconnected from {self.peer_ip}:{self.peer_port}")
        except Exception as e:
            print(f"✗ Error disconnecting: {e}")

    def is_alive(self) -> bool:
        """
        Check if peer connection is alive
        
        Returns:
            True if connected and not timed out, False otherwise
        """
        if not self.connected:
            return False
        
        time_since_seen = time.time() - self.last_seen
        
        if time_since_seen > config.P2P_TIMEOUT:
            print(f"✗ Peer {self.peer_ip}:{self.peer_port} timed out")
            self.disconnect()
            return False
        
        return True

    def get_info(self) -> Dict[str, Any]:
        """
        Get peer connection information
        
        Returns:
            Dictionary with connection stats
        """
        return {
            'ip': self.peer_ip,
            'port': self.peer_port,
            'connected': self.connected,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'connection_attempts': self.connection_attempts,
            'last_seen': self.last_seen,
            'uptime': time.time() - self.last_seen if self.connected else 0,
        }

    def __str__(self) -> str:
        """String representation of peer"""
        status = "🟢 Connected" if self.connected else "🔴 Disconnected"
        return f"{self.peer_ip}:{self.peer_port} [{status}] (sent: {self.messages_sent}, received: {self.messages_received})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"Peer({self.peer_ip}:{self.peer_port}, connected={self.connected})"

    def ping(self) -> bool:
        """
        Send ping to peer
        
        Returns:
            True if peer responds, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            ping_data = {'type': 'ping', 'timestamp': time.time()}
            return self.send_json(ping_data)
        except Exception:
            return False

    def reconnect(self) -> bool:
        """
        Attempt to reconnect to peer
        
        Returns:
            True if reconnection successful, False otherwise
        """
        self.disconnect()
        time.sleep(1)  # Wait before reconnecting
        return self.connect()

    def is_responding(self) -> bool:
        """
        Check if peer is responding (not dead)
        
        Returns:
            True if peer is responding, False if dead
        """
        # Check if we've had recent activity
        time_since_seen = time.time() - self.last_seen
        
        if self.connected:
            # If connected and recently seen, assume responding
            if time_since_seen < 5:
                return True
            # Try a ping
            return self.ping()
        
        # If disconnected, check if we can reconnect
        return self.is_alive()

    def reset_stats(self):
        """Reset connection statistics"""
        self.messages_sent = 0
        self.messages_received = 0
        self.connection_attempts = 0
        self.last_seen = time.time()

    def get_address(self) -> str:
        """
        Get peer address as string
        
        Returns:
            String in format "IP:PORT"
        """
        return f"{self.peer_ip}:{self.peer_port}"

    @staticmethod
    def from_address(address: str) -> 'Peer':
        """
        Create Peer from address string
        
        Args:
            address: Address in format "IP:PORT"
        
        Returns:
            New Peer instance
        
        Raises:
            ValueError: If address format is invalid
        """
        try:
            ip, port = address.split(':')
            return Peer(ip, int(port))
        except Exception as e:
            raise ValueError(f"Invalid address format: {address}. Must be 'IP:PORT'. Error: {e}")
