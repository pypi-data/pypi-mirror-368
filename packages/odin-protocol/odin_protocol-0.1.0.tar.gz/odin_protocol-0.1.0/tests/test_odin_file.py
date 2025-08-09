"""Test ODIN file format operations."""

import pytest
from datetime import datetime, timezone

from odin_protocol import (
    create_odin_file,
    pack_odin,
    unpack_odin,
    sign_odin,
    verify_odin,
    encrypt_odin,
    decrypt_odin,
    OdinCapsule,
    OdinFile,
    MetaObject,
    StateObject,
    ValidationError,
    InvalidMagicError,
    ChecksumError,
)


class TestOdinFileOperations:
    """Test core ODIN file operations."""

    def test_create_odin_file(self):
        """Test creating a basic ODIN file."""
        odin_file = create_odin_file(
            content_type="text/plain",
            data="Hello, ODIN!",
            creator="test-user",
            description="Test file",
            tags=["test"],
        )
        
        assert isinstance(odin_file, OdinFile)
        assert odin_file.state.type == "text/plain"
        assert odin_file.state.data == "Hello, ODIN!"
        assert odin_file.meta.creator == "test-user"
        assert odin_file.meta.description == "Test file"
        assert odin_file.meta.tags == ["test"]
        assert odin_file.meta.schema_version == "1.0.0"

    def test_pack_unpack_roundtrip(self):
        """Test packing and unpacking ODIN files."""
        # Create test file
        original_file = create_odin_file(
            content_type="application/json",
            data={"message": "test", "number": 42, "nested": {"key": "value"}},
            creator="test-creator",
            description="Test JSON data",
            tags=["json", "test"],
        )
        
        # Pack to binary
        packed_data = pack_odin(original_file)
        assert isinstance(packed_data, bytes)
        assert len(packed_data) > 0
        assert packed_data.startswith(b"ODIN\x01")  # Check magic bytes
        
        # Unpack back to OdinFile
        unpacked_file = unpack_odin(packed_data)
        
        # Verify roundtrip integrity
        assert unpacked_file.state.type == original_file.state.type
        assert unpacked_file.state.data == original_file.state.data
        assert unpacked_file.meta.creator == original_file.meta.creator
        assert unpacked_file.meta.description == original_file.meta.description
        assert unpacked_file.meta.tags == original_file.meta.tags

    def test_pack_unpack_minimal(self):
        """Test packing/unpacking with minimal data."""
        # Create minimal file (only required fields)
        odin_file = OdinFile(
            meta=MetaObject(
                created=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            ),
            state=StateObject(
                type="text/plain",
                data="minimal"
            )
        )
        
        # Pack and unpack
        packed = pack_odin(odin_file)
        unpacked = unpack_odin(packed)
        
        assert unpacked.state.type == "text/plain"
        assert unpacked.state.data == "minimal"
        assert unpacked.meta.schema_version == "1.0.0"

    def test_invalid_magic_bytes(self):
        """Test handling invalid magic bytes."""
        with pytest.raises(InvalidMagicError):
            unpack_odin(b"INVALID_MAGIC_BYTES")

    def test_corrupted_checksum(self):
        """Test handling corrupted checksum."""
        # Create valid file
        odin_file = create_odin_file("text/plain", "test")
        packed = pack_odin(odin_file)
        
        # Corrupt the last byte (checksum)
        corrupted = packed[:-1] + b'\x00'
        
        with pytest.raises(ChecksumError):
            unpack_odin(corrupted)

    def test_file_too_short(self):
        """Test handling files that are too short."""
        with pytest.raises(ValidationError, match="File too short"):
            unpack_odin(b"ODIN\x01abc")  # Less than minimum size

    def test_large_data_structures(self):
        """Test handling large but valid data structures."""
        # Create file with large data
        large_data = {
            "items": [{"id": i, "value": f"item_{i}"} for i in range(1000)],
            "metadata": {"total": 1000, "type": "test_data"}
        }
        
        odin_file = create_odin_file(
            content_type="application/json",
            data=large_data,
            description="Large test dataset"
        )
        
        # Pack and unpack
        packed = pack_odin(odin_file)
        unpacked = unpack_odin(packed)
        
        assert len(unpacked.state.data["items"]) == 1000
        assert unpacked.state.data["metadata"]["total"] == 1000

    def test_unicode_data(self):
        """Test handling Unicode data."""
        unicode_data = {
            "text": "Hello 世界! 🌍 Здравствуй мир!",
            "emoji": "🚀🔥💫⭐",
            "special": "Special chars: ñáéíóú àèìòù äëïöü"
        }
        
        odin_file = create_odin_file(
            content_type="text/unicode",
            data=unicode_data,
            description="Unicode test data"
        )
        
        # Pack and unpack
        packed = pack_odin(odin_file)
        unpacked = unpack_odin(packed)
        
        assert unpacked.state.data == unicode_data

    def test_binary_data(self):
        """Test handling binary data."""
        binary_data = b'\x00\x01\x02\x03\xff\xfe\xfd\xfc'
        
        odin_file = create_odin_file(
            content_type="application/octet-stream",
            data=binary_data,
            description="Binary test data"
        )
        
        # Pack and unpack
        packed = pack_odin(odin_file)
        unpacked = unpack_odin(packed)
        
        assert unpacked.state.data == binary_data

    def test_nested_data_structures(self):
        """Test handling deeply nested data structures."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "data": "deep nested value",
                            "array": [1, 2, {"nested_in_array": True}]
                        }
                    }
                }
            }
        }
        
        odin_file = create_odin_file(
            content_type="application/json",
            data=nested_data,
            description="Nested structure test"
        )
        
        packed = pack_odin(odin_file)
        unpacked = unpack_odin(packed)
        
        assert unpacked.state.data["level1"]["level2"]["level3"]["level4"]["data"] == "deep nested value"
        assert unpacked.state.data["level1"]["level2"]["level3"]["level4"]["array"][2]["nested_in_array"] is True


@pytest.mark.skipif(True, reason="Crypto tests require dependencies")
class TestCryptographicOperations:
    """Test cryptographic operations (signing and encryption)."""

    def test_ed25519_signing(self):
        """Test Ed25519 signing and verification."""
        from cryptography.hazmat.primitives.asymmetric import ed25519
        
        # Generate key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Create and pack ODIN file
        odin_file = create_odin_file("text/plain", "test message")
        packed_data = pack_odin(odin_file)
        
        # Sign the data
        sig_obj = sign_odin(packed_data, private_key)
        
        assert sig_obj.algorithm == "ed25519"
        assert len(sig_obj.public_key) == 32  # Ed25519 public key size
        assert len(sig_obj.signature) == 64   # Ed25519 signature size
        
        # Verify signature
        is_valid = verify_odin(packed_data, sig_obj)
        assert is_valid is True

    def test_encryption_decryption(self):
        """Test file encryption and decryption."""
        # Create test file
        odin_file = create_odin_file(
            content_type="application/json",
            data={"secret": "confidential data", "public": "public data"}
        )
        
        # Encrypt specific fields
        encryption_key = b'0' * 32  # 32-byte key
        encrypted_file, enc_obj = encrypt_odin(
            odin_file,
            encryption_key,
            ["state.data.secret"]
        )
        
        assert enc_obj.algorithm == "chacha20-poly1305"
        assert "state.data.secret" in enc_obj.encrypted_fields
        
        # Decrypt file
        decrypted_file = decrypt_odin(encrypted_file, encryption_key)
        
        # Verify decryption
        assert decrypted_file.state.data["secret"] == "confidential data"
        assert decrypted_file.state.data["public"] == "public data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
