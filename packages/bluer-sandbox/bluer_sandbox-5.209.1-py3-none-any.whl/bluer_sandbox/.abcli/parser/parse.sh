#! /usr/bin/env bash

function bluer_sandbox_parser_parse() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_upload=$(bluer_ai_option_int "$options" upload $(bluer_ai_not $do_dryrun))

    local url=$2
    if [[ -z "$url" ]]; then
        bluer_ai_log_error "url not found."
        return 0
    fi

    local object_name=$(bluer_ai_clarify_object $3 parsed-$(bluer_ai_string_timestamp))

    bluer_ai_eval dryrun=$do_dryrun \
        python3 -m bluer_sandbox.parser \
        parse \
        --url $url \
        --object_name $object_name \
        "${@:4}"
    [[ $? -ne 0 ]] && return 1

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - $object_name

    return 0
}
