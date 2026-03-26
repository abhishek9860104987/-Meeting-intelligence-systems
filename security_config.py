import os
import json
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_key: str
    api_key_encrypted: str
    database_encryption: bool = True
    audit_logging: bool = True
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    password_min_length: int = 12
    require_mfa: bool = True
    data_retention_days: int = 2555
    backup_encryption: bool = True

class SecureConfigManager:
    """Secure configuration management with encryption and environment variables"""
    
    def __init__(self, config_file: str = "security_config.json"):
        self.config_file = config_file
        self.config = None
        self.fernet = None
        
        # Initialize security
        self._initialize_security()
        
    def _initialize_security(self):
        """Initialize security configuration"""
        
        # Load or create encryption key
        key_file = "encryption.key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set file permissions (read/write for owner only)
            os.chmod(key_file, 0o600)
        
        self.fernet = Fernet(key)
        
        # Load configuration
        self._load_config()
        
        # Validate security settings
        self._validate_security()
    
    def _load_config(self):
        """Load configuration from file or environment"""
        
        # Try to load from file first
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                encrypted_data = f.read()
                
            try:
                decrypted_data = self.fernet.decrypt(encrypted_data.encode()).decode()
                config_data = json.loads(decrypted_data)
            except Exception:
                # File corrupted, create new config
                config_data = {}
        else:
            config_data = {}
        
        # Override with environment variables if available
        env_config = self._load_from_environment()
        
        # Merge configurations
        merged_config = {**config_data, **env_config}
        
        # Create SecurityConfig object
        self.config = SecurityConfig(
            encryption_key=os.environ.get('ENCRYPTION_KEY', merged_config.get('encryption_key', '')),
            api_key_encrypted=self._encrypt_api_key(),
            database_encryption=merged_config.get('database_encryption', True),
            audit_logging=merged_config.get('audit_logging', True),
            session_timeout_minutes=merged_config.get('session_timeout_minutes', 30),
            max_login_attempts=merged_config.get('max_login_attempts', 5),
            password_min_length=merged_config.get('password_min_length', 12),
            require_mfa=merged_config.get('require_mfa', True),
            data_retention_days=merged_config.get('data_retention_days', 2555),
            backup_encryption=merged_config.get('backup_encryption', True)
        )
        
        # Save updated configuration
        self._save_config()
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        
        config = {}
        
        # API Keys
        if 'GROQ_API_KEY' in os.environ:
            config['api_key'] = os.environ['GROQ_API_KEY']
        
        # Database settings
        if 'DB_ENCRYPTION' in os.environ:
            config['database_encryption'] = os.environ['DB_ENCRYPTION'].lower() == 'true'
        
        # Security settings
        if 'SESSION_TIMEOUT' in os.environ:
            config['session_timeout_minutes'] = int(os.environ['SESSION_TIMEOUT'])
        
        if 'MAX_LOGIN_ATTEMPTS' in os.environ:
            config['max_login_attempts'] = int(os.environ['MAX_LOGIN_ATTEMPTS'])
        
        if 'REQUIRE_MFA' in os.environ:
            config['require_mfa'] = os.environ['REQUIRE_MFA'].lower() == 'true'
        
        if 'DATA_RETENTION_DAYS' in os.environ:
            config['data_retention_days'] = int(os.environ['DATA_RETENTION_DAYS'])
        
        return config
    
    def _encrypt_api_key(self) -> str:
        """Encrypt API key for secure storage"""
        
        api_key = os.environ.get('GROQ_API_KEY')
        
        if not api_key:
            # Try to get from existing config
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    encrypted_data = f.read()
                try:
                    decrypted_data = self.fernet.decrypt(encrypted_data.encode()).decode()
                    config_data = json.loads(decrypted_data)
                    api_key = config_data.get('api_key', '')
                except Exception:
                    api_key = ''
        
        if api_key:
            encrypted_key = self.fernet.encrypt(api_key.encode()).decode()
            return encrypted_key
        
        return ""
    
    def get_api_key(self) -> str:
        """Get decrypted API key"""
        
        if self.config and self.config.api_key_encrypted:
            try:
                return self.fernet.decrypt(self.config.api_key_encrypted.encode()).decode()
            except Exception:
                pass
        
        # Fallback to environment
        return os.environ.get('GROQ_API_KEY', '')
    
    def _save_config(self):
        """Save encrypted configuration to file"""
        
        if not self.config:
            return
        
        config_data = {
            'encryption_key': self.config.encryption_key,
            'api_key': self.get_api_key(),  # Will be encrypted below
            'database_encryption': self.config.database_encryption,
            'audit_logging': self.config.audit_logging,
            'session_timeout_minutes': self.config.session_timeout_minutes,
            'max_login_attempts': self.config.max_login_attempts,
            'password_min_length': self.config.password_min_length,
            'require_mfa': self.config.require_mfa,
            'data_retention_days': self.config.data_retention_days,
            'backup_encryption': self.config.backup_encryption
        }
        
        # Encrypt and save
        json_data = json.dumps(config_data)
        encrypted_data = self.fernet.encrypt(json_data.encode()).decode()
        
        with open(self.config_file, 'w') as f:
            f.write(encrypted_data)
        
        # Set secure permissions
        os.chmod(self.config_file, 0o600)
    
    def _validate_security(self):
        """Validate security configuration"""
        
        if not self.config:
            raise ValueError("Security configuration not loaded")
        
        # Validate API key
        api_key = self.get_api_key()
        if not api_key:
            raise ValueError("API key not configured")
        
        # Validate session timeout
        if self.config.session_timeout_minutes < 5 or self.config.session_timeout_minutes > 480:
            raise ValueError("Session timeout must be between 5 and 480 minutes")
        
        # Validate password requirements
        if self.config.password_min_length < 8:
            raise ValueError("Password minimum length must be at least 8")
        
        # Validate data retention
        if self.config.data_retention_days < 365:
            raise ValueError("Data retention must be at least 365 days for compliance")
    
    def rotate_encryption_key(self):
        """Rotate encryption key and re-encrypt all data"""
        
        # Generate new key
        new_key = Fernet.generate_key()
        new_fernet = Fernet(new_key)
        
        # Load current config with old key
        old_config_data = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                encrypted_data = f.read()
            try:
                decrypted_data = self.fernet.decrypt(encrypted_data.encode()).decode()
                old_config_data = json.loads(decrypted_data)
            except Exception:
                pass
        
        # Re-encrypt with new key
        new_encrypted_data = new_fernet.encrypt(json.dumps(old_config_data).encode()).decode()
        
        # Save new key and config
        key_file = "encryption.key"
        with open(key_file, 'wb') as f:
            f.write(new_key)
        os.chmod(key_file, 0o600)
        
        with open(self.config_file, 'w') as f:
            f.write(new_encrypted_data)
        
        # Update fernet instance
        self.fernet = new_fernet
        
        # Reload config
        self._load_config()
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt"""
        
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        
        hashed = kdf.derive(password.encode())
        return base64.b64encode(hashed).decode(), salt
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        
        new_hash, _ = self.hash_password(password, salt)
        return new_hash == hashed
    
    def create_secure_session(self, user_id: str) -> Dict[str, Any]:
        """Create secure session with token"""
        
        session_token = self.generate_secure_token()
        session_data = {
            'user_id': user_id,
            'session_token': session_token,
            'created_at': os.time.time(),
            'expires_at': os.time.time() + (self.config.session_timeout_minutes * 60),
            'ip_address': '127.0.0.1',  # Would get from request
            'user_agent': 'Agent System'  # Would get from request
        }
        
        # Encrypt session data
        encrypted_session = self.fernet.encrypt(json.dumps(session_data).encode()).decode()
        
        return {
            'session_token': session_token,
            'encrypted_session': encrypted_session,
            'expires_at': session_data['expires_at']
        }
    
    def validate_session(self, session_token: str, encrypted_session: str) -> bool:
        """Validate session token"""
        
        try:
            # Decrypt session data
            session_data = json.loads(self.fernet.decrypt(encrypted_session.encode()).decode())
            
            # Check token
            if session_data.get('session_token') != session_token:
                return False
            
            # Check expiration
            if os.time.time() > session_data.get('expires_at', 0):
                return False
            
            return True
            
        except Exception:
            return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def get_security_audit_config(self) -> Dict[str, Any]:
        """Get security audit configuration"""
        
        return {
            'encryption_enabled': True,
            'api_key_encrypted': bool(self.config.api_key_encrypted),
            'database_encryption': self.config.database_encryption,
            'audit_logging': self.config.audit_logging,
            'session_timeout_minutes': self.config.session_timeout_minutes,
            'max_login_attempts': self.config.max_login_attempts,
            'password_min_length': self.config.password_min_length,
            'require_mfa': self.config.require_mfa,
            'data_retention_days': self.config.data_retention_days,
            'backup_encryption': self.config.backup_encryption,
            'config_file_permissions': oct(os.stat(self.config_file).st_mode)[-3:],
            'key_file_permissions': oct(os.stat("encryption.key").st_mode)[-3:] if os.path.exists("encryption.key") else "not_found"
        }

# Global security manager
security_manager = SecureConfigManager()
