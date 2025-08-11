#! /usr/bin/env bash

# https://chatgpt.com/c/67fae383-ecc8-8005-b3fa-a6aeb08ca931
function bluer_sandbox_offline_llm_build() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)

    bluer_ai_git_clone \
        https://github.com/ggerganov/llama.cpp
    [[ $? -ne 0 ]] && return 1

    pushd $abcli_path_git/llama.cpp >/dev/null
    # https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
    bluer_ai_eval dryrun=$do_dryrun \
        cmake -B build
    [[ $? -ne 0 ]] && return 1

    bluer_ai_eval dryrun=$do_dryrun \
        cmake --build build --config Release
    [[ $? -ne 0 ]] && return 1
    popd >/dev/null
}
