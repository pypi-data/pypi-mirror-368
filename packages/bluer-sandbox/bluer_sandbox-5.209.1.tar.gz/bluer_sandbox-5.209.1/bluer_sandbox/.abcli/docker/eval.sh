#! /usr/bin/env bash

function bluer_sandbox_docker_eval() {
    local options=$1
    local do_verbose=$(bluer_ai_option_int "$options" verbose 0)

    local eval_options="install,mono"
    [[ "$do_verbose" == 1 ]] &&
        eval_options="$eval_options,verbose"

    local command_line="source \
        /root/git/bluer-ai/bluer_ai/.abcli/bluer_ai.sh \
        $eval_options \
        bluer_ai_eval $options \
        ${@:2}"

    local bluer_sandbox_path=$(python3 -m bluer_sandbox locate)

    bluer_ai_eval dryrun=$do_dryrun,path=$bluer_sandbox_path \
        docker-compose run bluer_ai \
        bash -c \"$command_line\"
}
