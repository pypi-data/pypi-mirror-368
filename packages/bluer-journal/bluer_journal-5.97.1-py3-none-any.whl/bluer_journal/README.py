import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_journal import NAME, VERSION, ICON, REPO_NAME
from bluer_journal.help.functions import help_functions


def build():
    return all(
        README.build(
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {"path": ".."},
            {"path": "./docs"},
            # aliases
            {"path": "./docs/aliases"},
            {"path": "./docs/aliases/journal.md"},
        ]
    )
