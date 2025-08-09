from bluer_objects import path

from bluer_journal.classes.page import journal
from bluer_journal.tests.fixtures import journal_checkout


def test_journal(journal_checkout):
    assert journal.path
    assert path.exists(journal.path)

    list_of_pages = journal.list_of_pages()
    assert list_of_pages
    assert "Home" in list_of_pages
