#! /usr/bin/env bash

function bluer_sandbox_docker_clear() {
    local options=$1

    bluer_ai_eval ,$options \
        "docker image prune"

    bluer_ai_eval ,$options \
        "docker system prune"

    bluer_ai_eval ,$options \
        "docker-compose down --remove-orphans"
}
