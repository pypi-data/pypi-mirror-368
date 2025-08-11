#! /usr/bin/env bash

function test_bluer_sandbox_version() {
    local options=$1

    bluer_ai_eval ,$options \
        "bluer_sandbox version ${@:2}"
}
