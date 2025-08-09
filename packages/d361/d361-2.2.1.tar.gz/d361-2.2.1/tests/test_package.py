"""Test suite for d361."""


def test_version() -> None:
    """Verify package exposes version."""
    import d361

    assert d361.__version__
