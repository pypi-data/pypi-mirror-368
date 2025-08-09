"""ODIN protocol exception definitions."""

from typing import Optional


class OdinError(Exception):
    """Base exception for all ODIN protocol errors."""
    
    def __init__(self, message: str, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class AuthError(OdinError):
    """Authentication or authorization error."""
    pass


class RateLimitError(OdinError):
    """Rate limiting error."""
    
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        code: Optional[str] = None
    ) -> None:
        super().__init__(message, code)
        self.retry_after = retry_after


class NetworkError(OdinError):
    """Network connectivity or communication error."""
    pass


class ServerError(OdinError):
    """Server-side error."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        code: Optional[str] = None
    ) -> None:
        super().__init__(message, code)
        self.status_code = status_code


class ValidationError(OdinError):
    """Data validation error."""
    pass


class CompressionError(OdinError):
    """Compression or decompression error."""
    pass


class CryptoError(OdinError):
    """Cryptographic operation error."""
    pass


class RegistryError(OdinError):
    """Registry operation error."""
    pass


class FileTooLargeError(ValidationError):
    """File exceeds size limits."""
    
    def __init__(self, size: int, limit: int) -> None:
        super().__init__(f"File size {size} bytes exceeds limit of {limit} bytes")
        self.size = size
        self.limit = limit


class InvalidMagicError(ValidationError):
    """Invalid magic bytes in file header."""
    pass


class ChecksumError(ValidationError):
    """Checksum verification failed."""
    pass


class SignatureError(CryptoError):
    """Digital signature verification failed."""
    pass


class EncryptionError(CryptoError):
    """Encryption or decryption failed."""
    pass
