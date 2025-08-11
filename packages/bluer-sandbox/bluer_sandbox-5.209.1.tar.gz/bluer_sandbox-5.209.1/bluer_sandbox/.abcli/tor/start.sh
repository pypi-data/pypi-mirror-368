#! /usr/bin/env bash

function bluer_sandbox_tor_start() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_install=$(bluer_ai_option_int "$options" install 0)

    if [[ "$do_install" == 1 ]]; then
        local module
        for module in tor torsocks obfs4proxy; do
            bluer_ai_eval dryrun=$do_dryrun \
                brew install $module
            [[ $? -ne 0 ]] && return 1
        done
    fi

    bluer_sandbox_tor_test $options
}
