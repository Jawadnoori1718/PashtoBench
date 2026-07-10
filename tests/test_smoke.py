from pashtobench import __version__


def test_version_is_a_string():
    assert isinstance(__version__, str)
    assert __version__


def test_cli_imports():
    from pashtobench.cli import main

    assert callable(main)
