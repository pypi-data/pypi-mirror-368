"""
Agent-side encryption for GatherChat E2E encryption
Uses RSA-OAEP with SHA-256 for message encryption
"""

import base64
import os
from typing import Dict, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


class AgentCrypto:
    """
    Handles encryption/decryption for GatherChat agents
    """
    
    def __init__(self, private_key_pem: Optional[str] = None):
        """
        Initialize agent crypto with private key
        
        Args:
            private_key_pem: PEM-encoded private key string. If None, will generate new key pair.
        """
        if private_key_pem:
            self.private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )
        else:
            # Generate new key pair
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
        
        self.public_key = self.private_key.public_key()
        self.participant_keys: Dict[str, RSAPublicKey] = {}
    
    def export_public_key(self) -> str:
        """Export public key as base64-encoded DER format"""
        public_der = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(public_der).decode('utf-8')
    
    def export_private_key(self) -> str:
        """Export private key as PEM format for storage"""
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return private_pem.decode('utf-8')
    
    def import_participant_key(self, participant_name: str, public_key_base64: str):
        """
        Import a participant's public key
        
        Args:
            participant_name: Name of the participant
            public_key_base64: Base64-encoded DER public key
        """
        try:
            key_data = base64.b64decode(public_key_base64)
            public_key = serialization.load_der_public_key(key_data)
            self.participant_keys[participant_name] = public_key
            print(f"🔑 Imported public key for {participant_name}")
        except Exception as e:
            print(f"❌ Failed to import public key for {participant_name}: {e}")
            raise
    
    def encrypt_message_for(self, message: str, participant_name: str) -> str:
        """
        Encrypt message for a specific participant
        
        Args:
            message: Plaintext message
            participant_name: Name of the participant
            
        Returns:
            Base64-encoded encrypted message
        """
        if participant_name not in self.participant_keys:
            raise ValueError(f"No public key found for participant: {participant_name}")
        
        public_key = self.participant_keys[participant_name]
        
        try:
            encrypted = public_key.encrypt(
                message.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"❌ Failed to encrypt message for {participant_name}: {e}")
            raise
    
    def encrypt_for_participants(self, message: str, participant_names: list) -> Dict[str, str]:
        """
        Encrypt message for multiple participants
        
        Args:
            message: Plaintext message
            participant_names: List of participant names
            
        Returns:
            Dictionary mapping participant names to encrypted messages
        """
        encrypted = {}
        
        for participant_name in participant_names:
            try:
                encrypted[participant_name] = self.encrypt_message_for(message, participant_name)
            except Exception as e:
                print(f"❌ Failed to encrypt for {participant_name}: {e}")
                # Continue with other participants
        
        print(f"🔒 Encrypted message for {len(encrypted)} participants")
        return encrypted
    
    def decrypt_message(self, encrypted_message_base64: str) -> str:
        """
        Decrypt received message using agent's private key
        
        Args:
            encrypted_message_base64: Base64-encoded encrypted message
            
        Returns:
            Decrypted plaintext message
        """
        try:
            encrypted_data = base64.b64decode(encrypted_message_base64)
            
            decrypted = self.private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            message = decrypted.decode('utf-8')
            print("🔓 Decrypted message successfully")
            return message
        except Exception as e:
            print(f"❌ Failed to decrypt message: {e}")
            raise
    
    @classmethod
    def from_env(cls, env_var: str = "GATHERCHAT_AGENT_PRIVATE_KEY") -> "AgentCrypto":
        """
        Create AgentCrypto instance from environment variable
        
        Args:
            env_var: Environment variable name containing private key PEM
            
        Returns:
            AgentCrypto instance
        """
        private_key_pem = os.getenv(env_var)
        if not private_key_pem:
            print(f"⚠️ No private key found in {env_var}, generating new key pair")
            return cls()
        
        return cls(private_key_pem)
    
    def save_keys_to_env_format(self) -> str:
        """
        Generate environment variable format for storing keys
        
        Returns:
            String to add to .env file
        """
        private_key_pem = self.export_private_key()
        public_key_b64 = self.export_public_key()
        
        # Escape newlines for .env format
        private_key_env = private_key_pem.replace('\n', '\\n')
        
        return f"""
# Agent encryption keys
GATHERCHAT_AGENT_PRIVATE_KEY="{private_key_env}"
GATHERCHAT_AGENT_PUBLIC_KEY="{public_key_b64}"
"""