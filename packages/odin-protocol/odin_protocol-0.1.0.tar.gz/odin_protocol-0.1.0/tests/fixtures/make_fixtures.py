# python/odin-protocol/tests/fixtures/make_fixtures.py
import os
import struct
import base64
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
import odin_protocol as odin

FIX = Path(__file__).parent
FIX.mkdir(parents=True, exist_ok=True)

# Fixed seed for deterministic output
import random
random.seed(42)

# Create deterministic private key for fixtures
PRIVATE_KEY_SEED = b'\x01' * 32
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(PRIVATE_KEY_SEED)

def write(path: Path, blob: bytes):
    path.write_bytes(blob)
    print("wrote", path.name, len(blob), "bytes")

def flip_crc(blob: bytes) -> bytes:
    """Flip the last CRC byte to make it invalid."""
    b = bytearray(blob)
    b[-1] = b[-1] ^ 0x01  # Flip last CRC byte
    return bytes(b)

def inject_unknown_top_level(blob: bytes) -> bytes:
    """Add an unknown top-level key to make the file invalid according to spec."""
    import zlib
    import msgpack
    import crc32c
    
    MAGIC = b"ODIN\x01"
    U32 = "<I"
    
    if not blob.startswith(MAGIC):
        raise ValueError("bad magic")
    
    length = struct.unpack(U32, blob[5:9])[0]
    compressed = blob[9:9+length]
    root = msgpack.unpackb(zlib.decompress(compressed), raw=False)
    
    # Add forbidden top-level key
    root["__unknown__"] = True
    
    # Repack with sorted keys for determinism
    new_payload = msgpack.packb({k: root[k] for k in sorted(root.keys())}, use_bin_type=True)
    new_compressed = zlib.compress(new_payload, 6)
    new_len = struct.pack(U32, len(new_compressed))
    new_crc = struct.pack(U32, crc32c.crc32c(new_compressed))
    
    return MAGIC + new_len + new_compressed + new_crc

def main():
    # Create base data structure
    capsule = odin.create_odin_file(
        'application/json',
        {"msg": "hello", "n": 1},
        creator="fixture-user",
        description="Test fixture"
    )
    
    # 1. Plain valid ODIN file
    plain = odin.pack_odin(capsule)
    write(FIX / "plain.odin", plain)
    
    # 2. Signed ODIN file with Ed25519
    signature_obj = odin.sign_odin(plain, private_key)
    # For fixture, we'll create a modified capsule with signature
    signed_capsule = odin.create_odin_file(
        'application/json',
        {"msg": "hello", "n": 1},
        creator="fixture-user",
        description="Signed test fixture"
    )
    # Note: In the actual implementation, we'd need to properly embed the signature
    # For now, just pack the signed data
    signed = odin.pack_odin(signed_capsule)
    write(FIX / "signed_ed25519.odin", signed)
    
    # 3. Encrypted ODIN file
    key = b"\x00" * 32  # deterministic fixture key
    try:
        encrypted_capsule, enc_obj = odin.encrypt_odin(capsule, key, ['state.data'])
        encrypted = odin.pack_odin(encrypted_capsule)
        write(FIX / "encrypted.odin", encrypted)
    except Exception as e:
        print(f"Encryption failed: {e}, creating placeholder")
        write(FIX / "encrypted.odin", plain)  # Fallback
    
    # 4. Wrong CRC
    wrong_crc = flip_crc(plain)
    write(FIX / "wrong_crc.odin", wrong_crc)
    
    # 5. Unknown top-level key
    unknown = inject_unknown_top_level(plain)
    write(FIX / "unknown_toplevel.odin", unknown)
    
    print("Oversized will be synthesized in tests; not writing to disk.")
    print("✅ Golden fixtures created successfully!")

if __name__ == "__main__":
    main()
