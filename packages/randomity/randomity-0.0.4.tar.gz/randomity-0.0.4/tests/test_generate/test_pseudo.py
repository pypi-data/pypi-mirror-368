import pytest
from randomity.generate import prandom

def test_returntType():
    """Test that prandom returns a list."""
    result = prandom()
    assert isinstance(result, list)

def test_outputLength():
    """Test that prandom returns the correct number of outputs."""
    num_out = 5
    result = prandom(num_out=num_out)
    assert len(result) == num_out

def test_outputRange():
    """Test that generated numbers are within the specified range."""
    min_val = 5
    max_val = 15
    result = prandom(min_val=min_val, max_val=max_val, num_out=10)
    for num in result:
        assert min_val <= num <= max_val

def test_histogram():
    """Test that histogram is drawn when hist=True."""
    result = prandom(hist=True)
    assert isinstance(result, list)
    
def test_randSeed():
    """Test that not setting a seed uses the os.urandom method."""
    result1 = prandom()
    result2 = prandom()
    assert result1 != result2, "Random numbers should differ when no seed is set"

def test_setSeed():
    """Test that setting a seed produces consistent results."""
    seed = 100
    result1 = prandom(seed=seed)
    result2 = prandom(seed=seed)
    assert result1 == result2, "Random numbers should be the same when the same seed is used"
    