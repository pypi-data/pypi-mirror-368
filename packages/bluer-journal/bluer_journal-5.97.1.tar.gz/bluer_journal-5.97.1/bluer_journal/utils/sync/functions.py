from blueness import module

from bluer_journal import NAME
from bluer_journal.utils.sync.checklist import sync_checklist
from bluer_journal.utils.sync.relations import sync_relations
from bluer_journal.logger import logger


NAME = module.name(__file__, NAME)


def sync(
    checklist: bool = True,
    relations: bool = True,
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.sync ...")

    if checklist:
        if not sync_checklist(verbose=verbose):
            return False

    if relations:
        if not sync_relations(verbose=verbose):
            return False

    return True
