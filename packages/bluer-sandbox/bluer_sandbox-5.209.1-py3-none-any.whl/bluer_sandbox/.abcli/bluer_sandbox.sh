#! /usr/bin/env bash

function bluer_sandbox() {
    local task=$1

    bluer_ai_generic_task \
        plugin=bluer_sandbox,task=$task \
        "${@:2}"
}

bluer_ai_log $(bluer_sandbox version --show_icon 1)
