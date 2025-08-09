import git
import pytest

from bluer_objects import path

from bluer_journal.env import BLUER_JOURNAL_REPO
from bluer_journal.classes.journal import journal


@pytest.fixture
def journal_checkout():
    if not path.exists(journal.path):
        git.Repo.clone_from(
            f"https://github.com/kamangir/{BLUER_JOURNAL_REPO}.wiki.git",
            journal.path,
        )
