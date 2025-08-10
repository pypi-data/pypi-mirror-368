from tqdm import tqdm
import re

from blueness import module

from bluer_journal import NAME
from bluer_journal.classes.page import JournalPage
from bluer_journal.classes.journal import journal
from bluer_journal.logger import logger


NAME = module.name(__file__, NAME)


def reformat(
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.reformat ...")

    for title in tqdm(journal.list_of_pages(log=verbose)):
        page = JournalPage(
            title=title,
            load=True,
            verbose=verbose,
        )

        page.content = (
            sorted(
                [
                    line
                    for line in page.content
                    if re.fullmatch(
                        r"- \[\[.+?\]\]",
                        line,
                    )
                ]
            )
            + [""]
            + [
                line
                for line in page.content
                if not re.fullmatch(
                    r"- \[\[.+?\]\]",
                    line,
                )
            ]
        )

        page.remove_double_blanks()

        if not page.save(
            generate=False,
            log=verbose,
        ):
            return False

    return True
