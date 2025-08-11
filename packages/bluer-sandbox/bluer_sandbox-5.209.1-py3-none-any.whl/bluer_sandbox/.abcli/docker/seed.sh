#! /usr/bin/env bash

# internal function to bluer_ai_seed.
function bluer_ai_seed_docker() {
    # seed is NOT local
    seed="${seed}source /root/git/bluer-ai/bluer_ai/.abcli/bluer_ai.sh$delim_section"
}

function bluer_sandbox_docker_seed() {
    bluer_ai_seed docker "$@"
}
