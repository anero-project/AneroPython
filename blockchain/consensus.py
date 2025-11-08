# blockchain/consensus.py - Proof of Work Consensus

from blockchain.utils import Utils
import config

class ProofOfWork:
    """Monero-style Proof of Work consensus"""

    @staticmethod
    def verify_work(block_hash: str, difficulty: int) -> bool:
        """Verify that work meets difficulty requirement"""
        return Utils.check_hash_meets_difficulty(block_hash, difficulty)

    @staticmethod
    def calculate_difficulty_target(difficulty: int) -> str:
        """Calculate target from difficulty"""
        max_hash = 2 ** 256 - 1
        target = max_hash // difficulty
        return hex(target)[2:].zfill(64)

    @staticmethod
    def adjust_difficulty(previous_difficulty: int, time_taken: int, target_time: int) -> int:
        """Adjust difficulty based on mining time"""
        if time_taken == 0:
            return previous_difficulty
        
        adjustment_ratio = target_time / time_taken
        new_difficulty = int(previous_difficulty * adjustment_ratio)
        
        # Limit adjustment to prevent extreme changes
        max_change = previous_difficulty * 4
        min_change = previous_difficulty / 4
        
        return max(int(min_change), min(int(max_change), new_difficulty))

    @staticmethod
    def get_difficulty_for_block(blockchain_chain, block_height: int) -> int:
        """Get difficulty for next block"""
        if block_height < config.DIFFICULTY_ADJUSTMENT_INTERVAL:
            return config.INITIAL_DIFFICULTY
        
        # Adjust every N blocks
        if block_height % config.DIFFICULTY_ADJUSTMENT_INTERVAL == 0:
            old_block = blockchain_chain.get_block_by_height(
                block_height - config.DIFFICULTY_ADJUSTMENT_INTERVAL
            )
            current_block = blockchain_chain.get_block_by_height(block_height - 1)
            
            if old_block and current_block:
                time_span = current_block.timestamp - old_block.timestamp
                target_span = config.BLOCK_TIME * config.DIFFICULTY_ADJUSTMENT_INTERVAL
                
                return ProofOfWork.adjust_difficulty(
                    current_block.difficulty, time_span, target_span
                )
        
        # Otherwise keep same difficulty
        last_block = blockchain_chain.get_block_by_height(block_height - 1)
        return last_block.difficulty if last_block else config.INITIAL_DIFFICULTY
