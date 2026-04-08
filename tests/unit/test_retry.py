import pytest

from async_sendgrid.pool import ConnectionPool


def test_pool_default_retry():
    """Test pool initializes with default retry values."""
    pool = ConnectionPool()
    assert pool._retry.total == 5
    assert pool._retry.backoff_factor == 0.5


def test_pool_custom_retry():
    """Test pool initialization with custom retry values."""
    pool = ConnectionPool(total=3, backoff_factor=1.0)
    assert pool._retry.total == 3
    assert pool._retry.backoff_factor == 1.0


@pytest.mark.parametrize("total", [-1, -100, 1.5, "3", None])
def test_pool_invalid_total_raises(total):
    """Test that invalid total raises ValueError."""
    with pytest.raises(ValueError, match="total"):
        ConnectionPool(total=total)


@pytest.mark.parametrize("backoff_factor", [-0.5, -1, "0.5", None])
def test_pool_invalid_backoff_raises(backoff_factor):
    """Test that invalid backoff_factor raises ValueError."""
    with pytest.raises(ValueError, match="backoff_factor"):
        ConnectionPool(backoff_factor=backoff_factor)
