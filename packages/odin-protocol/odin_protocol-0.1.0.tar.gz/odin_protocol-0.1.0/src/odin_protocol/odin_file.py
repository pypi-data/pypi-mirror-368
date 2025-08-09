"""ODIN file format implementation."""

import hashlib
import struct
import zlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

import crc32c
import msgpack
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from pydantic import BaseModel, Field, field_validator

from .errors import (
    ChecksumError,
    CompressionError,
    CryptoError,
    EncryptionError,
    FileTooLargeError,
    InvalidMagicError,
    SignatureError,
    ValidationError,
)

# Constants from spec
MAGIC_BYTES = b"ODIN\x01"
DEFAULT_SIZE_LIMIT = 8 * 1024 * 1024  # 8MB
HARD_SIZE_LIMIT = 32 * 1024 * 1024    # 32MB
COMPRESSION_LEVEL = 6


class MetaObject(BaseModel):
    """Metadata object schema."""
    # Store internally as schema_version, expose as "schema" (tests expect .schema)
    schema_version: str = Field(default="1.0.0", alias="schema", description="Schema version")
    created: str = Field(description="ISO 8601 UTC timestamp")
    creator: Optional[str] = Field(default=None, description="Creator identifier")
    description: Optional[str] = Field(default=None, description="Human description")
    tags: Optional[List[str]] = Field(default=None, description="Tag array")
    fingerprint: Optional[str] = Field(default=None, description="Content hash")
    chain: Optional[str] = Field(default=None, description=".odin.chain filename")

    # Allow "schema" key and attribute access
    @property
    def schema(self) -> str:
        return self.schema_version

    model_config = {
        "populate_by_name": True,        # lets us accept schema=... and access by field name
        "protected_namespaces": (),      # silence "schema" shadow warning
        "from_attributes": True,
    }

    # ---- Pydantic v2 style validators ----
    @field_validator("created")
    @classmethod
    def validate_created(cls, v: str) -> str:
        """Validate ISO 8601 timestamp."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("created must be valid ISO 8601 timestamp")


class StateObject(BaseModel):
    """State object schema."""
    type: str = Field(description="Content type identifier")
    version: Optional[str] = Field(default=None, description="Content version")
    data: Any = Field(description="Primary payload")


class SignatureObject(BaseModel):
    """Signature object schema."""
    algorithm: str = Field(description="Signature algorithm")
    public_key: bytes = Field(description="Public key bytes")
    signature: bytes = Field(description="Signature bytes")

    @field_validator('algorithm')
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate signature algorithm."""
        if v not in ('ed25519', 'rsa-pss'):
            raise ValueError("algorithm must be 'ed25519' or 'rsa-pss'")
        return v


