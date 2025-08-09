from pathlib import Path

import os
import subprocess
import sys

from unittest.mock import patch, mock_open
from quackdoor.__main__ import main


@patch("quackdoor.__main__.read_payload")
@patch("quackdoor.__main__.encode_payload")
@patch("quackdoor.__main__.build_python_exec_command")
@patch("quackdoor.__main__.build_ducky_script")
@patch("builtins.open", new_callable=mock_open)
def test_main_success(
    mock_file, mock_build_ducky, mock_build_exec, mock_encode, mock_read, capsys
):
    # Arrange
    mock_read.return_value = "print('hello')"
    mock_encode.return_value = "encoded"
    mock_build_exec.return_value = "exec_cmd"
    mock_build_ducky.return_value = "ducky_script"

    test_args = [
        "program",
        "input.py",
        "-o",
        "output.txt",
        "-p",
        "2",
        "-r",
        "requests",
        "numpy",
    ]
    with patch.object(sys, "argv", test_args):
        # Act
        result = main()

    # Assert
    assert result == 0
    mock_read.assert_called_once_with("input.py")
    mock_encode.assert_called_once_with("print('hello')")
    mock_build_exec.assert_called_once_with("encoded")
    mock_build_ducky.assert_called_once_with(
        "exec_cmd", pip_time="2", requirements=["requests", "numpy"]
    )
    mock_file.assert_called_once_with("output.txt", "w", encoding="utf-8")
    handle = mock_file()
    handle.write.assert_called_once_with("ducky_script")

    out = capsys.readouterr().out
    assert "[+] DuckyScript written to output.txt" in out


@patch(
    "quackdoor.__main__.read_payload", side_effect=FileNotFoundError("File not found")
)
def test_main_exception(mock_read, capsys):
    test_args = ["program", "missing.py"]
    with patch.object(sys, "argv", test_args):
        result = main()

    assert result == 1
    out = capsys.readouterr().out
    assert "[!] File not found" in out


def test_main_entrypoint(tmp_path):
    input_file = tmp_path / "input.py"
    output_file = tmp_path / "output.txt"
    input_file.write_text("print('hello')")

    script_path = (Path(__file__).parent.parent / "quackdoor" / "__main__.py").resolve()
    project_root = Path(__file__).parent.parent.resolve()

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"

    result = subprocess.run(
        [sys.executable, str(script_path), str(input_file), "-o", str(output_file)],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    assert output_file.exists()
    assert f"[+] DuckyScript written to {output_file}" in result.stdout
