#! /usr/bin/env bash

function bluer_journal_git_pull() {
    local options=$1
    local do_pull=$(bluer_ai_option_int "$options" pull 1)
    local is_webhook=$(bluer_ai_option_int "$options" webhook 0)

    if [[ -z "$BLUER_JOURNAL_REPO" ]]; then
        bluer_ai_log_error "BLUER_JOURNAL_REPO is not set."
        return 1
    fi

    local repo_name
    for repo_name in \
        $BLUER_JOURNAL_REPO \
        $BLUER_JOURNAL_REPO.wiki; do
        if [[ ! -d "$abcli_path_git/$repo_name" ]]; then
            if [[ "$abcli_is_github_workflow" == true ]]; then
                pushd $abcli_path_git >/dev/null
                if [[ "$is_webhook" == 1 ]]; then
                    bluer_ai_eval - \
                        git clone https://x-access-token:$BLUER_AI_GITHUB_TOKEN@github.com/kamangir/$repo_name.git
                else
                    bluer_ai_eval - \
                        git clone https://github.com/kamangir/$repo_name.git
                fi
                [[ $? -ne 0 ]] && return 1
                popd >/dev/null
            else
                bluer_ai_git_clone $repo_name
                [[ $? -ne 0 ]] && return 1
            fi
        fi
    done

    [[ "$do_pull" == 0 ]] &&
        return 0

    bluer_ai_git \
        $BLUER_JOURNAL_REPO.wiki \
        pull \
        ~all
}
