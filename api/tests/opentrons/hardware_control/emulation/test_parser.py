from typing import Sequence

import pytest
from opentrons.hardware_control.emulation.parser import Parser, Command


@pytest.fixture
def gcodes() -> Sequence[str]:
    return ["G123", "G123.2", "G1", "M123.2"]


@pytest.fixture
def parser(gcodes: Sequence[str]) -> Parser:
    return Parser(gcodes)


@pytest.mark.parametrize(
    argnames=["line", "expected"],
    argvalues=[
        ["", []],
        ["G2", []],
        ["G13", []],
        ["M123", []],
        ["G123 V2", [Command(gcode="G123", params={"V": 2.0})]],
        ["G123G123.2G1", [
            Command(gcode="G123", params={}),
            Command(gcode="G123.2", params={}),
            Command(gcode="G1", params={}),
        ]],
        ["M123.2 B132C-1D321.2", [
            Command(gcode="M123.2", params={"B": 132, "C": -1, "D": 321.2})
        ]]

    ]
)
def test_parse_command(parser: Parser, line: str, expected: Sequence[Command]) -> None:
    """It should parse the commands and parameters."""
    result = list(parser.parse(line))

    assert result == expected
