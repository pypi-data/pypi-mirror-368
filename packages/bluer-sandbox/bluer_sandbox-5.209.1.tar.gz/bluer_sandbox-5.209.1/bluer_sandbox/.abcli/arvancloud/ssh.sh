#! /usr/bin/env bash

function bluer_sandbox_arvancloud_ssh() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_seed=$(bluer_ai_option_int "$options" seed 1)

    local ip_address=$2
    if [[ -z "$ip_address" ]]; then
        bluer_ai_log_error "ip address not found."
        return 1
    fi

    local pem_filename="$HOME/.ssh/$ARVANCLOUD_PRIVATE_KEY.pem"
    if [[ ! -f "$pem_filename" ]]; then
        bluer_ai_log_error "$pem_filename not found."
        return 1
    fi

    chmod 400 $pem_filename

    bluer_ai_badge "🌀"

    if [[ "$do_seed" == 1 ]]; then
        bluer_ai_seed arvancloud clipboard
        [[ $? -ne 0 ]] && return 1
    fi

    # https://chatgpt.com/c/683e8862-1078-8005-85e5-ff3915347e3e
    ssh-keygen -R $ip_address # Remove any old entry
    ssh-keyscan -t ed25519 $ip_address >>~/.ssh/known_hosts

    bluer_ai_eval dryrun=$do_dryrun \
        ssh \
        -i $pem_filename \
        ubuntu@$ip_address
}
