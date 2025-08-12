import pytest
from src.randomity.generate import qrandom

def test_returntType():
    """Test that qrandom returns a list."""
    result = qrandom()
    assert isinstance(result, list)

def test_outputLength():
    """Test that qrandom returns the correct number of outputs."""
    num_out = 5
    result = qrandom(num_out=num_out)
    assert len(result) == num_out

def test_outputRange():
    """Test that generated numbers are within the specified range."""
    min_val = 5
    max_val = 15
    result = qrandom(min_val=min_val, max_val=max_val, num_out=10)
    for num in result:
        assert min_val <= num <= max_val

def test_histogram():
    """Test that histogram is drawn when hist=True."""
    result = qrandom(hist=True)
    assert isinstance(result, list)

def test_gates():
    """Test that different quantum gates can be used."""
    gates = ["h", "rx", "ry", "sx"]
    for gate in gates:
        result = qrandom(q_gate=gate)
        assert isinstance(result, list)