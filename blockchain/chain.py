# blockchain/chain.py - Main blockchain implementation

import json
import time
import sqlite3
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from blockchain_block import Block
from blockchain_transaction import Transaction, CoinbaseTransaction, TokenTransaction
from blockchain_utils import Utils
import config

class Blockchain:
    """Main blockchain class"""

    def __init__(self, node_type: str = "primary"):
        """Initialize blockchain"""
        self.node_type = node_type
        self.chain = []
        self.pending_transactions = []
        self.accounts = {}  # address -> balance
        self.token_ledger = {}  # token_id -> {owner_address -> balance}
        self.smart_contracts = {}  # contract_address -> contract_code
        self.db_path = config.DB_PATH
        
        self.init_database()
        self.load_chain_from_db()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Blocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                height INTEGER PRIMARY KEY,
                block_hash TEXT UNIQUE,
                previous_hash TEXT,
                timestamp INTEGER,
                nonce INTEGER,
                difficulty INTEGER,
                miner_address TEXT,
                block_data TEXT,
                created_at INTEGER
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                tx_hash TEXT PRIMARY KEY,
                block_height INTEGER,
                tx_type TEXT,
                from_address TEXT,
                to_address TEXT,
                amount REAL,
                timestamp INTEGER,
                tx_data TEXT
            )
        ''')
        
        # Account balances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_balances (
                address TEXT PRIMARY KEY,
                balance REAL,
                updated_at INTEGER
            )
        ''')
        
        # Token balances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_balances (
                token_id TEXT,
                address TEXT,
                balance REAL,
                PRIMARY KEY (token_id, address)
            )
        ''')
        
        # Smart contracts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smart_contracts (
                contract_address TEXT PRIMARY KEY,
                contract_code TEXT,
                creator_address TEXT,
                created_at INTEGER,
                state TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def load_chain_from_db(self):
        """Load blockchain from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT block_data FROM blocks ORDER BY height')
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                block_dict = json.loads(row[0])
                self.chain.append(Block.from_dict(block_dict))
            print(f"Loaded {len(self.chain)} blocks from database")
        
        conn.close()

    def save_block_to_db(self, block: Block):
        """Save block to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO blocks 
                (height, block_hash, previous_hash, timestamp, nonce, difficulty, miner_address, block_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                block.height,
                block.block_hash,
                block.previous_hash,
                block.timestamp,
                block.nonce,
                block.difficulty,
                block.miner_address,
                block.to_json(),
                int(time.time())
            ))
            
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Block {block.height} already in database")
        finally:
            conn.close()

    def add_block(self, block: Block) -> bool:
        """Add block to chain"""
        # Validate block
        if not block.is_valid():
            print(f"Invalid block: {block.block_hash}")
            return False
        
        # Validate chain link
        if len(self.chain) > 0:
            last_block = self.chain[-1]
            if block.previous_hash != last_block.block_hash:
                print(f"Block doesn't link to previous: {block.previous_hash} != {last_block.block_hash}")
                return False
            
            if block.height != last_block.height + 1:
                print(f"Invalid block height: {block.height} != {last_block.height + 1}")
                return False
        
        # Validate transactions
        for tx_dict in block.transactions:
            tx = Transaction.from_dict(tx_dict)
            if not tx.is_valid():
                print(f"Invalid transaction in block: {tx.tx_hash}")
                return False
        
        # Add to chain
        self.chain.append(block)
        
        # Update state
        self.process_block_transactions(block)
        
        # Save to database
        self.save_block_to_db(block)
        
        print(f"✓ Block {block.height} added to chain")
        return True

    def process_block_transactions(self, block: Block):
        """Process transactions in block"""
        for tx_dict in block.transactions:
            tx = Transaction.from_dict(tx_dict)
            self.process_transaction(tx)

    def process_transaction(self, tx: Transaction):
        """Process single transaction"""
        # Update account balances
        for inp in tx.inputs:
            address = inp['sender_address']
            amount = inp['amount']
            self.accounts[address] = self.accounts.get(address, 0) - amount
        
        for out in tx.outputs:
            address = out['recipient_address']
            amount = out['amount']
            self.accounts[address] = self.accounts.get(address, 0) + amount

    def create_block_from_pending_transactions(self, miner_address: str) -> Block:
        """Create new block from pending transactions"""
        block = Block()
        block.height = len(self.chain)
        block.timestamp = int(time.time())
        block.difficulty = self.get_current_difficulty()
        
        if len(self.chain) > 0:
            block.previous_hash = self.chain[-1].block_hash
        else:
            block.previous_hash = '0' * 64
        
        # Add pending transactions
        for tx in self.pending_transactions:
            if block.get_size() + len(tx.to_json()) < config.MAX_BLOCK_SIZE:
                block.add_transaction(tx)
        
        # Add coinbase (mining reward)
        reward = Utils.calculate_block_reward(block.height)
        coinbase = CoinbaseTransaction(miner_address, reward, block.height)
        coinbase.calculate_hash()
        block.add_transaction(coinbase)
        
        # Clear pending transactions that were added
        self.pending_transactions = self.pending_transactions[len(block.transactions) - 1:]
        
        return block

    def add_pending_transaction(self, tx: Transaction) -> bool:
        """Add transaction to pending pool"""
        if not tx.is_valid():
            return False
        
        tx.calculate_hash()
        
        # Check if already exists
        for ptx in self.pending_transactions:
            if ptx.tx_hash == tx.tx_hash:
                return False
        
        self.pending_transactions.append(tx)
        return True

    def get_balance(self, address: str) -> float:
        """Get account balance"""
        return self.accounts.get(address, 0)

    def get_token_balance(self, token_id: str, address: str) -> float:
        """Get token balance"""
        if token_id not in self.token_ledger:
            return 0
        
        return self.token_ledger[token_id].get(address, 0)

    def get_current_difficulty(self) -> int:
        """Get current difficulty with adjustment"""
        if len(self.chain) < config.DIFFICULTY_ADJUSTMENT_INTERVAL:
            return config.INITIAL_DIFFICULTY
        
        # Adjust difficulty every N blocks
        if len(self.chain) % config.DIFFICULTY_ADJUSTMENT_INTERVAL == 0:
            # Get time span of last N blocks
            old_block = self.chain[-config.DIFFICULTY_ADJUSTMENT_INTERVAL]
            new_block = self.chain[-1]
            time_span = new_block.timestamp - old_block.timestamp
            
            # Target time span
            target_time_span = config.BLOCK_TIME * config.DIFFICULTY_ADJUSTMENT_INTERVAL
            
            # Adjust difficulty
            if time_span > 0:
                difficulty = self.chain[-1].difficulty * target_time_span / time_span
                # Limit adjustments
                max_adjustment = self.chain[-1].difficulty * 4
                min_adjustment = self.chain[-1].difficulty / 4
                return int(max(min_adjustment, min(max_adjustment, difficulty)))
        
        return self.chain[-1].difficulty if self.chain else config.INITIAL_DIFFICULTY

    def get_block_by_height(self, height: int) -> Optional[Block]:
        """Get block by height"""
        if 0 <= height < len(self.chain):
            return self.chain[height]
        return None

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """Get block by hash"""
        for block in self.chain:
            if block.block_hash == block_hash:
                return block
        return None

    def get_transaction_by_hash(self, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash"""
        for block in self.chain:
            for tx_dict in block.transactions:
                tx = Transaction.from_dict(tx_dict)
                if tx.tx_hash == tx_hash:
                    return tx
        return None

    def is_valid(self) -> bool:
        """Validate entire blockchain"""
        for i, block in enumerate(self.chain):
            if not block.is_valid():
                return False
            
            if i > 0:
                if block.previous_hash != self.chain[i - 1].block_hash:
                    return False
        
        return True

    def get_chain_height(self) -> int:
        """Get blockchain height"""
        return len(self.chain) - 1 if self.chain else -1

    def get_chain_length(self) -> int:
        """Get total blocks"""
        return len(self.chain)

    def get_pending_transaction_count(self) -> int:
        """Get pending transaction count"""
        return len(self.pending_transactions)
