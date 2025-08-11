#! /usr/bin/env bash

function bluer_sandbox_interview() {
    local task=$1

    local function_name=bluer_sandbox_interview_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m bluer_sandbox.interview "$@"
}
