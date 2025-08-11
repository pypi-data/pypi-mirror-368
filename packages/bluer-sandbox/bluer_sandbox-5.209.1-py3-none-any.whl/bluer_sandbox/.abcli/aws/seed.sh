# internal function to bluer_ai_seed.
# seed is NOT local
function bluer_ai_seed_cloudshell() {
    bluer_sandbox_seed_aws "$@"
}
function bluer_ai_seed_ec2() {
    bluer_sandbox_seed_aws "$@"
}
function bluer_ai_seed_sagemaker_jupyterlab() {
    bluer_sandbox_seed_aws "$@"
}
function bluer_ai_seed_studio_classic_sagemaker() {
    bluer_sandbox_seed_aws "$@"
}
function bluer_ai_seed_studio_classic_sagemaker_system() {
    bluer_sandbox_seed_aws "$@"
}

function bluer_sandbox_seed_aws() {
    local target=$1

    [[ "$target" == "ec2" ]] &&
        env_name="worker"
    [[ "$target" == *"sagemaker"* ]] &&
        sudo_prefix=""

    bluer_ai_seed add_kaggle

    [[ "|cloudshell|studio_classic_sagemaker|" != *"|$target|"* ]] &&
        bluer_ai_seed add_ssh_key

    seed="${seed}apt-get update$delim"
    if [[ "$target" == "studio_classic_sagemaker_system" ]]; then
        # https://chat.openai.com/c/8bdce889-a9fa-41c2-839f-f75c14d48e52
        seed="${seed}conda install -y unzip$delim_section"
    fi
    if [[ "$target" == "studio_classic_sagemaker" ]]; then
        seed="${seed}apt install -y libgl1-mesa-glx rsync$delim"
        seed="${seed}conda install -c conda-forge nano --yes$delim_section"
    fi

    if [[ "$target" == "studio_classic_sagemaker" ]]; then
        bluer_ai_seed add_repo ~clone
    elif [[ "$target" == "studio_classic_sagemaker_system" ]]; then
        bluer_ai_seed add_repo https
    else
        bluer_ai_seed add_repo
    fi

    bluer_ai_seed add_bluer_ai_env

    seed="${seed}pip install --upgrade pip --no-input$delim"
    seed="${seed}pip3 install -e .$delim"
    seed="${seed}pip3 install opencv-python-headless$delim_section"

    seed="${seed}source ./bluer_ai/.abcli/bluer_ai.sh$delim_section"

    [[ "$target" == "ec2" ]] &&
        seed="${seed}source ~/.bash_profile$delim_section"

    [[ "$target" == sagemaker_jupyterlab ]] &&
        seed="${seed}bluer_ai_plugins_install all$delim_section"

    [[ "$target" == studio_classic_sagemaker* ]] &&
        bluer_ai_log_warning "run \"bash\" before pasting the seed."
}
