from fulltrader import hello


def test_hello_default() -> None:
    assert hello() == "Hello, FullTrader!"


def test_hello_custom() -> None:
    assert hello("Ederson") == "Hello, Ederson!"


