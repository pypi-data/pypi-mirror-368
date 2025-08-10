from tqdm import tqdm
from typing import List, Dict, Set
import re

from blueness import module
from bluer_objects import file

from bluer_journal import NAME
from bluer_journal.classes.page import JournalPage
from bluer_journal.classes.journal import journal
from bluer_journal.utils.sync.utils import reformat

from bluer_journal.logger import logger


NAME = module.name(__file__, NAME)


def add_relations(
    dict_of_relations: Dict[str, List[str]],
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.add_relations ...")

    dict_of_relations_inverse: Dict[str, List[str]] = {}
    for related, list_of_relations in tqdm(dict_of_relations.items()):
        for relation in list_of_relations:

            if related in dict_of_relations.get(relation, []):
                continue

            if not file.exists(
                JournalPage(
                    title=relation.replace(" ", "-"),
                    load=False,
                    verbose=verbose,
                ).filename
            ):
                continue

            if relation not in dict_of_relations_inverse:
                dict_of_relations_inverse[relation] = []

            if related in dict_of_relations_inverse[relation]:
                continue

            dict_of_relations_inverse[relation].append(related)

    for relation in dict_of_relations_inverse:
        list_of_similar_relations = [
            relation_
            for relation_ in dict_of_relations_inverse
            if relation_.lower() == relation.lower()
        ]
        if len(list_of_similar_relations) > 1:
            logger.error(
                "similar keywords: {}".format(", ".join(list_of_similar_relations))
            )

            return False

    for relation, list_of_related in tqdm(dict_of_relations_inverse.items()):
        page = JournalPage(
            title=relation.replace(" ", "-"),
            load=True,
            verbose=verbose,
        )

        page.content = [
            f"- [[{related}]]" for related in list_of_related
        ] + page.content

        page.remove_double_blanks()

        if not page.save(
            generate=False,
            log=verbose,
        ):
            return False

    return True


# pylint: disable=unused-argument
def find_relations(
    page_title: str,
    dict_of_relations: Dict[str, List[str]],
    verbose: bool = False,
) -> bool:
    if page_title in ["Home", "_Sidebar"]:
        return True

    page = JournalPage(
        title=page_title,
        load=True,
        verbose=verbose,
    )
    updated_content: List[str] = []
    for line in page.content:

        if not line.startswith(": "):
            updated_content.append(line)
            continue

        keyword = line.split(": ", 1)[1]
        if not keyword:
            logger.info(f'keyword not found: "{line}"')
            return False

        if bool(re.fullmatch(r"\[\[.+?\]\]", keyword)):
            updated_content.append(line)
            continue

        updated_content.append(f": [[{keyword}]]")

    if updated_content != page.content:
        page.content = updated_content
        if not page.save(
            generate=False,
            log=verbose,
        ):
            return False

    set_of_relations: Set[str] = set()
    pattern = re.compile(r"\[\[([^\[\]]+)\]\]")
    for line in page.content:
        set_of_relations.update(pattern.findall(line))

    page_title_normalized = page_title.replace("-", " ")
    list_of_relations = [item.replace("-", " ") for item in list(set_of_relations)]
    dict_of_relations[page_title_normalized] = list_of_relations

    if verbose and list_of_relations:
        logger.info(
            "{} -:-> {}".format(
                page_title_normalized,
                ", ".join(list_of_relations),
            )
        )

    return True


def sync_relations(
    verbose: bool = False,
) -> bool:
    logger.info(f"{NAME}.sync_relations ...")

    dict_of_relations: Dict[str, List[str]] = {}
    list_of_pages = journal.list_of_pages(log=verbose)
    for page_title in tqdm(list_of_pages):
        if not find_relations(
            page_title=page_title,
            dict_of_relations=dict_of_relations,
            verbose=verbose,
        ):
            return False

    if not add_relations(
        dict_of_relations=dict_of_relations,
        verbose=verbose,
    ):
        return False

    return reformat(verbose=verbose)
