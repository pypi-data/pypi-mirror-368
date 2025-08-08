import sys

from collections.abc import Iterator
from typing import Any, Tuple

from artefacts.cli import errors, localise
from artefacts.cli.containers import CMgr
from artefacts.cli.logger import logger


class ContainerMgr:
    SUPPORTED_PRIORITISED_ENGINES = {
        1: "docker",
        # 2: "podman",
    }

    def __init__(self):
        self.logger = logger
        self.mgr = self._configure()
        if self.mgr is None:
            self.logger.error(
                localise(
                    "Failed to find supported container stack. Please install and start one of {engines}, with default settings (custom sockets not supported at this stage)".format(
                        engines=list(self.SUPPORTED_PRIORITISED_ENGINES.values())
                    )
                )
            )
            sys.exit(errors.CONTAINER_ENGINE_NOT_FOUND)

    def _configure(self) -> CMgr:
        manager = None
        for idx in sorted(self.SUPPORTED_PRIORITISED_ENGINES):
            engine = self.SUPPORTED_PRIORITISED_ENGINES[idx]
            try:
                handler = getattr(self, f"_configure_{engine}")
                manager = handler()
            except AttributeError:
                self.logger.warning(
                    localise(
                        "Tried to detect an unsupported engine: {engine}. WIP? Ignore and continue.".format(
                            engine=engine
                        )
                    )
                )
            except Exception as e:
                self.logger.warning(
                    localise(
                        "Problem in detecting {engine} ({message}) Ignore and continue.".format(
                            engine=engine, message=e
                        )
                    )
                )
            if manager is not None:
                break
        return manager

    def _configure_docker(self):
        from artefacts.cli.containers.docker_cm import DockerManager

        return DockerManager()

    # def _configure_podman(self):
    #     from artefacts.cli.containers import podman
    #     return PodmanManager()

    def build(self, **kwargs) -> Tuple[str, Iterator]:
        return self.mgr.build(**kwargs)

    def check(self, image: str) -> bool:
        return self.mgr.check(image)

    def run(self, **kwargs) -> Tuple[Any, Iterator]:
        return self.mgr.run(**kwargs)
