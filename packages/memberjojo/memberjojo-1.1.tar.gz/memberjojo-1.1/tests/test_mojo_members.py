"""
Tests for the member module
"""

from csv import DictWriter
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from memberjojo import Member

# pylint: disable=redefined-outer-name
# or pylint thinks fixtures are redined as function variables
# --- Fixtures & Helpers ---


@pytest.fixture
def mock_csv_file(tmp_path):
    """
    Create a temporary mock CSV file for testing.
    Returns path to the CSV.
    """
    fieldnames = [
        "Member number",
        "Title",
        "First name",
        "Last name",
        "membermojo ID",
        "Short URL",
    ]
    rows = [
        {
            "Member number": "1",
            "Title": "Mr",
            "First name": "John",
            "Last name": "Doe",
            "membermojo ID": "1001",
            "Short URL": "http://short.url/johndoe",
        },
        {
            "Member number": "2",
            "Title": "Ms",
            "First name": "Jane",
            "Last name": "Smith",
            "membermojo ID": "1002",
            "Short URL": "http://short.url/janesmith",
        },
        {
            "Member number": "3",
            "Title": "Dr",
            "First name": "Emily",
            "Last name": "Stone",
            "membermojo ID": "1001",
            "Short URL": "http://short.url/emilystone",
        },  # duplicate ID
        {
            "Member number": "1",
            "Title": "Mrs",
            "First name": "Sara",
            "Last name": "Connor",
            "membermojo ID": "1003",
            "Short URL": "http://short.url/saraconnor",
        },  # duplicate number
        {
            "Member number": "4",
            "Title": "Sir",
            "First name": "Rick",
            "Last name": "Grimes",
            "membermojo ID": "1004",
            "Short URL": "http://short.url/rickgrimes",
        },  # invalid title
    ]

    csv_path = tmp_path / "mock_data.csv"
    with csv_path.open(mode="w", encoding="ISO-8859-1", newline="") as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return Path(csv_path)


@pytest.fixture
def db_path():
    """
    Temp file for db connection
    """
    with NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        path = Path(tmp.name)
    yield path
    path.unlink()


@pytest.fixture
def member_db(db_path, mock_csv_file):
    """
    Test sqlite member database
    """
    test_db = Member(db_path)
    test_db.import_csv(mock_csv_file)
    return test_db


# --- Tests ---


def test_empty_db(capsys):
    """
    Test empty db
    """
    with NamedTemporaryFile(suffix=".db") as tmp:
        empty_db = Member(tmp.name)
        # create tables so is empty database
        empty_db._create_tables()  # pylint: disable=protected-access
        empty_db.show_table()
        captured = capsys.readouterr()
        assert "(No data)" in captured.out
        assert empty_db.count() == 0


def test_invalid_csv_path_message(tmp_path, db_path, capsys):
    """
    Test import non existing csv file
    """
    non_exist = Path(tmp_path, "non-exist.csv")
    txn = Member(db_path)
    txn.import_csv(non_exist)
    # Capture stdout
    captured = capsys.readouterr()
    assert "CSV file not found" in captured.out
    assert str(non_exist) in captured.out


def test_member_import_and_validation(member_db):
    """
    Test importing valid/invalid members from CSV.
    """
    # Valid inserts
    assert member_db.get_number_first_last("john", "doe") == 1
    assert member_db.get_number("Jane Smith") == 2
    assert member_db.get_name(2) == "Jane Smith"
    # Invalid member number
    assert member_db.get_name(888) is None

    # Should not be inserted due to duplicate membermojo ID
    assert member_db.get_number_first_last("Emily", "Stone") is None

    # Should not be inserted due to duplicate member_number
    assert member_db.get_number("Sara Connor") is None

    # Should not be inserted due to invalid title
    assert member_db.get_number_first_last("Rick", "Grimes") is None


def test_show_table(member_db):
    """
    Test the show table function
    """
    # Should be equal as default show_table is 5 entries and member_db is 2
    entries = member_db.count()
    assert entries == 2
    assert member_db.show_table() == member_db.show_table(100)
    assert member_db.show_table(entries) == member_db.show_table(100)


def test_get_number_first_last_not_found_raises(member_db):
    """
    Test found_error
    """
    with pytest.raises(
        ValueError, match=r"❌ Cannot find: John Snow in member database."
    ):
        member_db.get_number_first_last("John", "Snow", found_error=True)


def test_get_number_first_last_more_names(member_db):
    """
    Test logic for 3 names passed
    """
    assert member_db.get_number("Dr Jane Smith") == 2
    assert member_db.get_number("John Jojo Doe") == 1
    with pytest.raises(ValueError) as exc_info:
        member_db.get_number("Emily Sara", found_error=True)

    assert "Cannot find" in str(exc_info.value)
