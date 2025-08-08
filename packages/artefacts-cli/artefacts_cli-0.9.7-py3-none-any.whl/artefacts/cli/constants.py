import os


DEFAULT_API_URL = "https://app.artefacts.com/api"

SUPPORTED_FRAMEWORKS = [
    "ros2:iron",
    "ros2:humble",
    "ros2:galactic",
    "maniskill:challenge2022",
    "None",
    "none",
    "null",
    None,
]

DEPRECATED_FRAMEWORKS = {
    "ros2:0": "ros2:galactic",
}

HOME = os.path.expanduser("~")
CONFIG_DIR = f"{HOME}/.artefacts"
CONFIG_PATH = f"{CONFIG_DIR}/config"
