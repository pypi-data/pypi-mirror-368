#! /usr/bin/env bash

function test_bluer_sandbox_offline_llm_prompt() {
    local options=$1

    local object_name=test_bluer_sandbox_offline_llm_prompt-$(bluer_ai_string_timestamp_short)

    bluer_sandbox_offline_llm_build
    [[ $? -ne 0 ]] && return 1

    bluer_sandbox_offline_llm_prompt \
        download_model,tiny,~upload,$options \
        "Why is Mathematics said to be the Voice of God?" \
        $object_name
}
