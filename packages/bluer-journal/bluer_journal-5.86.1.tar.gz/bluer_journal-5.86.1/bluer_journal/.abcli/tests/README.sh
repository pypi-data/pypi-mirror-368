#! /usr/bin/env bash

function test_bluer_journal_README() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_journal build_README
}

