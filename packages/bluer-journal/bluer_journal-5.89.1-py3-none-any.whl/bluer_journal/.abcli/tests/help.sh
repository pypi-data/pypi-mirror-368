#! /usr/bin/env bash

function test_bluer_journal_help() {
    local options=$1

    local module
    for module in \
        "@journal" \
        \
        "@journal git" \
        "@journal git cd" \
        "@journal git pull" \
        "@journal git push" \
        "@journal sync" \
        \
        "@journal open" \
        \
        "@journal pypi" \
        "@journal pypi browse" \
        "@journal pypi build" \
        "@journal pypi install" \
        \
        "@journal pytest" \
        \
        "@journal test" \
        "@journal test list" \
        \
        "bluer_journal"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
