#! /usr/bin/env bash

function bluer_sandbox_offline_llm_model_get() {
    local options_what=$1
    local what=$(bluer_ai_option_choice "$options_what" filename,object_name,repo_name object_name)

    local options=$2
    local tiny=$(bluer_ai_option_int "$options" tiny 0)

    python3 -m bluer_sandbox.offline_llm.model \
        get \
        --what $what \
        --tiny $tiny
}
