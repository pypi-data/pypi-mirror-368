#! /usr/bin/env bash

function bluer_sandbox_arvancloud() {
    local task=${1:-ssh}

    local function_name=bluer_sandbox_arvancloud_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 bluer_sandbox.arvancloud "$@"
}

bluer_ai_source_caller_suffix_path /arvancloud
