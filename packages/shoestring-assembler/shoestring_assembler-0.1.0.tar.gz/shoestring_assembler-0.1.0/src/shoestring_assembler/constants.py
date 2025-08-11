import os
from pathlib import Path

class Constants:
    INSTALLED_SOLUTIONS_LIST = Path(os.getenv("HOME"))/".local/share/shoestring/installed.json"

    # SOLUTION FILE PATHS (relative to solution root)
    SOLUTION_FILES_DIR = "solution_files"
    MODULE_SOURCE_FILES_DIR = f"{SOLUTION_FILES_DIR}/sources"
    SOLUTION_CONFIG_DIR = f"{SOLUTION_FILES_DIR}/config"
    USER_CONFIG_SRC_DIR = f"{SOLUTION_FILES_DIR}/user_config_templates"

    DATA_DIR = "data"
    USER_CONFIG_DIR = "user_config"

    TEMPLATE_MANAGEMENT_SUBDIR = "__templating"
    VERSION_FILE_NAME = "__version__"
    DEFAULTS_FILE_NAME = "defaults.json"
    PREV_ANSWERS_FILE_NAME = "prev_answers.json"
    PROMPTS_FILE = "prompts.yaml"

    DOCKER_NETWORK_NAME = "internal"

    META_FILE_NAME = "meta.toml"
    DOCKER_ALIAS_SUFFIX = ".docker.local"

    # TODO
    DEFAULT_GIT_HOST = ""
    DEFAULT_GIT_REPO = ""

