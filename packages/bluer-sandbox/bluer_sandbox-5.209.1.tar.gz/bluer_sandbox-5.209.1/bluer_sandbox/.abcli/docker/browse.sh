#! /usr/bin/env bash

function bluer_sandbox_docker_browse() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local show_public=$(bluer_ai_option_int "$options" public 1)

    local url="https://hub.docker.com/repository/docker/kamangir/bluer_ai/general"
    [[ "$show_public" == 1 ]] &&
        local url="https://hub.docker.com/r/kamangir/bluer_ai/tags"

    bluer_ai_browse $url
}
