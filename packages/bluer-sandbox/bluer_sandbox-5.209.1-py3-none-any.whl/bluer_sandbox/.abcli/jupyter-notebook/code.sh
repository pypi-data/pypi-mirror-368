#! /usr/bin/env bash

function bluer_sandbox_notebooks_code() {
    local notebook_name=$(bluer_ai_clarify_input $1 notebook)

    bluer_sandbox_notebooks_create "$1"

    [[ "$notebook_name" == *.ipynb ]] && notebook_name="${notebook_name%.ipynb}"

    code "$notebook_name.ipynb"
}
