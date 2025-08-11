#! /usr/bin/env bash

function test_bluer_sandbox_parser_parse() {
    local options=$1

    local object_name=test_bluer_sandbox_parser_parse-$(bluer_ai_string_timestamp)

    local url="https://iribnews.ir"
    [[ "$abcli_is_github_workflow" == true ]] &&
        url="https://cnn.com"

    bluer_ai_eval ,$options \
        bluer_sandbox_parser_parse \
        ~upload,$options \
        $url \
        $object_name
}
