from typing import List
import os
import glob

from bluer_objects.env import abcli_path_git
from bluer_objects import file

from bluer_journal.env import BLUER_JOURNAL_REPO
from bluer_journal.logger import logger


class Journal:
    def __init__(self): ...

    def list_of_pages(
        self,
        log: bool = False,
    ) -> List[str]:
        list_of_pages = sorted(
            [
                file.name(filename)
                for filename in glob.glob(
                    os.path.join(
                        self.path,
                        "*.md",
                    )
                )
            ]
        )

        if log:
            logger.info(
                "{} page(s): {}".format(
                    len(list_of_pages),
                    ", ".join(
                        list_of_pages[:3] + ["..."],
                    ),
                )
            )

        return list_of_pages

    @property
    def path(self):
        return os.path.join(
            abcli_path_git,
            f"{BLUER_JOURNAL_REPO}.wiki",
        )


journal = Journal()
