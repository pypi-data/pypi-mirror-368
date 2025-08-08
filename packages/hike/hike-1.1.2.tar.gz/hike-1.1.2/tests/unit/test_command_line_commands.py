"""Tests for the command line command matching code."""

##############################################################################
# Pytest imports.
from pytest import mark

##############################################################################
# Local imports.
from hike.widgets.command_line.base_command import InputCommand


##############################################################################
class ExampleCommand(InputCommand):
    COMMAND = "`test`"
    ALIASES = "`t`, `tester`, `testing`"


##############################################################################
@mark.parametrize(
    "look_for, found",
    (
        ("test", True),
        ("t", True),
        ("tester", True),
        ("testing", True),
        ("TEST", True),
        ("T", True),
        ("TESTER", True),
        ("TESTING", True),
        ("  TeST  ", True),
        ("  T  ", True),
        ("  TEstER  ", True),
        ("  TESting  ", True),
        ("", False),
        ("te", False),  # codespell:ignore
    ),
)
def test_is_command(look_for: str, found: bool) -> None:
    """We should be able to find if a command is a match."""
    assert ExampleCommand.is_command(look_for) is found


##############################################################################
@mark.parametrize(
    "split, result",
    (
        ("", ("", "")),
        ("test", ("test", "")),
        (" test ", ("test", "")),
        ("test test", ("test", "test")),
        (" test  test ", ("test", "test")),
        ("test test test test", ("test", "test test test")),
    ),
)
def test_split_command(split: str, result: tuple[str, str]) -> None:
    """The command splitting code should work as expected."""
    assert ExampleCommand.split_command(split) == result


### test_command_line_commands.py ends here
