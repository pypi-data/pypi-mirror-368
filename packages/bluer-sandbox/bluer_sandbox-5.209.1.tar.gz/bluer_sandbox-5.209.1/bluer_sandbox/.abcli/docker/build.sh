#! /usr/bin/env bash

function bluer_sandbox_docker_build() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_push=$(bluer_ai_option_int "$options" push $(bluer_ai_not $do_dryrun))
    local do_run=$(bluer_ai_option_int "$options" run 0)
    local no_cache=$(bluer_ai_option_int "$options" no_cache 0)
    local verbose=$(bluer_ai_option_int "$options" verbose 0)

    bluer_ai_badge "🪄🌠"
    bluer_ai_log "@docker: build $options ..."

    pushd $abcli_path_git >/dev/null

    mkdir -p temp
    cp -v ~/.kaggle/kaggle.json temp/

    local extra_args=""
    [[ "$verbose" == 1 ]] &&
        extra_args="$extra_args --progress=plain"
    [[ "$no_cache" == 1 ]] &&
        extra_args="$extra_args --no-cache"

    bluer_ai_eval ,$options \
        docker build \
        --platform=linux/amd64 \
        $extra_args \
        --build-arg HOME=$HOME \
        -t kamangir/bluer_ai \
        -f bluer-sandbox/Dockerfile \
        .
    [[ $? -ne 0 ]] && return 1

    rm -rfv temp

    if [[ "$do_push" == "1" ]]; then
        bluer_sandbox_docker_push $options
        [[ $? -ne 0 ]] && return 1
    fi

    if [[ "$do_run" == "1" ]]; then
        bluer_sandbox_docker_run $options
        [[ $? -ne 0 ]] && return 1
    fi

    popd >/dev/null
}
