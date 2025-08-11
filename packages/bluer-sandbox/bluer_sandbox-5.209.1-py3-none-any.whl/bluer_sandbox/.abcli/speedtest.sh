#! /usr/bin/env bash

function bluer_sandbox_speedtest() {
    local options=$1
    local do_install=$(bluer_ai_option_int "$options" install 1)
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)

    local install_command=""
    if [[ "$do_install" == 1 ]]; then
        if [[ "$abcli_is_mac" == true ]]; then
            install_command="brew install speedtest-cli"
        elif [[ "$abcli_is_ubuntu" == true ]]; then
            install_command="sudo apt install -y speedtest-cli"
        else
            bluer_ai_log_error "do not know how to install speedtest."
            return 1
        fi

        bluer_ai_eval dryrun=$do_dryrun \
            $install_command
        [[ $? -ne 0 ]] && return 1
    fi

    bluer_ai_eval dryrun=$do_dryrun \
        speedtest
}
