def get(
    what: str,
    tiny: bool,
) -> str:
    if what == "filename":
        if tiny:
            return "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

        return "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

    if what == "object_name":
        model_object_name = "offline-llm-model-object"
        if tiny:
            model_object_name = f"{model_object_name}-tiny"

        return model_object_name

    if what == "repo_name":
        if tiny:
            return "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"

        return "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"

    return f"invalid-{what}"
