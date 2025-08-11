#! /usr/bin/env bash

function test_bluer_sandbox_seed_aws() {
    local options=$1

    local target
    for target in \
        cloudshell \
        ec2 \
        sagemaker_jupyterlab \
        studio_classic_sagemaker \
        studio_classic_sagemaker_system; do
        bluer_ai_eval ,$options \
            bluer_ai_seed $target screen
        [[ $? -ne 0 ]] && return 1
    done

    return 0
}
