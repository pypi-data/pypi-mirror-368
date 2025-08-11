#! /usr/bin/env bash

function test_bluer_sandbox_docker_seed() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_ai_seed docker screen
    [[ $? -ne 0 ]] && return 1

    bluer_ai_eval ,$options \
        bluer_sandbox_docker seed screen
}
