from vibesum import vibesum
from dotenv import load_dotenv

load_dotenv()


def test_vibesum():
    assert vibesum(1, 2) == 3
    assert vibesum(5, 3) == 8
    assert vibesum(0, 0) == 0
    assert vibesum(-1, 1) == 0


def test_large_numbers():
    assert vibesum(100, 200) == 300
    assert vibesum(999, 1) == 1000
    assert vibesum(123, 456) == 579


def test_negative_numbers():
    assert vibesum(-5, -3) == -8
    assert vibesum(-10, 5) == -5
    assert vibesum(10, -3) == 7