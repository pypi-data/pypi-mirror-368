#! /usr/bin/env bash

function bluer_journal_action_git_before_push() {
    bluer_journal build_README
    [[ $? -ne 0 ]] && return 1

    [[ "$(bluer_ai_git get_branch)" != "main" ]] &&
        return 0

    bluer_journal pypi build
}
