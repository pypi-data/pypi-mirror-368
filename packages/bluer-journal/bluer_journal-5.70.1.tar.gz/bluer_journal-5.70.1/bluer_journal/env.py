from bluer_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)


BLUER_JOURNAL_REPO = get_env("BLUER_JOURNAL_REPO")

BLUER_JOURNAL_CONFIG = get_env("BLUER_JOURNAL_CONFIG")
