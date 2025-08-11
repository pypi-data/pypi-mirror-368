#! /usr/bin/env bash

function test_bluer_sandbox_offline_llm_model_get() {
    local options=$1

    local what
    local tiny
    local thing
    for what in filename object_name repo_name; do
        for tiny in 0 1; do
            thing=$(bluer_sandbox_offline_llm_model_get $what tiny=$tiny)
            bluer_ai_assert "$thing" - non-empty
            [[ $? -ne 0 ]] && return 1
        done
    done
    return 0
}
