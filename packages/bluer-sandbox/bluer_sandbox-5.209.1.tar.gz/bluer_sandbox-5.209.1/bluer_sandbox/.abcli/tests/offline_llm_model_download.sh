#! /usr/bin/env bash

function test_bluer_sandbox_offline_llm_model_download() {
    local options=$1

    bluer_sandbox_offline_llm_model_download \
        tiny,$options
}
