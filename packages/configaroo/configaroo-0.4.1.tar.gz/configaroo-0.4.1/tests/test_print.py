"""Test pretty printing of configurations."""

import pytest

from configaroo import Configuration, print_configuration
from tests.schema import ConfigSchema


def test_printing_of_config(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that a configuration can be printed."""
    print_configuration(config, indent=4)
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- number: 42" in lines
    assert "- word: 'platypus'" in lines
    assert "- nested" in lines
    assert "    - pie: 3.14" in lines


def test_indentation(capsys: pytest.CaptureFixture[str], config: Configuration) -> None:
    """Test that indentation can be controlled."""
    print_configuration(config, indent=7)
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "       - pie: 3.14" in lines


def test_printing_of_basemodel(
    capsys: pytest.CaptureFixture[str], config: Configuration, model: type[ConfigSchema]
) -> None:
    """Test that a configuration converted into a BaseModel can be printed."""
    print_configuration(config.with_model(model))
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- number: 42" in lines
    assert "- word: 'platypus'" in lines
    assert "- nested" in lines
    assert "    - pie: 3.14" in lines


def test_printing_of_dynamic_values(
    capsys: pytest.CaptureFixture[str], config: Configuration
) -> None:
    """Test that interpolated values are printed correctly."""
    print_configuration(config.parse_dynamic({"message": "testing configaroo"}))
    stdout = capsys.readouterr().out
    lines = stdout.splitlines()

    assert "- number: 42" in lines
    assert "- phrase: 'The meaning of life is 42'" in lines
    assert "    - format: '<level>{level:<8} testing configaroo</level>'" in lines
