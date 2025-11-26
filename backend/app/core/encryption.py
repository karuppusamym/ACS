from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import os
from app.core.logging import get_logger

logger = get_logger(__name__)


class EncryptionService:
    """Service for encrypting/decrypting sensitive data like API keys"""

    def __init__(self):
        # Get encryption key from environment - REQUIRED
        key = settings.ENCRYPTION_KEY if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY else None

        if not key:
            error_msg = (
                "ENCRYPTION_KEY environment variable is required but not set. "
                "Generate a key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
                "and add it to your .env file."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        try:
            self.cipher = Fernet(key)
            logger.info("Encryption service initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize encryption service with provided key: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        if not plaintext:
            return ""
        
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string
        
        Args:
            ciphertext: Base64 encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""
        
        try:
            encrypted = base64.b64decode(ciphertext.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt: {str(e)}")
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()


# Global instance
encryption_service = EncryptionService()
