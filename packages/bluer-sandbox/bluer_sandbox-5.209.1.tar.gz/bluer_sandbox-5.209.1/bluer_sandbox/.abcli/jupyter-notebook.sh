#! /usr/bin/env bash

function bluer_sandbox_notebooks() {
    local task=${1:-open}
    [[ "$task" == "touch" ]] && task="create"

    local function_name=bluer_sandbox_notebooks_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    bluer_ai_log_error "@notebooks: $task: command not found."
    return 1
}

bluer_ai_source_caller_suffix_path /jupyter-notebook
