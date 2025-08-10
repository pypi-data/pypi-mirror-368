from bluer_journal.classes.page import JournalPage
from bluer_journal.tests.fixtures import journal_checkout


def test_journal_page(journal_checkout):
    page = JournalPage(
        title="Home",
        load=True,
    )

    page.generate()

    assert page.save()

    list_of_todos = page.list_of_todos()
    assert isinstance(list_of_todos, list)
