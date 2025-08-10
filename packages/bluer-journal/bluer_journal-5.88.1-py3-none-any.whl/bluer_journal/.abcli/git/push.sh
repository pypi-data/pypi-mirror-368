#! /usr/bin/env bash

function bluer_journal_git_push() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_push=$(bluer_ai_option_int "$options" push 1)
    local do_sync=$(bluer_ai_option_int "$options" sync 1)
    local is_webhook=$(bluer_ai_option_int "$options" webhook 0)

    if [[ "$do_sync" == 1 ]]; then
        bluer_journal_sync \
            dryrun=$do_dryrun - \
            ~push
        [[ $? -ne 0 ]] && return 1
    fi

    if [[ "$do_push" == 1 ]]; then
        if [[ "$is_webhook" == 1 ]]; then
            pushd $abcli_path_git/$BLUER_JOURNAL_REPO.wiki >/dev/null
            [[ $? -ne 0 ]] && return 1

            bluer_ai_eval dryrun=$do_dryrun \
                git push "https://$BLUER_AI_GITHUB_TOKEN@github.com/kamangir/$BLUER_JOURNAL_REPO.wiki.git"
            [[ $? -ne 0 ]] && return 1

            popd >/dev/null
        else
            bluer_ai_git \
                $BLUER_JOURNAL_REPO.wiki \
                push \
                "@journal git push" \
                ~increment_version
        fi
    fi
}
