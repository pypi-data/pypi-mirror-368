#! /usr/bin/env bash

# https://chatgpt.com/c/68046861-c950-8005-8f01-a2c27754b4b5
function bluer_sandbox_offline_llm_model_download() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local tiny=$(bluer_ai_option_int "$options" tiny 0)
    local overwrite=$(bluer_ai_option_int "$options" overwrite 0)

    local model_object_name=$(bluer_sandbox_offline_llm_model_get object_name tiny=$tiny)
    local model_object_path=$ABCLI_OBJECT_ROOT/$model_object_name
    mkdir -pv $model_object_path

    local repo_name=$(bluer_sandbox_offline_llm_model_get repo_name tiny=$tiny)
    local filename=$(bluer_sandbox_offline_llm_model_get filename tiny=$tiny)

    if [[ "$overwrite" == 0 ]] && [[ -f "$model_object_path/$filename" ]]; then
        bluer_ai_log "✅ $repo_name/$filename in $model_object_name."
        return 0
    fi
    bluer_ai_log "downloading $repo_name/$filename -> $model_object_name ..."

    bluer_ai_eval dryrun=$do_dryrun \
        huggingface-cli download $repo_name \
        $filename \
        --local-dir $model_object_path \
        --local-dir-use-symlinks False
}
