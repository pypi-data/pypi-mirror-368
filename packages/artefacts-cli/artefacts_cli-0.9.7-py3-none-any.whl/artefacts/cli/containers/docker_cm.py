from collections.abc import Iterator
import json
import os
from pathlib import Path
import platform
from typing import Any, Optional, Tuple, Union
from uuid import uuid4

from artefacts.cli.constants import DEFAULT_API_URL
from artefacts.cli.containers import CMgr
from artefacts.cli.i18n import localise
from artefacts.cli.utils import ensure_available

ensure_available("docker")

# Note: E402 requires imports are at the top of the file.
#       Exceptions here as we dynamically get Docker.
import docker  # noqa: E402
from docker import APIClient  # noqa: E402

from artefacts.cli.containers.docker_utils import cli2sdk  # noqa: E402


class DockerManager(CMgr):
    def __init__(self):
        self.client = APIClient()

    def build(self, **kwargs) -> Tuple[str, Iterator]:
        kwargs["tag"] = kwargs.pop("name")
        # Ensure `path` is a string, the Docker package does not support pathlib.
        kwargs["path"] = str(kwargs.pop("path"))
        # Remove intermediate containers
        kwargs["rm"] = True
        logs = []
        img_id = None
        error = False
        for entry in self.client.build(**kwargs):
            line_data = [
                json.loads(v) for v in entry.decode("utf-8").split("\r\n") if len(v) > 0
            ]
            for data in line_data:
                if "stream" in data:
                    line = data["stream"].strip()
                    if not line.startswith("---") and len(line) > 0:
                        print(f"[{kwargs['tag'].split('/')[-1]}] {line}")
                        logs.append(line)
                elif "message" in data:
                    error = True
                    print(
                        f"[{kwargs['tag'].split('/')[-1]}] Error: {data['message'].strip()}"
                    )
                elif "aux" in data and "ID" in data["aux"]:
                    img_id = str(data["aux"]["ID"])
        if img_id is None and not error:
            img_id = str(self.client.inspect_image(kwargs["tag"])["Id"])
        return img_id, iter(logs)

    def check(
        self,
        image: str,
    ) -> bool:
        return len(self.client.images(name=image)) > 0

    def run(
        self,
        image: str,
        project: str,
        jobname: Optional[str] = None,
        artefacts_dir: Union[str, Path] = Path("~/.artefacts").expanduser(),
        api_url: str = DEFAULT_API_URL,
        api_key: Optional[str] = None,
        with_gui: bool = False,
        engine_args: Optional[list] = None,
        code_state: Optional[str] = None,
        code_reference: Optional[str] = None,
    ) -> Tuple[Any, Iterator]:
        """
        Run an application as an Artefacts-enabled container in a Docker engine
        """
        env = {
            "JOB_ID": str(uuid4()),
            "ARTEFACTS_JOB_NAME": jobname,
            "ARTEFACTS_API_URL": api_url,
        }
        if code_state:
            env["ARTEFACTS_CODE_STATE"] = code_state
        if code_reference:
            env["ARTEFACTS_CODE_REFERENCE"] = code_reference

        env["ARTEFACTS_KEY"] = api_key or self._get_artefacts_api_key(
            project, artefacts_dir
        )
        if env["ARTEFACTS_KEY"] is None:
            return None, iter(
                [
                    localise(
                        "Missing API key for the project. Does `{path}/config` exist and contain your key? Alternatively ARTEFACTS_KEY can be set with the key.".format(
                            path=artefacts_dir
                        )
                    )
                ]
            )
        try:
            if platform.system() in ["Darwin", "Windows"]:
                # Assume we run in Docker Desktop
                env["DISPLAY"] = "host.docker.internal:0"
            else:
                env["DISPLAY"] = os.environ.get("DISPLAY", ":0")

            if not with_gui:
                env["QT_QPA_PLATFORM"] = "offscreen"

            # Default configs
            host_conf = dict(
                network_mode="host",
            )

            container_conf = dict(
                image=image,
                environment=env,
                detach=False,
            )

            # Apply user config and overrides, if any
            if engine_args:
                option = None
                # Add a marker to detect end of args
                engine_args.append("--end--")
                for current in engine_args:
                    is_option = current.startswith("-")
                    if is_option and not option:
                        option = current.lstrip("-")
                        if "=" in option:
                            option, value = option.split("=")
                            cli2sdk(host_conf, container_conf, option, value)
                            option = None
                    elif not is_option and option:
                        cli2sdk(host_conf, container_conf, option, current)
                        option = None
                    elif is_option and option:
                        # Assuming detection of concatenated flags, all set.
                        for flag in str(option):
                            cli2sdk(host_conf, container_conf, flag, True)
                        if current != "--end--":
                            option = current

            # Final container config
            container_conf["host_config"] = self.client.create_host_config(**host_conf)

            try:
                container = self.client.create_container(**container_conf)
            except Exception as e:
                # SDK errors may have an explanation
                # E.g. in 7.1.0 https://github.com/docker/docker-py/blob/7.1.0/docker/errors.py#L53
                known = str(e)
                if known.endswith(")"):
                    # Error message: info ("explanation")
                    # We return explanation
                    detail = known[known.index("(") + 2 : -2]
                else:
                    # Error message: info
                    # We return info
                    detail = known[known.index(":") + 2 :]
                raise Exception(f"Invalid container configuration: {detail}")
            self.client.start(container=container.get("Id"))

            for entry in self.client.logs(container=container.get("Id"), stream=True):
                print(entry.decode("utf-8").strip())

            return container, iter([])
        except docker.errors.ImageNotFound:
            return None, iter(
                [
                    localise(
                        "Image {image} not found by Docker. Perhaps need to build first?".format(
                            image=image
                        )
                    )
                ]
            )
        except Exception as e:
            return None, iter(
                [
                    localise(
                        "Failed to run from {image}. All we know: {message}".format(
                            image=image, message=e
                        )
                    )
                ]
            )
