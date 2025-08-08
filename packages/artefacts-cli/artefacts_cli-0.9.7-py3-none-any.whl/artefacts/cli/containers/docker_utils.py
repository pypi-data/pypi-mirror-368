from typing import Any

import docker  # noqa: E402

from artefacts.cli.i18n import localise


def _identity(v: Any) -> Any:
    return v


def _make_gpu_device_request(gpus: str) -> list:
    """
    Code based on Docker documented use, not on the source code.

    https://docs.docker.com/reference/cli/docker/container/run/#gpus
    """
    if '"device=' in gpus:
        try:
            # Docs: `--gpus '"device=1,2"'`
            _g = gpus.strip('"')
            # There must be 2 double quotes.
            assert len(_g) == len(gpus) - 2
            ids = sorted(_g[_g.index("=") + 1 :].split(","))
        except Exception as e:
            raise Exception(
                localise(
                    'Invalid GPU device for Docker: {g} ({e}). Accepted device formats are all, device=1 and "device=1,2" (with a list of devices, quotes must be included'.format(
                        g=gpus, e=e
                    )
                )
            )
    elif "device=" in gpus:
        # Docs: `--gpus device=1` or `--gpus device=GPU-3faa8-219`
        if "," in gpus:
            raise Exception(
                localise(
                    'Invalid GPU device for Docker: {g}. List of devices must be double-quoted. Accepted device formats are all, device=1 and "device=1,2" (with a list of devices, quotes must be included'.format(
                        g=gpus,
                    )
                )
            )
        ids = [gpus.split("=")[-1]]
    elif "all" == gpus:
        ids = [gpus]
    else:
        raise Exception(
            localise(
                'Invalid GPU device for Docker: {g}. Accepted device formats are all, device=1 and "device=1,2" (with a list of devices, quotes must be included'.format(
                    g=gpus
                )
            )
        )
    return [docker.types.DeviceRequest(device_ids=ids, capabilities=[["gpu"]])]


_cli_sdk_option_map = {
    "net": {
        "t": "host",
        "o": "network_mode",
    },
    "gpus": {
        "t": "host",
        "o": "device_requests",
        "f": _make_gpu_device_request,
    },
    "t": {
        "t": "container",
        "o": "tty",
    },
    "i": {
        "t": "container",
        "o": "stdin_open",
    },
    "tty": {
        "t": "container",
    },
    "interactive": {
        "t": "container",
        "o": "stdin_open",
    },
}


def cli2sdk(host: dict, container: dict, option: str, value: Any) -> None:
    """
    `host` and `container` are IO map arguments.
    """
    method = _cli_sdk_option_map.get(option)
    if method:
        if method["t"] == "host":
            host[method.get("o") or option] = (method.get("f") or _identity)(value)
        elif method["t"] == "container":
            container[method.get("o") or option] = (method.get("f") or _identity)(value)
    else:
        # Based on current knowledge of the SDK, it seems
        # we can opt for the host config as default.
        host[option] = value
