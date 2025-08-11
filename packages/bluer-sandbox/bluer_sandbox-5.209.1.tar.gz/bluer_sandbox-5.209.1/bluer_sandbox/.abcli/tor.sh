#! /usr/bin/env bash

function bluer_sandbox_tor() {
    local task=${1-:install}

    local function_name=bluer_sandbox_tor_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    bluer_ai_log_error "@sandbox: @tor: $task: command not found."
}

bluer_ai_source_caller_suffix_path /tor
