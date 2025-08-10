#! /usr/bin/env bash

function test_bluer_journal_sync() {
    local options=$1

    bluer_journal_sync \
        ~push,$options
}
