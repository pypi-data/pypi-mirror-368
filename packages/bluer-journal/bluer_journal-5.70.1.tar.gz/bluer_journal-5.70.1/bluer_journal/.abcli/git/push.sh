#! /usr/bin/env bash

function bluer_journal_git_push() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_push=$(bluer_ai_option_int "$options" push 1)
    local do_sync=$(bluer_ai_option_int "$options" sync 1)

    if [[ "$do_sync" == 1 ]]; then
        bluer_journal_sync ~push,dryrun=$do_dryrun
        [[ $? -ne 0 ]] && return 1
    fi

    if [[ "$do_push" == 1 ]]; then
        bluer_ai_git \
            $BLUER_JOURNAL_REPO.wiki \
            push \
            "@journal git push" \
            ~increment_version
    fi
}
