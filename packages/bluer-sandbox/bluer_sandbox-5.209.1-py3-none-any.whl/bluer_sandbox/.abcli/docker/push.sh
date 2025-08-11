#! /usr/bin/env bash

function bluer_sandbox_docker_push() {
    local options=$1

    bluer_ai_eval ,$options \
        docker push \
        kamangir/bluer_ai:latest
}