class EncryptionObject(BaseModel):
    """Encryption object schema."""
    algorithm: str = Field(description="Encryption algorithm")
    nonce: bytes = Field(description="Encryption nonce")
    encrypted_fields: List[str] = Field(description="Encrypted field paths")

    @field_validator('algorithm')
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate encryption algorithm."""
        if v not in ('xchacha20-poly1305', 'chacha20-poly1305'):
            raise ValueError("algorithm must be 'xchacha20-poly1305' or 'chacha20-poly1305'")
        return v


class OdinFile(BaseModel):
    """Top-level ODIN file structure."""
    meta: MetaObject = Field(description="File metadata")
    state: StateObject = Field(description="Primary content")
    sig: Optional[SignatureObject] = Field(default=None, description="Digital signature")
    enc: Optional[EncryptionObject] = Field(default=None, description="Encryption metadata")


def _deterministic_msgpack_encode(obj: Any) -> bytes:
    """Encode object to deterministic msgpack."""
    def default(obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            # Convert Pydantic models to dict with sorted keys, using aliases
            return _sort_dict(obj.model_dump(exclude_unset=True, by_alias=True))
        elif isinstance(obj, dict):
            return _sort_dict(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def _sort_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sort dictionary keys."""
        result = {}
        for key in sorted(d.keys()):
            value = d[key]
            if isinstance(value, dict):
                result[key] = _sort_dict(value)
            elif isinstance(value, list):
                result[key] = [_sort_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result

    return msgpack.packb(obj, default=default, use_bin_type=True, strict_types=True)


def _deterministic_msgpack_decode(data: bytes) -> Any:
    """Decode msgpack data."""
    return msgpack.unpackb(data, raw=False, strict_map_key=False)


def _compress_data(data: bytes) -> bytes:
    """Compress data using zlib."""
    try:
        return zlib.compress(data, level=COMPRESSION_LEVEL)
    except Exception as e:
        raise CompressionError(f"Failed to compress data: {e}")


def _decompress_data(data: bytes) -> bytes:
    """Decompress zlib data."""
    try:
        return zlib.decompress(data)
    except Exception as e:
        raise CompressionError(f"Failed to decompress data: {e}")


def _calculate_crc32c(data: bytes) -> int:
    """Calculate CRC32C checksum."""
    return crc32c.crc32c(data)


def _generate_fingerprint(content: bytes) -> str:
    """Generate content fingerprint using SHA-256."""
    return hashlib.sha256(content).hexdigest()


def pack_odin(
    odin_data: Union[OdinFile, Dict[str, Any]],
    size_limit: int = DEFAULT_SIZE_LIMIT
) -> bytes:
    """
    Pack ODIN data into binary format.
    
    Args:
        odin_data: ODIN file data as OdinFile instance or dict
        size_limit: Maximum uncompressed size in bytes
        
    Returns:
        Binary ODIN file data
        
    Raises:
        FileTooLargeError: If data exceeds size limit
        ValidationError: If data validation fails
        CompressionError: If compression fails
    """
    # Convert to OdinFile if needed
    if isinstance(odin_data, dict):
        odin_file = OdinFile(**odin_data)
    else:
        odin_file = odin_data

    # Serialize to msgpack
    payload_data = _deterministic_msgpack_encode(odin_file)
    
    # Check size limits
    if len(payload_data) > HARD_SIZE_LIMIT:
        raise FileTooLargeError(len(payload_data), HARD_SIZE_LIMIT)
    if len(payload_data) > size_limit:
        raise FileTooLargeError(len(payload_data), size_limit)

    # Compress payload
    compressed_payload = _compress_data(payload_data)
    
    # Build header: Magic(5) + Length(4) + CompressedPayload(N)
    header = MAGIC_BYTES + struct.pack('<I', len(compressed_payload))
    
    # Calculate CRC32C checksum of header + compressed payload
    content_for_checksum = header + compressed_payload
    checksum = _calculate_crc32c(content_for_checksum)
    
    # Final file: Header + CompressedPayload + CRC32C(4)
    return content_for_checksum + struct.pack('<I', checksum)


def unpack_odin(data: bytes) -> OdinFile:
    """
    Unpack binary ODIN file data.
    
    Args:
        data: Binary ODIN file data
        
    Returns:
        OdinFile instance
        
    Raises:
        InvalidMagicError: If magic bytes are invalid
        ChecksumError: If checksum verification fails
        CompressionError: If decompression fails
        ValidationError: If data validation fails
    """
    if len(data) < 13:  # Magic(5) + Length(4) + CRC32C(4)
        raise ValidationError("File too short")

    # Extract magic bytes
    magic = data[:5]
    if magic != MAGIC_BYTES:
        raise InvalidMagicError(f"Invalid magic bytes: {magic!r}")

    # Extract length
    length = struct.unpack('<I', data[5:9])[0]
    
    # Check if we have enough data
    expected_size = 9 + length + 4  # Header + Payload + CRC32C
    if len(data) != expected_size:
        raise ValidationError(f"File size mismatch: got {len(data)}, expected {expected_size}")

    # Extract compressed payload and checksum
    compressed_payload = data[9:9 + length]
    stored_checksum = struct.unpack('<I', data[9 + length:9 + length + 4])[0]

    # Verify checksum
    content_for_checksum = data[:9 + length]  # Magic + Length + CompressedPayload
    calculated_checksum = _calculate_crc32c(content_for_checksum)
    if stored_checksum != calculated_checksum:
        raise ChecksumError(f"Checksum mismatch: stored {stored_checksum:08x}, calculated {calculated_checksum:08x}")

    # Decompress payload
    payload_data = _decompress_data(compressed_payload)

    # Check decompressed size limits
    if len(payload_data) > HARD_SIZE_LIMIT:
        raise FileTooLargeError(len(payload_data), HARD_SIZE_LIMIT)

    # Decode msgpack
    try:
        payload_dict = _deterministic_msgpack_decode(payload_data)
    except Exception as e:
        raise ValidationError(f"Failed to decode msgpack: {e}")

    # Validate and create OdinFile
    try:
        return OdinFile(**payload_dict)
    except Exception as e:
        raise ValidationError(f"Failed to validate ODIN structure: {e}")


def sign_odin(
    data: bytes,
    private_key: Union[ed25519.Ed25519PrivateKey, RSAPrivateKey],
    algorithm: Optional[str] = None
) -> SignatureObject:
    """
    Sign ODIN file data.
    
    Args:
        data: Raw file data (magic + length + compressed payload)
        private_key: Ed25519 or RSA private key
        algorithm: Signature algorithm ('ed25519' or 'rsa-pss'), auto-detected if None
        
    Returns:
        SignatureObject with signature
        
    Raises:
        CryptoError: If signing fails
    """
    try:
        if isinstance(private_key, ed25519.Ed25519PrivateKey):
            if algorithm and algorithm != 'ed25519':
                raise CryptoError(f"Algorithm mismatch: got {algorithm}, expected ed25519")
            
            signature = private_key.sign(data)
            public_key_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            return SignatureObject(
                algorithm='ed25519',
                public_key=public_key_bytes,
                signature=signature
            )
            
        elif isinstance(private_key, RSAPrivateKey):
            if algorithm and algorithm != 'rsa-pss':
                raise CryptoError(f"Algorithm mismatch: got {algorithm}, expected rsa-pss")
            
            from cryptography.hazmat.primitives.asymmetric import padding
            
            signature = private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            public_key_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return SignatureObject(
                algorithm='rsa-pss',
                public_key=public_key_bytes,
                signature=signature
            )
        else:
            raise CryptoError(f"Unsupported key type: {type(private_key)}")
            
    except Exception as e:
        if isinstance(e, CryptoError):
            raise
        raise CryptoError(f"Signing failed: {e}")


def verify_odin(data: bytes, sig_obj: SignatureObject) -> bool:
    """
    Verify ODIN file signature.
    
    Args:
        data: Raw file data (magic + length + compressed payload)
        sig_obj: SignatureObject with signature details
        
    Returns:
        True if signature is valid
        
    Raises:
        SignatureError: If verification fails
    """
    try:
        if sig_obj.algorithm == 'ed25519':
            if len(sig_obj.public_key) != 32:
                raise SignatureError("Invalid Ed25519 public key length")
            
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(sig_obj.public_key)
            public_key.verify(sig_obj.signature, data)
            return True
            
        elif sig_obj.algorithm == 'rsa-pss':
            public_key = serialization.load_pem_public_key(sig_obj.public_key)
            if not isinstance(public_key, RSAPublicKey):
                raise SignatureError("Invalid RSA public key")
                
            from cryptography.hazmat.primitives.asymmetric import padding
            
            public_key.verify(
                sig_obj.signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        else:
            raise SignatureError(f"Unsupported signature algorithm: {sig_obj.algorithm}")
            
    except Exception as e:
        if isinstance(e, SignatureError):
            raise
        raise SignatureError(f"Signature verification failed: {e}")


def encrypt_odin(
    odin_file: OdinFile,
    key: bytes,
    field_paths: List[str],
    algorithm: str = 'xchacha20-poly1305'
) -> Tuple[OdinFile, EncryptionObject]:
    """
    Encrypt specified fields in ODIN file.
    
    Args:
        odin_file: ODIN file to encrypt
        key: 32-byte encryption key
        field_paths: List of field paths to encrypt (e.g., ['state.data.secret'])
        algorithm: Encryption algorithm ('xchacha20-poly1305' default, 'chacha20-poly1305' fallback)
        
    Returns:
        Tuple of (encrypted_odin_file, encryption_object)
        
    Raises:
        EncryptionError: If encryption fails
    """
    try:
        if algorithm == 'xchacha20-poly1305':
            # Use PyNaCl for XChaCha20-Poly1305 (preferred)
            from nacl.secret import SecretBox
            import nacl.utils
            
            cipher = SecretBox(key)
            nonce = nacl.utils.random(SecretBox.NONCE_SIZE)  # 24 bytes for XChaCha20
            
        elif algorithm == 'chacha20-poly1305':
            # Fallback to standard ChaCha20-Poly1305
            cipher = ChaCha20Poly1305(key)
            nonce = cipher.generate_nonce(12)  # 12 bytes for ChaCha20Poly1305
        else:
            raise EncryptionError(f"Unsupported encryption algorithm: {algorithm}")

        # Create a copy of the file data
        file_dict = odin_file.model_dump(by_alias=True)
        
        # Encrypt specified fields
        for field_path in field_paths:
            _encrypt_field_at_path(file_dict, field_path, cipher, nonce, algorithm)

        # Create encryption object
        enc_obj = EncryptionObject(
            algorithm=algorithm,
            nonce=nonce,
            encrypted_fields=field_paths
        )

        # Create new ODIN file with encrypted data
        encrypted_file = OdinFile(**file_dict)
        encrypted_file.enc = enc_obj

        return encrypted_file, enc_obj

    except Exception as e:
        if isinstance(e, EncryptionError):
            raise
        raise EncryptionError(f"Encryption failed: {e}")


def decrypt_odin(
    encrypted_file: OdinFile,
    key: bytes
) -> OdinFile:
    """
    Decrypt ODIN file.
    
    Args:
        encrypted_file: Encrypted ODIN file
        key: 32-byte decryption key
        
    Returns:
        Decrypted ODIN file
        
    Raises:
        EncryptionError: If decryption fails
    """
    if not encrypted_file.enc:
        return encrypted_file  # Not encrypted

    try:
        enc_obj = encrypted_file.enc
        
        if enc_obj.algorithm == 'xchacha20-poly1305':
            # Use PyNaCl for XChaCha20-Poly1305 
            from nacl.secret import SecretBox
            cipher = SecretBox(key)
        elif enc_obj.algorithm == 'chacha20-poly1305':
            # Standard ChaCha20-Poly1305
            cipher = ChaCha20Poly1305(key)
        else:
            raise EncryptionError(f"Unsupported encryption algorithm: {enc_obj.algorithm}")

        # Create a copy of the file data
        file_dict = encrypted_file.model_dump(by_alias=True)
        
        # Remove encryption metadata
        del file_dict['enc']

        # Decrypt specified fields
        for field_path in enc_obj.encrypted_fields:
            _decrypt_field_at_path(file_dict, field_path, cipher, enc_obj.nonce, enc_obj.algorithm)

        # Create decrypted ODIN file
        return OdinFile(**file_dict)

    except Exception as e:
        if isinstance(e, EncryptionError):
            raise
        raise EncryptionError(f"Decryption failed: {e}")


def _encrypt_field_at_path(data: Dict[str, Any], path: str, cipher: Any, nonce: bytes, algorithm: str) -> None:
    """Encrypt field at specified path."""
    parts = path.split('.')
    current = data
    
    # Navigate to parent
    for part in parts[:-1]:
        if part not in current:
            return  # Path doesn't exist
        current = current[part]
    
    # Encrypt the final field
    field_name = parts[-1]
    if field_name in current:
        field_data = _deterministic_msgpack_encode(current[field_name])
        
        if algorithm == 'xchacha20-poly1305':
            # PyNaCl SecretBox
            encrypted = cipher.encrypt(field_data, nonce)
        else:
            # cryptography ChaCha20Poly1305
            encrypted = cipher.encrypt(nonce, field_data, None)
            
        current[field_name] = encrypted


def _decrypt_field_at_path(data: Dict[str, Any], path: str, cipher: Any, nonce: bytes, algorithm: str) -> None:
    """Decrypt field at specified path."""
    parts = path.split('.')
    current = data
    
    # Navigate to parent
    for part in parts[:-1]:
        if part not in current:
            return  # Path doesn't exist
        current = current[part]
    
    # Decrypt the final field
    field_name = parts[-1]
    if field_name in current and isinstance(current[field_name], bytes):
        if algorithm == 'xchacha20-poly1305':
            # PyNaCl SecretBox - nonce is included in ciphertext
            decrypted = cipher.decrypt(current[field_name])
        else:
            # cryptography ChaCha20Poly1305
            decrypted = cipher.decrypt(nonce, current[field_name], None)
            
        current[field_name] = _deterministic_msgpack_decode(decrypted)


def write_chain(odin_files: List[bytes], output_stream) -> None:
    """
    Write ODIN files to a chain stream as base64-encoded entries.
    
    Args:
        odin_files: List of packed ODIN file bytes
        output_stream: File-like object to write to
        
    Raises:
        ValidationError: If writing fails
    """
    import base64
    
    try:
        for odin_data in odin_files:
            # Encode as base64url and write one per line
            encoded = base64.urlsafe_b64encode(odin_data).decode('ascii')
            line = encoded + '\n'
            
            # Handle both text and binary streams
            if hasattr(output_stream, 'mode') and 'b' in output_stream.mode:
                output_stream.write(line.encode('utf-8'))
            elif hasattr(output_stream, 'write') and hasattr(output_stream, 'read'):
                # BytesIO or similar
                try:
                    output_stream.write(line.encode('utf-8'))
                except TypeError:
                    output_stream.write(line)
            else:
                output_stream.write(line)
            
    except Exception as e:
        raise ValidationError(f"Failed to write chain: {e}")


def open_chain(chain_stream) -> List[OdinFile]:
    """
    Open and parse a .odin.chain file or stream.
    
    Args:
        chain_stream: File path, file-like object, or stream containing base64-encoded ODIN files
        
    Returns:
        List of parsed OdinFile objects
        
    Raises:
        ValidationError: If chain file is invalid
    """
    import base64
    
    try:
        # Handle different input types
        if isinstance(chain_stream, str):
            # File path
            with open(chain_stream, 'r') as f:
                lines = f.readlines()
        else:
            # File-like object or stream
            # For BytesIO, we need to read and decode
            if hasattr(chain_stream, 'getvalue'):
                # BytesIO
                content = chain_stream.getvalue()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                lines = content.splitlines()
            else:
                # Regular file-like object
                lines = chain_stream.readlines()
                # Handle bytes if necessary
                if lines and isinstance(lines[0], bytes):
                    lines = [line.decode('utf-8') for line in lines]
        
        odin_files = []
        
        for line in lines:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
                
            line = line.strip()
            if not line:
                continue
                
            try:
                # Decode base64url to get ODIN binary data
                odin_data = base64.urlsafe_b64decode(line)
                
                # Unpack ODIN file
                odin_file = unpack_odin(odin_data)
                odin_files.append(odin_file)
                
            except Exception as e:
                raise ValidationError(f"Failed to decode chain entry: {e}")
        
        return odin_files
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Failed to open chain file: {e}")


# Alias for CLI compatibility
def read_chain(chain_stream) -> List[OdinFile]:
    """
    Alias for open_chain() for CLI compatibility.
    """
    return open_chain(chain_stream)


def create_odin_file(content_type: str, data, **kwargs) -> OdinFile:
    """
    Create ODIN file with simplified API.
    
    Args:
        content_type: MIME type of the data
        data: The actual data to store
        **kwargs: Additional metadata fields
        
    Returns:
        OdinFile instance
    """
    from datetime import datetime, timezone
    
    meta = MetaObject(
        created=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        **{k: v for k, v in kwargs.items() if k in ['creator', 'description', 'tags', 'fingerprint', 'chain']}
    )
    
    state = StateObject(
        type=content_type,
        data=data,
        version=kwargs.get('version')
    )
    
    return OdinFile(meta=meta, state=state)
