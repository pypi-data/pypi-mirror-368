#! /usr/bin/env bash

function bluer_journal() {
    local task=${1:-open}

    bluer_ai_generic_task \
        plugin=bluer_journal,task=$task \
        "${@:2}"
}

bluer_ai_log $(bluer_journal version --show_icon 1)
