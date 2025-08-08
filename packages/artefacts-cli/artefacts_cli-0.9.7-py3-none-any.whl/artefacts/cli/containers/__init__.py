from collections.abc import Iterator
import configparser
import os
from pathlib import Path
from typing import Any, Optional, Tuple, Union

from artefacts.cli.constants import DEFAULT_API_URL


class CMgr:
    def build(self, **kwargs) -> Tuple[str, Iterator]:
        """
        Returns the build image ID (e.g. sha256:abcdefghi)
        and an iterator over the build log entries.
        """
        raise NotImplementedError()

    def check(self, image: str) -> bool:
        """
        Checks whether a target image exists locally.
        """
        raise NotImplementedError()

    def run(
        self,
        image: str,
        project: str,
        jobname: Optional[str] = None,
        artefacts_dir: Union[str, Path] = Path("~/.artefacts").expanduser(),
        api_url: str = DEFAULT_API_URL,
        with_gui: bool = False,
    ) -> Tuple[Any, Iterator]:
        """
        Returns a container (Any type as depends on the framework)
        and an iterator over the container log entries.
        """
        raise NotImplementedError()

    def _get_artefacts_api_key(
        self, project: str, path: Union[str, Path] = Path("~/.artefacts").expanduser()
    ) -> Optional[str]:
        """
        Get any valid API key to embed in containers.

        1. Checks first from the ARTEFACTS_KEY environment variable.
        2. If `path` is not given, check from the default configuraiton file in the .artefacts folder.
        3. If `path` is given, check the file directly if a file, or check for a `config` file if a folder.

        When a config file is found, we get the API key for the `project`.

        `path` set to None is an error, and aborts execution.
        """
        if not path:
            raise Exception(
                "`path` must be a string, a Path object, or excluded from the kwargs"
            )
        if os.environ.get("ARTEFACTS_KEY", None):
            return os.environ["ARTEFACTS_KEY"]
        path = Path(path)  # Ensure we have a Path object
        config = configparser.ConfigParser()
        if path.is_dir():
            config.read(path / "config")
        else:
            config.read(path)
        try:
            return config[project].get("apikey")
        except KeyError:
            return None
