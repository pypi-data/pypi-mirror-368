#! /usr/bin/env bash

function test_bluer_sandbox_README() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_sandbox build_README
}
