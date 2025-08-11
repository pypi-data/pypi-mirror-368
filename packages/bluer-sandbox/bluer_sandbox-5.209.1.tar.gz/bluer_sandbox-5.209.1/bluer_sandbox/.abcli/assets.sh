#! /usr/bin/env bash

function bluer_sandbox_assets() {
    local task=$1

    local function_name=bluer_sandbox_assets_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m bluer_sandbox.assets "$@"
}

bluer_ai_source_caller_suffix_path /assets
