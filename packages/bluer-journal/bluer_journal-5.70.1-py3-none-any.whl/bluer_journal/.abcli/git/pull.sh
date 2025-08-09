#! /usr/bin/env bash

function bluer_journal_git_pull() {
    local options=$1
    local do_pull=$(bluer_ai_option_int "$options" pull 1)

    local repo_name
    for repo_name in \
        $BLUER_JOURNAL_REPO \
        $BLUER_JOURNAL_REPO.wiki; do
        if [[ ! -d "$abcli_path_git/$repo_name" ]]; then
            if [[ "$abcli_is_github_workflow" == true ]]; then
                pushd $abcli_path_git >/dev/null
                git clone https://github.com/kamangir/$repo_name.git
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
