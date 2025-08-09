# python/odin-protocol/tests/test_chain.py
from io import BytesIO
import odin_protocol as odin

def test_chain_roundtrip():
    """Test creating a chain, writing it, and reading it back."""
    # Create test metadata template
    meta_template = {
        'creator': 'test-user',
        'description': 'Chain test'
    }
    
    # Create 3 ODIN capsules with different data
    capsule1 = odin.create_odin_file('application/json', {"i": 1}, **meta_template)
    capsule2 = odin.create_odin_file('application/json', {"i": 2}, **meta_template)
    capsule3 = odin.create_odin_file('application/json', {"i": 3}, **meta_template)
    
    # Pack them to binary
    b1 = odin.pack_odin(capsule1)
    b2 = odin.pack_odin(capsule2)
    b3 = odin.pack_odin(capsule3)
    
    # Write chain to buffer
    buf = BytesIO()
    odin.write_chain([b1, b2, b3], buf)
    buf.seek(0)
    
    # Read chain back
    caps = odin.open_chain(buf)
    
    # Verify we got all 3 capsules back
    assert len(caps) == 3
    assert caps[0].state.data["i"] == 1
    assert caps[1].state.data["i"] == 2 
    assert caps[2].state.data["i"] == 3

def test_empty_chain():
    """Test handling of empty chain."""
    buf = BytesIO()
    odin.write_chain([], buf)
    buf.seek(0)
    
    caps = odin.open_chain(buf)
    assert len(caps) == 0

def test_single_item_chain():
    """Test chain with single item."""
    capsule = odin.create_odin_file('application/json', {"single": True})
    packed = odin.pack_odin(capsule)
    
    buf = BytesIO()
    odin.write_chain([packed], buf)
    buf.seek(0)
    
    caps = odin.open_chain(buf)
    assert len(caps) == 1
    assert caps[0].state.data["single"] is True

def test_chain_preserves_metadata():
    """Test that chain operations preserve all metadata."""
    capsule = odin.create_odin_file(
        'application/json', 
        {"test": "data"},
        creator="test-creator",
        description="Test capsule for chain"
    )
    packed = odin.pack_odin(capsule)
    
    buf = BytesIO()
    odin.write_chain([packed], buf)
    buf.seek(0)
    
    caps = odin.open_chain(buf)
    assert len(caps) == 1
    
    recovered = caps[0]
    assert recovered.state.data["test"] == "data"
    assert recovered.meta.creator == "test-creator"
    assert recovered.meta.description == "Test capsule for chain"

def test_chain_with_different_content_types():
    """Test chain with mixed content types."""
    json_capsule = odin.create_odin_file('application/json', {"type": "json"})
    text_capsule = odin.create_odin_file('text/plain', "This is plain text")
    
    b1 = odin.pack_odin(json_capsule)
    b2 = odin.pack_odin(text_capsule)
    
    buf = BytesIO()
    odin.write_chain([b1, b2], buf)
    buf.seek(0)
    
    caps = odin.open_chain(buf)
    assert len(caps) == 2
    assert caps[0].state.type == "application/json"
    assert caps[1].state.type == "text/plain"
    assert caps[0].state.data["type"] == "json"
    assert caps[1].state.data == "This is plain text"
