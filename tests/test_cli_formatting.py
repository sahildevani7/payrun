import pytest

from payrun.cli.formatting import format_table
from payrun.errors import ValidationError


def test_header_and_separator_present_with_no_rows():
    table = format_table(["ID", "Name"], [])
    lines = table.splitlines()
    assert lines[0] == "ID | Name"
    assert lines[1] == "---+-----"


def test_columns_are_padded_to_the_widest_cell():
    table = format_table(["ID", "Name"], [["E0001", "Jordan Lee"], ["E2", "Ada"]])
    lines = table.splitlines()
    assert lines[0] == "ID    | Name      "
    assert lines[2] == "E0001 | Jordan Lee"
    assert lines[3] == "E2    | Ada       "


def test_one_row_per_input_row():
    table = format_table(["ID"], [["E0001"], ["E0002"], ["E0003"]])
    assert len(table.splitlines()) == 5


def test_rejects_row_with_wrong_column_count():
    with pytest.raises(ValidationError):
        format_table(["ID", "Name"], [["E0001"]])


def test_single_column_table_pads_the_header_to_the_widest_row():
    table = format_table(["ID"], [["E0001"]])
    assert table.splitlines() == ["ID   ", "-----", "E0001"]


def test_single_column_table_with_no_rows_has_no_padding():
    table = format_table(["ID"], [])
    assert table.splitlines() == ["ID", "--"]
