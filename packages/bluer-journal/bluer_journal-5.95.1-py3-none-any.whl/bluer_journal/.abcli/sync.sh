#! /usr/bin/env bash

function bluer_journal_sync() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)

    local pull_options=$2
    local do_pull=$(bluer_ai_option_int "$pull_options" pull 1)
    if [[ "$do_pull" == 1 ]]; then
        bluer_journal_git_pull $pull_options
        [[ $? -ne 0 ]] && return 1
    fi

    local push_options=$3
    local do_push=$(bluer_ai_option_int "$push_options" push 1)

    bluer_ai_eval dryrun=$do_dryrun \
        python3 -m bluer_journal.utils \
        sync \
        "${@:4}"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_git \
        $BLUER_JOURNAL_REPO.wiki \
        --no-pager diff
    [[ $? -ne 0 ]] && return 1

    if [[ "$do_push" == 1 ]]; then
        bluer_journal_git_push ~sync,$push_options
    fi
}
