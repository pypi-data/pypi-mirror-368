from typing import List

from bluer_options.terminal import show_usage, xtra


def help_cd(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@journal",
            "git",
            "cd",
        ],
        "cd git/journal.",
        mono=mono,
    )


def pull_options(mono: bool):
    return xtra("~pull,token", mono=mono)


def help_pull(
    tokens: List[str],
    mono: bool,
) -> str:
    options = pull_options(mono=mono)

    return show_usage(
        [
            "@journal",
            "git",
            "pull",
            f"[{options}]",
        ],
        "git -> journal.",
        mono=mono,
    )


def push_options(
    mono: bool,
    cascade: bool = False,
):
    return "".join(
        ([] if cascade else [xtra("dryrun,", mono=mono)])
        + [xtra("~push", mono=mono)]
        + ([] if cascade else [xtra(",~sync", mono=mono)])
        + [xtra(",token", mono=mono)]
    )


def help_push(
    tokens: List[str],
    mono: bool,
) -> str:

    return show_usage(
        [
            "@journal",
            "git",
            "push",
            f"[{push_options(mono=mono)}]",
        ],
        "journal -> git.",
        mono=mono,
    )


help_functions = {
    "cd": help_cd,
    "pull": help_pull,
    "push": help_push,
}
