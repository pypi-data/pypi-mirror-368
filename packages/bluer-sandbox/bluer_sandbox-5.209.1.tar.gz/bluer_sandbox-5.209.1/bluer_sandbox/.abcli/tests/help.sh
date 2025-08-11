#! /usr/bin/env bash

function test_bluer_sandbox_help() {
    local options=$1

    local module
    for module in \
        "@arvan" \
        "@arvan seed" \
        "@arvan ssh" \
        \
        "@assets" \
        "@assets publish" \
        \
        "@docker" \
        "@docker browse" \
        "@docker build" \
        "@docker clear" \
        "@docker eval" \
        "@docker push" \
        "@docker run" \
        "@docker seed" \
        \
        "@interview" \
        \
        "@notebooks" \
        "@notebooks build" \
        "@notebooks code" \
        "@notebooks connect" \
        "@notebooks create" \
        "@notebooks host" \
        "@notebooks open" \
        \
        "@offline_llm" \
        "@offline_llm build" \
        "@offline_llm chat" \
        "@offline_llm create_env" \
        "@offline_llm model" \
        "@offline_llm model download" \
        "@offline_llm model get" \
        "@offline_llm prompt" \
        \
        "@parser" \
        "@parser parse" \
        \
        "@sandbox" \
        \
        "@sandbox pypi" \
        "@sandbox pypi browse" \
        "@sandbox pypi build" \
        "@sandbox pypi install" \
        \
        "@sandbox pytest" \
        \
        "@sandbox test" \
        "@sandbox test list" \
        \
        "@speedtest" \
        \
        "@tor" \
        "@tor test" \
        "@tor start" \
        \
        "bluer_sandbox"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1

        bluer_ai_hr
    done

    return 0
}
