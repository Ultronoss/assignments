import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os

class EncryptionManager:
    def __init__(self):
        self.backend = default_backend()
    
    def generate_key_from_password(self, password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """Generate a key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(password.encode())
        return key, salt
    
    def encrypt_data(self, data: bytes, key: bytes, iv: bytes = None) -> tuple[bytes, bytes]:
        """Encrypt data using AES-256-CBC"""
        if iv is None:
            iv = os.urandom(16)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # Pad data to be multiple of 16 bytes
        padded_data = self._pad_data(data)
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data, iv
    
    def decrypt_data(self, encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-256-CBC"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return self._unpad_data(decrypted_data)
    
    def _pad_data(self, data: bytes) -> bytes:
        """Pad data to be multiple of 16 bytes using PKCS7"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        padding_length = data[-1]
        return data[:-padding_length]
    
    def hash_key(self, key: bytes) -> str:
        """Create a hash of the encryption key for storage"""
        return hashlib.sha256(key).hexdigest()
    
    def encode_base64(self, data: bytes) -> str:
        """Encode bytes to base64 string"""
        return base64.b64encode(data).decode('utf-8')
    
    def decode_base64(self, data: str) -> bytes:
        """Decode base64 string to bytes"""
        return base64.b64decode(data.encode('utf-8'))

# Global encryption manager instance
encryption_manager = EncryptionManager() 