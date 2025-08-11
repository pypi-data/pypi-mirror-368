#! /usr/bin/env bash

# https://chatgpt.com/c/6805b118-6bb4-8005-b5d5-a503b14a3006
function bluer_sandbox_offline_llm_create_env() {
    local options=$1

    local PYTHON311="/opt/homebrew/opt/python@3.11/bin/python3.11"

    local model_object_name=$(bluer_sandbox_offline_llm_model_get object_name tiny)
    local filename=$(bluer_sandbox_offline_llm_model_get filename tiny)
    local MODEL_PATH=$ABCLI_OBJECT_ROOT/$model_object_name/$filename

    local ENV_DIR="./offline_llm_env"

    bluer_ai_log "🔧 Creating virtual environment at $ENV_DIR ..."
    $PYTHON311 -m venv "$ENV_DIR"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_log "📦 Activating environment and upgrading pip ..."
    source "$ENV_DIR/bin/activate"
    [[ $? -ne 0 ]] && return 1

    pip install --upgrade pip
    [[ $? -ne 0 ]] && return 1

    bluer_ai_log "📦 Installing numpy <2 and PyTorch (CPU only) ..."
    pip install "numpy<2"
    [[ $? -ne 0 ]] && return 1

    pip install torch --index-url https://download.pytorch.org/whl/cpu
    [[ $? -ne 0 ]] && return 1

    bluer_ai_log "🦙 Installing llama-cpp-python with Metal disabled ..."
    CMAKE_ARGS="-DLLAMA_METAL=OFF" pip install llama-cpp-python --no-cache-dir --force-reinstall
    [[ $? -ne 0 ]] && return 1

    bluer_ai_log "✅ Verifying imports ..."
    python -c "import torch; print('✅ torch:', torch.__version__)"
    [[ $? -ne 0 ]] && return 1

    python -c "from llama_cpp import Llama; print('✅ llama_cpp loaded')"
    [[ $? -ne 0 ]] && return 1

    bluer_ai_log "🧪 Running basic llama_cpp prompt..."
    python -c "from llama_cpp import Llama; llm = Llama(model_path='$MODEL_PATH'); print(llm('What is the capital of Iran?')['choices'][0]['text'])"
}
