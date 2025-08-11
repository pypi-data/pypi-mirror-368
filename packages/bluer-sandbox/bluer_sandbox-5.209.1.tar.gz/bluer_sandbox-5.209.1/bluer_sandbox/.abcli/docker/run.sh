#! /usr/bin/env bash

function bluer_sandbox_docker_run() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)

    bluer_ai_log "@docker: run $options ..."

    local bluer_sandbox_path=$(python3 -m bluer_sandbox locate)

    bluer_ai_eval dryrun=$do_dryrun,path=$bluer_sandbox_path \
        docker-compose run bluer_ai bash \
        --init-file /root/git/bluer-ai/bluer_ai/.abcli/bluer_ai.sh
}
