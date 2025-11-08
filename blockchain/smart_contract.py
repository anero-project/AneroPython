# blockchain/smart_contract.py - Smart Contract Implementation

import json
import time
from typing import Dict, List, Any, Optional
from blockchain_utils import Utils
import config

class SmartContract:
    """Represents a deployed smart contract"""

    def __init__(self, contract_data: Dict = None):
        """Initialize smart contract"""
        if contract_data:
            self.contract_address = contract_data.get('contract_address', '')
            self.creator_address = contract_data.get('creator_address', '')
            self.code = contract_data.get('code', '')
            self.abi = contract_data.get('abi', [])
            self.state = contract_data.get('state', {})
            self.created_at = contract_data.get('created_at', int(time.time()))
            self.balance = contract_data.get('balance', 0)
        else:
            self.contract_address = ''
            self.creator_address = ''
            self.code = ''
            self.abi = []
            self.state = {}
            self.created_at = int(time.time())
            self.balance = 0

    def generate_address(self) -> str:
        """Generate contract address"""
        data = f"{self.creator_address}{self.code}{self.created_at}"
        self.contract_address = Utils.hash_data(data)
        return self.contract_address

    def set_code(self, code: str):
        """Set contract code (Python)"""
        self.code = code

    def execute_function(self, function_name: str, args: List[Any]) -> Any:
        """Execute contract function"""
        try:
            # Create a safe execution environment
            exec_globals = {
                'state': self.state,
                'balance': self.balance,
                'utils': Utils,
            }
            
            # Add function definitions
            exec(self.code, exec_globals)
            
            # Call function
            if function_name in exec_globals:
                func = exec_globals[function_name]
                result = func(*args)
                
                # Update state if modified
                if 'state' in exec_globals:
                    self.state = exec_globals['state']
                
                return result
            else:
                raise ValueError(f"Function {function_name} not found")
        
        except Exception as e:
            return f"Error: {str(e)}"

    def get_state(self) -> Dict:
        """Get contract state"""
        return self.state.copy()

    def set_state(self, key: str, value: Any):
        """Set contract state"""
        self.state[key] = value

    def transfer_funds(self, amount: float) -> bool:
        """Transfer funds to contract"""
        if amount < 0:
            return False
        
        self.balance += amount
        return True

    def withdraw_funds(self, amount: float) -> bool:
        """Withdraw funds from contract"""
        if amount < 0 or amount > self.balance:
            return False
        
        self.balance -= amount
        return True

    def is_valid(self) -> bool:
        """Validate contract"""
        if not self.contract_address:
            return False
        
        if not Utils.validate_address(self.contract_address):
            return False
        
        if not Utils.validate_address(self.creator_address):
            return False
        
        if not self.code:
            return False
        
        return True

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'contract_address': self.contract_address,
            'creator_address': self.creator_address,
            'code': self.code,
            'abi': self.abi,
            'state': self.state,
            'created_at': self.created_at,
            'balance': self.balance,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), default=str)

    @staticmethod
    def from_dict(contract_dict: Dict) -> 'SmartContract':
        """Create contract from dictionary"""
        return SmartContract(contract_dict)

    @staticmethod
    def from_json(contract_json: str) -> 'SmartContract':
        """Create contract from JSON"""
        return SmartContract(json.loads(contract_json))


class SmartContractManager:
    """Manages all smart contracts in the blockchain"""

    def __init__(self):
        """Initialize smart contract manager"""
        self.contracts = {}  # contract_address -> SmartContract

    def deploy_contract(self, creator_address: str, code: str, abi: List = None) -> Optional[str]:
        """Deploy new smart contract"""
        if not creator_address or not code:
            return None
        
        if not Utils.validate_address(creator_address):
            return None
        
        # Check code size
        if len(code) > config.MAX_CONTRACT_SIZE:
            return None
        
        # Validate code syntax
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            print(f"Contract code syntax error: {e}")
            return None
        
        contract = SmartContract()
        contract.creator_address = creator_address
        contract.code = code
        contract.abi = abi or []
        
        # Generate contract address
        contract_address = contract.generate_address()
        
        # Store contract
        self.contracts[contract_address] = contract
        
        return contract_address

    def get_contract(self, contract_address: str) -> Optional[SmartContract]:
        """Get contract by address"""
        return self.contracts.get(contract_address)

    def contract_exists(self, contract_address: str) -> bool:
        """Check if contract exists"""
        return contract_address in self.contracts

    def call_contract(self, contract_address: str, function_name: str, args: List[Any]) -> Any:
        """Call contract function"""
        contract = self.get_contract(contract_address)
        if not contract:
            return None
        
        return contract.execute_function(function_name, args)

    def get_contract_state(self, contract_address: str) -> Optional[Dict]:
        """Get contract state"""
        contract = self.get_contract(contract_address)
        if not contract:
            return None
        
        return contract.get_state()

    def update_contract_state(self, contract_address: str, key: str, value: Any) -> bool:
        """Update contract state"""
        contract = self.get_contract(contract_address)
        if not contract:
            return False
        
        contract.set_state(key, value)
        return True

    def list_contracts(self) -> List[str]:
        """Get list of all contract addresses"""
        return list(self.contracts.keys())

    def get_contract_info(self, contract_address: str) -> Optional[Dict]:
        """Get contract information"""
        contract = self.get_contract(contract_address)
        if not contract:
            return None
        
        return {
            'contract_address': contract.contract_address,
            'creator_address': contract.creator_address,
            'created_at': contract.created_at,
            'balance': contract.balance,
            'state': contract.state,
        }
