# wallet/mnemonic_handler.py - BIP39 Mnemonic Handler

from mnemonic import Mnemonic
from typing import List, Optional
import config

class MnemonicHandler:
    """Handles BIP39 mnemonic seed phrases"""

    def __init__(self, language: str = config.MNEMONIC_LANGUAGE):
        """Initialize mnemonic handler"""
        self.language = language
        self.mnemo = Mnemonic(language)

    def generate(self, strength: int = config.MNEMONIC_STRENGTH) -> str:
        """
        Generate a new mnemonic seed phrase
        
        Args:
            strength: Entropy strength in bits (128, 160, 192, 224, 256)
                     Results in 12, 15, 18, 21, 24 word phrases
        
        Returns:
            12-word mnemonic phrase as string
        """
        return self.mnemo.generate(strength=strength)

    def to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """
        Convert mnemonic to seed
        
        Args:
            mnemonic: The mnemonic phrase (space-separated words)
            passphrase: Optional passphrase for additional security
        
        Returns:
            64-byte seed
        
        Raises:
            ValueError: If mnemonic is invalid
        """
        if not self.check(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        
        return self.mnemo.to_seed(mnemonic, passphrase)

    def check(self, mnemonic: str) -> bool:
        """
        Validate mnemonic phrase
        
        Args:
            mnemonic: The mnemonic phrase to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            return self.mnemo.check(mnemonic)
        except Exception:
            return False

    def to_entropy(self, mnemonic: str) -> bytes:
        """
        Convert mnemonic to entropy
        
        Args:
            mnemonic: The mnemonic phrase
        
        Returns:
            Entropy bytes
        
        Raises:
            ValueError: If mnemonic is invalid
        """
        if not self.check(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        
        return self.mnemo.to_entropy(mnemonic)

    def from_entropy(self, entropy: bytes) -> str:
        """
        Generate mnemonic from entropy
        
        Args:
            entropy: Entropy bytes (16, 20, 24, 28, or 32 bytes)
        
        Returns:
            Mnemonic phrase
        
        Raises:
            ValueError: If entropy length is invalid
        """
        try:
            return self.mnemo.from_entropy(entropy)
        except Exception as e:
            raise ValueError(f"Invalid entropy: {e}")

    def get_word_list(self) -> List[str]:
        """
        Get BIP39 word list for this language
        
        Returns:
            List of 2048 valid BIP39 words
        """
        return self.mnemo.wordlist

    def validate_word(self, word: str) -> bool:
        """
        Check if a word is in the BIP39 wordlist
        
        Args:
            word: The word to validate
        
        Returns:
            True if word is valid, False otherwise
        """
        return word in self.mnemo.wordlist

    def get_word_index(self, word: str) -> Optional[int]:
        """
        Get the index of a word in the BIP39 wordlist
        
        Args:
            word: The word to find
        
        Returns:
            Index (0-2047) or None if not found
        """
        try:
            return self.mnemo.wordlist.index(word)
        except ValueError:
            return None

    def get_word_by_index(self, index: int) -> Optional[str]:
        """
        Get word by its index in the BIP39 wordlist
        
        Args:
            index: Index (0-2047)
        
        Returns:
            Word or None if index is invalid
        """
        if 0 <= index < len(self.mnemo.wordlist):
            return self.mnemo.wordlist[index]
        return None

    def mnemonic_to_words(self, mnemonic: str) -> List[str]:
        """
        Split mnemonic into individual words
        
        Args:
            mnemonic: The mnemonic phrase
        
        Returns:
            List of words
        """
        return mnemonic.split()

    def words_to_mnemonic(self, words: List[str]) -> str:
        """
        Join words into mnemonic phrase
        
        Args:
            words: List of words
        
        Returns:
            Mnemonic phrase
        """
        return " ".join(words)

    @staticmethod
    def get_supported_languages() -> List[str]:
        """
        Get list of supported languages
        
        Returns:
            List of language codes
        """
        return [
            'english', 'spanish', 'french', 'italian', 'portuguese',
            'czech', 'polish', 'russian', 'ukrainian', 'simplified_chinese',
            'traditional_chinese', 'japanese', 'korean'
        ]

    def estimate_entropy_strength(self, word_count: int) -> int:
        """
        Estimate entropy strength from word count
        
        Args:
            word_count: Number of words (12, 15, 18, 21, or 24)
        
        Returns:
            Entropy strength in bits (128, 160, 192, 224, or 256)
        
        Raises:
            ValueError: If word count is invalid
        """
        entropy_map = {
            12: 128,
            15: 160,
            18: 192,
            21: 224,
            24: 256
        }
        
        if word_count not in entropy_map:
            raise ValueError(f"Invalid word count. Must be 12, 15, 18, 21, or 24. Got {word_count}")
        
        return entropy_map[word_count]

    def estimate_word_count(self, entropy_strength: int) -> int:
        """
        Estimate word count from entropy strength
        
        Args:
            entropy_strength: Entropy in bits (128, 160, 192, 224, or 256)
        
        Returns:
            Expected number of words (12, 15, 18, 21, or 24)
        
        Raises:
            ValueError: If entropy strength is invalid
        """
        strength_map = {
            128: 12,
            160: 15,
            192: 18,
            224: 21,
            256: 24
        }
        
        if entropy_strength not in strength_map:
            raise ValueError(f"Invalid entropy strength. Must be 128, 160, 192, 224, or 256. Got {entropy_strength}")
        
        return strength_map[entropy_strength]
