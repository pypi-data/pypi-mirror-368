#! /usr/bin/env bash

function bluer_journal_open() {
    local title=${1:-$(bluer_ai_string_today)}

    local url="https://github.com/kamangir/$BLUER_JOURNAL_REPO/wiki"
    [[ "$title" != "home" ]] &&
        url="$url/$title"

    bluer_ai_browse $url
}
