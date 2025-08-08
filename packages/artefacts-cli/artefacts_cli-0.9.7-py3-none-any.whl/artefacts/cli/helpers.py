import configparser
import os
from typing import Any, Optional

import requests

from artefacts.cli.constants import CONFIG_PATH, CONFIG_DIR


def get_conf_from_file():
    config = configparser.ConfigParser()
    if not os.path.isfile(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config["DEFAULT"] = {}
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    config.read(CONFIG_PATH)
    return config


def set_global_property(key: str, value: Any) -> None:
    config = get_conf_from_file()
    config.set("global", key, value)
    with open(CONFIG_PATH, "w") as f:
        config.write(f)


def get_global_property(key: str, default: Optional[Any] = None) -> Optional[Any]:
    config = get_conf_from_file()
    return config.get("global", key, fallback=default)


def get_artefacts_api_url(project_profile):
    return os.environ.get(
        "ARTEFACTS_API_URL",
        project_profile.get(
            "ApiUrl",
            "https://app.artefacts.com/api",
        ),
    )


def add_key_to_conf(project_name, api_key):
    config = get_conf_from_file()
    config[project_name] = {"ApiKey": api_key}
    with open(CONFIG_PATH, "w") as f:
        config.write(f)


def endpoint_exists(url: str) -> bool:
    """
    Simplistic confirmation of the existance of an endpoint.

    Under discussion: Use of HEAD verbs, etc.
    """
    access_test = requests.get(url)
    return access_test.status_code < 400
