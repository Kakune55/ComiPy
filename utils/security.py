import hashlib
import secrets
import hmac

from typing import Optional

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    哈希密码并返回哈希值和盐值
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 迭代次数
    )
    
    return password_hash.hex(), salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    验证密码是否正确
    """
    test_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(test_hash, hashed_password)

def generate_session_token() -> str:
    """
    生成安全的会话令牌
    """
    return secrets.token_urlsafe(32)
