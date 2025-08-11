#! /usr/bin/env bash

function bluer_sandbox_notebooks_create() {
    local notebook_name=$(bluer_ai_clarify_input $1 notebook)

    # for unity with the rest of @notebooks
    [[ "$notebook_name" == *.ipynb ]] && notebook_name="${notebook_name%.ipynb}"

    if [ -f "$notebook_name.ipynb" ]; then
        touch "$notebook_name.ipynb"
    else
        local path=$(dirname "$notebook_name.ipynb")
        mkdir -pv $path

        cp -v \
            $(python3 -m bluer_sandbox locate)/assets/template.ipynb \
            "$notebook_name.ipynb"
    fi
}
