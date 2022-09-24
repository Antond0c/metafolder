import os
from pathlib import Path

from control import main


def test_contains_cmd1(capsys):
    script_path = Path(os.getenv('PYTEST_CURRENT_TEST')).parent.parent.absolute().joinpath("control/__init__.py")
    main([script_path, "help"])

    captured = capsys.readouterr().out

    assert "list caches" in captured


def test_contains_cmd2(capsys):
    script_path = Path(os.getenv('PYTEST_CURRENT_TEST')).parent.parent.absolute().joinpath("control/__init__.py")
    main([script_path, "help"])

    captured = capsys.readouterr().out

    assert "clean foslders" in captured
