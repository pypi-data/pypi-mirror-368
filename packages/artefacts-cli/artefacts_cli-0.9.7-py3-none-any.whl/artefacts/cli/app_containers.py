import os
from pathlib import Path
from typing import Optional

import click

from c2d.core import Converter

from artefacts.cli.constants import DEFAULT_API_URL
from artefacts.cli.core import CodeEnvironment
from artefacts.cli.i18n import localise
from artefacts.cli.utils import config_validation, read_config
from artefacts.cli.containers.utils import ContainerMgr


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def containers(ctx: click.Context, debug: bool):
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@containers.command()
@click.option(
    "--path",
    default=".",
    help=localise(
        "[Deprecated since 0.8.0; please see --root] Path to the root of the project."
    ),
)
@click.option(
    "--root",
    default=".",
    help=localise("Path to the root of the project."),
)
@click.option(
    "--dockerfile",
    default="Dockerfile",
    help=localise(
        "Path to a custom Dockerfile. Defaults to Dockerfile under `path` (see option of the same name)."
    ),
)
@click.option(
    "--name",
    required=False,
    help=localise(
        "[Deprecated since 0.8.0; not used and will disappear after 0.8.0] Name for the generated image"
    ),
)
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help=localise(
        "Path to the Artefacts configuration file. It defaults to `./artefacts.yaml`"
    ),
)
@click.option(
    "--only",
    required=False,
    type=Optional[list],
    default=None,
    help=localise(
        "Optional list of job names to process. The default is to process all jobs."
    ),
)
@click.pass_context
def build(
    ctx: click.Context,
    path: str,
    root: str,
    dockerfile: str,
    name: str,
    config: str,
    only: Optional[list] = None,
) -> list:
    try:
        artefacts_config = read_config(config)
    except FileNotFoundError:
        raise click.ClickException(
            localise(
                "Project config file not found: {config}. Please provide an Artefacts configuration file to proceed (running `artefacts init` allows to generate one).".format(
                    config=config
                )
            )
        )
    prefix = artefacts_config["project"].strip().lower()
    dockerfiles = []
    if os.path.exists(dockerfile):
        if only:
            jobs = only
        else:
            jobs = artefacts_config["jobs"]
        for job_name in jobs:
            dockerfiles.append(
                dict(
                    path=root,
                    dockerfile=dockerfile,
                    name=f"{prefix}/{job_name.strip().lower()}",
                )
            )
    elif dockerfile != "Dockerfile" and not os.path.exists(dockerfile):
        # The user asks explicitly for using a specific Dockerfile, so fast fail if we cannot find it
        raise click.ClickException(
            localise(
                "Dockerfile `{dockerfile}` not found. Please ensure the file exits. Automatic Dockerfile generation may also work by dropping the --dockerfile option.".format(
                    dockerfile=dockerfile
                )
            )
        )
    else:
        # The split on `prefix` is to ensure there is no slash (project names are org/project) confusing the path across supported OS.
        dest_root = (
            Path.home()
            / Path(".artefacts")
            / Path("projects")
            / Path(*(prefix.split("/")))
            / Path("containers")
        )
        if not dest_root.exists():
            click.echo(
                localise(
                    "No {dockerfile} found here. Let's generate one per scenario based on artefacts.yaml. They will be available under the `{dest_root}` folder and used from there.".format(
                        dockerfile=dockerfile, dest_root=dest_root
                    )
                )
            )
        # No condition on generating the Dockerfiles as:
        #   - Fast
        #   - We consider entirely managed, so any manual change should be ignored.
        scenarios = Converter().process(config, as_text=False)
        for idx, df in enumerate(scenarios.values()):
            job_name = df.job_name.strip().lower()
            if only and job_name not in only:
                continue
            dest = dest_root / Path(job_name)
            dest.mkdir(parents=True, exist_ok=True)
            _dockerfile = os.path.join(dest, "Dockerfile")
            df.dump(_dockerfile)
            click.echo(
                f"[{job_name}] "
                + localise(
                    "Using generated Dockerfile at: {dockerfile}".format(
                        dockerfile=_dockerfile
                    )
                )
            )
            dockerfiles.append(
                dict(
                    path=root,
                    dockerfile=_dockerfile,
                    name=f"{prefix}/{job_name}",
                )
            )
    handler = ContainerMgr()
    images = []
    if len(dockerfiles) > 0:
        for specs in dockerfiles:
            # No condition on building the images, as relatively fast when already exists, and straightforward logic.
            image, _ = handler.build(**specs)
            images.append(image)
    else:
        click.echo(localise("No Dockerfile, nothing to do."))
    return images


@containers.command()
@click.argument("image_name", metavar=localise("IMAGE_NAME"))
@click.pass_context
def check(ctx: click.Context, image_name: str):
    if image_name is None:
        image_name = "artefacts"
    handler = ContainerMgr()
    result = handler.check(image_name)
    if ctx.parent is None:
        # Print only if the command is called directly.
        print(
            localise("Container image {name} exists and ready to use.").format(
                name=image_name
            )
        )
    return result


@containers.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("jobname", metavar=localise("JOBNAME"))
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help=localise(
        "Path to the Artefacts configuration file. It defaults to `./artefacts.yaml`"
    ),
)
@click.option(
    "--with-gui",
    "with_gui",
    default=False,
    help=localise(
        "Show any GUI if any is created by the test runs. By default, UI elements are run but hidden---only test logs are returned. Please note GUI often assume an X11 environment, typically with Qt, so this may not work without a appropriate environment."
    ),
)
# Not ready, placeholder for the introduction of Podman
# @click.option(
#     "--backend",
#     help="Container backend to use, mostly useful if you are using several at the same time. When this option is not specified, Artefacts will try to automatically detect available backends, with a preference for Docker if found. The `--engine-args` allows to pass engine arguments like `--gpu` for Docker, etc.",
# )
@click.argument("engine-args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(
    ctx: click.Context,
    jobname: str,
    config: str,
    with_gui: bool,
    #    backend: str,
    engine_args: tuple,
):
    # Workaround for job names coming after engine arguments
    #    Idea: Job names do not start with hyphens.
    if jobname.startswith("-") and engine_args is not None:
        _fix = list(engine_args)
        _fix.insert(0, jobname)
        jobname = _fix.pop()
        engine_args = tuple(_fix)

    try:
        artefacts_config = read_config(config)
    except FileNotFoundError:
        raise click.ClickException(
            localise("Project config file not found: {config}".format(config=config))
        )
    project = artefacts_config["project"]
    handler = ContainerMgr()
    code_env = CodeEnvironment()
    params = dict(
        image=f"{project.strip().lower()}/{jobname}",
        project=project,
        jobname=jobname,
        with_gui=with_gui,
        # Hidden settings primarily useful to Artefacts developers
        api_url=os.environ.get("ARTEFACTS_API_URL", DEFAULT_API_URL),
        api_key=os.environ.get("ARTEFACTS_KEY", None),
        engine_args=list(engine_args),
        code_state=code_env.get_state(),
        code_reference=code_env.get_reference(),
    )
    container, logs = handler.run(**params)
    if container:
        print(
            localise(
                "Container run complete: Container Id for inspection: {container_id}".format(
                    container_id=container["Id"]
                )
            )
        )
    else:
        print(localise("Package run failed:"))
        for entry in logs:
            print("\t- " + entry)
