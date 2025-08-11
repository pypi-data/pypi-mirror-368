#! /usr/bin/env bash

function bluer_sandbox_offline_llm_chat() {
    local options=$1
    local do_upload=$(bluer_ai_option_int "$options" upload 1)
    local tiny=$(bluer_ai_option_int "$options" tiny 0)
    local download_model=$(bluer_ai_option_int "$options" download_model 0)

    if [[ "$download_model" == 1 ]]; then
        bluer_sandbox_offline_llm_model_download tiny=$tiny
        [[ $? -ne 0 ]] && return 1
    fi

    local object_name=$(bluer_ai_clarify_object $2 offline_llm-chat-$(bluer_ai_string_timestamp_short))
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    mkdir -pv $object_path

    bluer_ai_log "starting chat (tiny=$tiny) ..."

    python3 -m bluer_sandbox.offline_llm.interactive \
        chat \
        --tiny $tiny \
        "${@:3}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - $object_name

    bluer_objects_mlflow_tags_set \
        $object_name \
        contains=offline_llm-chat
}
