import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_journal import NAME
from bluer_journal.utils.sync.functions import sync
from bluer_journal.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="sync",
)
parser.add_argument(
    "--checklist",
    type=int,
    default=1,
    help="0 | 1",
)
parser.add_argument(
    "--relations",
    type=int,
    default=1,
    help="0 | 1",
)
parser.add_argument(
    "--verbose",
    type=int,
    default=0,
    help="0 |1",
)
args = parser.parse_args()

success = False
if args.task == "sync":
    success = sync(
        checklist=args.checklist == 1,
        relations=args.relations == 1,
        verbose=args.verbose == 1,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
