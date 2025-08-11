from bluer_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)


BLUER_SANDBOX_CONFIG = get_env("BLUER_SANDBOX_CONFIG")

ARVANCLOUD_PRIVATE_KEY = get_env("ARVANCLOUD_PRIVATE_KEY")
