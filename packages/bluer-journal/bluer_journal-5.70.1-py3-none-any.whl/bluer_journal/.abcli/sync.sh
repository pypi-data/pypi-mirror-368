#! /usr/bin/env bash

function bluer_journal_sync() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_pull=$(bluer_ai_option_int "$options" pull 1)
    local do_push=$(bluer_ai_option_int "$options" push 1)

    if [[ "$do_pull" == 1 ]]; then
        bluer_journal_git_pull
    fi

    bluer_ai_eval dryrun=$do_dryrun \
        python3 -m bluer_journal.utils \
        sync \
        "${@:2}"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_git \
        $BLUER_JOURNAL_REPO.wiki \
        --no-pager diff
    [[ $? -ne 0 ]] && return 1

    if [[ "$do_push" == 1 ]]; then
        bluer_journal_git_push ~sync
    fi
}
