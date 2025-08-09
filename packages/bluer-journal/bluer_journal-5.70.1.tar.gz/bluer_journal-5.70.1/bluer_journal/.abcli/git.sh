#! /usr/bin/env bash

function bluer_journal_git() {
    local task=${1:-cd}

    local function_name=bluer_journal_git_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    bluer_ai_log_error "@journal: git: $task: command not found."
    return 1
}

bluer_ai_source_caller_suffix_path /git
