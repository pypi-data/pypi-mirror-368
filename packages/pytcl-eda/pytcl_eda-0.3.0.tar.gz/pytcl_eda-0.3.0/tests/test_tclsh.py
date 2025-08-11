# SPDX-FileCopyrightText: 2025 Tymoteusz Blazejczyk <tymoteusz.blazejczyk@tymonx.com>
# SPDX-License-Identifier: Apache-2.0

"""Test PyTCL with classic TCL shell (`tclsh`)."""

from shutil import which
from pytcl import PyTCL
import pytest

pytestmark = pytest.mark.skipif(not which("tclsh"), reason="Requires TCL shell (tclsh)")


def test_tclsh_list_create() -> None:
    """Test TCL shell: list."""
    with PyTCL() as tclsh:
        # TCL: list 7 a 1
        items = tclsh.list(7, "a", True)

        assert len(items) == 3
        assert int(items[0]) == 7
        assert str(items[1]) == "a"
        assert bool(items[2])


def test_tclsh_list_lappend() -> None:
    """Test TCL shell: `set items [list]` and `lappend`."""
    with PyTCL() as tclsh:
        # TCL: set items {}
        items = tclsh.set("items", [])

        assert len(items) == 0

        # TCL: lappend items 5
        items = tclsh.lappend("items", 5)

        assert len(items) == 1
        assert int(items[0]) == 5

        # TCL: lappend items foo
        items = tclsh.lappend("items", "foo")

        assert len(items) == 2
        assert str(items[1]) == "foo"


def test_tclsh_dict_create() -> None:
    """Test TCL shell: `set items [dict create]`"""
    with PyTCL() as tclsh:
        # TCL: set items [dict create a 1 b 2]
        items = tclsh.set("items", tclsh.dict("create", "a", 1, "b", 2))

        assert len(dict(items)) == 2
        assert items.keys() == ["a", "b"]
        assert [int(value) for value in items.values()] == [1, 2]
        assert int(items["a"]) == 1
        assert int(items["b"]) == 2


def test_tclsh_dict_from_python_dict() -> None:
    """Test TCL shell: `set items {}`"""
    with PyTCL() as tclsh:
        # TCL: set items [dict create a 1 b 2]
        items = tclsh.set("items", {"c": 3, "d": 4})

        assert len(dict(items)) == 2
        assert items.keys() == ["c", "d"]
        assert [int(value) for value in items.values()] == [3, 4]
        assert int(items["c"]) == 3
        assert int(items["d"]) == 4
