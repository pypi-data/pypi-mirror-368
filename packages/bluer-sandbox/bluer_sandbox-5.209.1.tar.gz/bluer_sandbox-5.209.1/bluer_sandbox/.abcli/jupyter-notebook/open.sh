#! /usr/bin/env bash

function bluer_sandbox_notebooks_open() {
    bluer_sandbox_notebooks_create "$1"
    [[ $? -ne 0 ]] && return 1

    export bluer_sandbox_notebooks_input="${@:2}"
    jupyter notebook
}
