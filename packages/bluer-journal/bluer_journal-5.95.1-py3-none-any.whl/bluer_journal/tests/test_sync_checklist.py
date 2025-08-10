from bluer_journal.utils.sync.checklist import sync_checklist, find_todo_items
from bluer_journal.tests.fixtures import journal_checkout


def test_sync_checklist_find_todo_items(journal_checkout):
    dict_of_todos = find_todo_items(verbose=True)
    assert isinstance(dict_of_todos, dict)


def test_sync_checklist(journal_checkout):
    assert sync_checklist(verbose=True)
