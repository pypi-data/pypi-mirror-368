#! /usr/bin/env bash

function test_bluer_sandbox_arvancloud_seed() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_ai_seed arvancloud screen
    [[ $? -ne 0 ]] && return 1

    bluer_ai_eval ,$options \
        bluer_sandbox_arvancloud seed screen
}
