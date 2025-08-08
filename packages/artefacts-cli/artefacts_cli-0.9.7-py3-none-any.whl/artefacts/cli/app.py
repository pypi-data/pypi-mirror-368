import json
import os
import random
import sys
import tarfile
import tempfile
import time
from typing import Optional
from urllib.parse import urlparse
import webbrowser

import yaml
import click
import requests
from pathlib import Path
from gitignore_parser import parse_gitignore

from artefacts.cli import (
    init_job,
    generate_scenarios,
    localise,
    logger,
    AuthenticationError,
    __version__,
)
from artefacts.cli import app_containers as containers
from artefacts.cli.config import APIConf
from artefacts.cli.constants import (
    DEPRECATED_FRAMEWORKS,
    SUPPORTED_FRAMEWORKS,
    CONFIG_PATH,
)
from artefacts.cli.core import CodeEnvironment
from artefacts.cli.helpers import (
    add_key_to_conf,
    endpoint_exists,
    get_conf_from_file,
    get_artefacts_api_url,
)
from artefacts.cli.utils import (
    add_output_from_default,
    config_validation,
    ClickNetWatch,
    read_config,
)


@click.group()
def config():
    return


@config.command()
def path():
    """
    Get the configuration file path
    """
    click.echo(CONFIG_PATH)


@config.command()
@click.argument("project_name", metavar=localise("PROJECT_NAME"))
def add(project_name):
    """
    Set configuration for PROJECT_NAME
    """
    config = get_conf_from_file()
    if project_name in config:
        profile = config[project_name]
    else:
        profile = {}

    api_url = get_artefacts_api_url(profile)
    dashboard_url = api_url.split("/api")[0]

    settings_page_url = f"{dashboard_url}/{project_name}/settings"
    click.echo(
        localise("Opening the project settings page: {url}").format(
            url=settings_page_url
        )
    )

    if endpoint_exists(settings_page_url):
        # Check if running on WSL
        if "WSLENV" in os.environ:
            os.system(f'cmd.exe /C start "" {settings_page_url} 2>/dev/null')
        else:
            webbrowser.open(settings_page_url)

        api_key = click.prompt(
            localise("Please enter your API KEY for {project}").format(
                project=project_name
            ),
            type=str,
            hide_input=True,
        )
        add_key_to_conf(project_name, api_key)
        click.echo(localise("API KEY saved for {project}").format(project=project_name))
        if click.confirm(
            localise(
                "Would you like to download a pregenerated artefacts.yaml file? This will overwrite any existing config file in the current directory."
            )
        ):
            config_file_name = "artefacts.yaml"
            config_file_url = f"{api_url}/{project_name}/{config_file_name}"
            # Get credentials only now, as API key set just before.
            api_conf = APIConf(project_name, __version__)
            config_response = api_conf.read("url", config_file_url)
            if config_response.status_code == 200:
                with open(config_file_name, "wb") as f:
                    f.write(config_response.content)
            else:
                click.echo(
                    localise(
                        "We encountered a problem in getting the generated configuration file. Please consider downloading it from the project page on the dashboard at {url}. Sorry for the inconvenience."
                    ).format(url=settings_page_url)
                )
                logger.debug(
                    localise(
                        "If you are using an alternative server, please also consider checking the value of ARTEFACTS_API_URL in your environment."
                    )
                )
    else:
        click.echo(
            localise(
                "Our apologies: The project page does not seem available at the moment. If `{project_name}` is correct, please try again later.".format(
                    project_name=project_name
                )
            )
        )
        click.echo(
            localise(
                "If you are using an alternative server, please also consider checking the value of ARTEFACTS_API_URL in your environment."
            )
        )
    return


@config.command()
@click.argument("project_name", metavar=localise("PROJECT_NAME"))
def delete(project_name):
    """
    Delete configuration for PROJECT_NAME
    """
    config = get_conf_from_file()
    config.remove_section(project_name)
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
    click.echo(localise("{project} config removed").format(project=project_name))


@click.command()
@click.argument("project_name", metavar=localise("PROJECT_NAME"))
def hello(project_name):
    """Show message to confirm credentials allow access to PROJECT_NAME"""
    api_conf = APIConf(project_name, __version__)
    response = api_conf.read("url", f"{api_conf.api_url}/{project_name}/info")
    if response.status_code == 200:
        result = response.json()
        click.echo(
            "Hello " + click.style(f"{result['name']}@{result['framework']}", fg="blue")
        )
    else:
        result = response.json()
        raise click.ClickException(
            localise("Error getting project info: {message}").format(
                message=result["message"]
            )
        )


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("jobname", metavar=localise("JOBNAME"))
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help=localise("Artefacts configuration file."),
)
@click.option(
    "--dryrun",
    is_flag=True,
    default=False,
    help=localise("Run with no tracking nor test execution"),
)
@click.option(
    "--nosim",
    is_flag=True,
    default=False,
    help=localise("Skip configuring a simulator resource provided by Artefacts"),
)
@click.option(
    "--noupload",
    is_flag=True,
    default=False,
    help=localise(
        "Do not upload to Artefacts files generated during a run (e.g. rosbags)"
    ),
)
@click.option(
    "--noisolation",
    is_flag=True,
    default=False,
    help=localise(
        "Break the 'middleware network' isolation between the test suite and the host (in ROS2: --disable-isolation flag). Primarily for debugging"
    ),
)
@click.option(
    "--description",
    default=None,
    help=localise("Optional description for this run"),
)
@click.option(
    "--skip-validation",
    is_flag=True,
    default=False,
    is_eager=True,  # Necessary for callbacks to see it.
    help=localise(
        "Skip configuration validation, so that unsupported settings can be tried out, e.g. non-ROS settings or simulators like SAPIEN."
    ),
)
@click.option(
    "--in-container",
    is_flag=True,
    default=False,
    help=localise(
        '[Experimental] Run the job inside a package container. The container image is build if it does not exist yet, with default name as "artefacts" (please use --with-image to override the image name). This option overrides (for now) --dryrun, --nosim, --noisolation and --description.'
    ),
)
@click.option(
    "--dockerfile",
    default="Dockerfile",
    help=localise(
        "[Experimental] Path to a custom Dockerfile. Defaults to Dockerfile in the run directory. This flag is only used together with `--in-container`"
    ),
)
@click.option(
    "--with-image",
    default=None,
    help=localise(
        "[Deprecated and unused from 0.8.0; Image names are now internally managed] Run the job using the image name passed here. Only used when running with --in-container set."
    ),
)
@click.option(
    "--no-rebuild",
    is_flag=True,
    default=False,
    help=localise(
        "[Experimental] Override the default behaviour to always rebuild the container image (as we assume incremental testing)."
    ),
)
@click.option(
    "--with-gui",
    is_flag=True,
    default=False,
    help=localise(
        "Show any GUI if any is created by the test runs. By default, UI elements are run but hidden---only test logs are returned. Please note GUI often assume X11 (e.g. ROS), typically with Qt, so this may not work without a appropriate environment."
    ),
)
@click.argument("container-engine-args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(
    ctx: click.Context,
    config,
    jobname,
    dryrun,
    nosim,
    noupload,
    noisolation,
    description="",
    skip_validation=False,
    in_container: bool = False,
    dockerfile: str = "Dockerfile",
    with_image: str = "artefacts",
    no_rebuild: bool = False,
    with_gui: bool = False,
    container_engine_args: Optional[tuple] = None,
):
    """
    Run JOBNAME locally

    * Directly in the shell by default.
    * Inside a packaged container when using the --in-container option.

    In container mode:
    * Images are built automatically if missing.
    * Currently 1 image per job found in artefacts.yaml.
    * Images are rebuilt at each run (relatively fast when no change).
    * `dockerfile` allows to specify an alternative Dockerfile.
    """
    # Workaround for job names coming after engine arguments
    #    Idea: Job names do not start with hyphens.
    if jobname.startswith("-") and container_engine_args is not None:
        _fix = list(container_engine_args)
        _fix.insert(0, jobname)
        jobname = _fix.pop()
        container_engine_args = tuple(_fix)

    artefacts_conf = read_config(config)
    project_id = artefacts_conf["project"]

    if in_container:
        click.echo("#" * 80)
        click.echo(f"# Job {jobname}".ljust(79, " ") + "#")
        click.echo("#" * 80)
        click.echo(f"[{jobname}] " + localise("Checking container image"))
        if not no_rebuild:
            images = ctx.invoke(
                containers.build,
                root=".",
                dockerfile=dockerfile,
                only=[jobname],
            )
            if images and len(images) == 1:
                click.echo(f"[{jobname}] " + localise("Container image ready"))
            else:
                click.echo(
                    f"[{jobname}] " + localise("Unable to find the generated image")
                )
                raise click.Abort()
        click.echo(f"[{jobname}] " + localise("Run in container"))
        return ctx.invoke(
            containers.run,
            jobname=jobname,
            config=config,
            with_gui=with_gui,
            engine_args=container_engine_args,
        )

    api_conf = APIConf(project_id, __version__, jobname)
    click.echo(f"[{jobname}] " + localise("Starting tests"))
    if jobname not in artefacts_conf["jobs"]:
        click.secho(
            f"[{jobname}] " + localise("Error: Job name not defined"),
            err=True,
            bold=True,
        )
        raise click.Abort()
    jobconf = artefacts_conf["jobs"][jobname]
    job_type = jobconf.get("type", "test")
    if job_type not in ["test"]:
        click.echo(
            f"[{jobname}] "
            + localise("Job type not supported: {jt}").format(jt=job_type)
        )
        return

    framework = jobconf["runtime"].get("framework", None)

    # migrate deprecated framework names
    if framework in DEPRECATED_FRAMEWORKS.keys():
        migrated_framework = DEPRECATED_FRAMEWORKS[framework]
        click.echo(
            f"[{jobname}] "
            + localise(
                "The selected framework '{framework}' is deprecated. Using '{alt}' instead."
            ).format(framework=framework, alt=migrated_framework)
        )
        framework = migrated_framework

    if framework not in SUPPORTED_FRAMEWORKS:
        click.echo(
            f"[{jobname}] "
            + localise(
                "WARNING: framework: '{framework}' is not officially supported. Attempting run."
            ).format(framework=framework)
        )

    batch_index = os.environ.get("AWS_BATCH_JOB_ARRAY_INDEX", None)
    if batch_index is not None:
        batch_index = int(batch_index)
        click.echo(
            f"[{jobname}] "
            + localise("AWS BATCH ARRAY DETECTED, batch_index={index}").format(
                index=batch_index
            )
        )
    scenarios, first = generate_scenarios(jobconf, batch_index)
    code_env = CodeEnvironment()
    context = {
        "ref": code_env.get_reference(),
        "commit": code_env.get_state(),
    }
    context["description"] = description
    try:
        job = init_job(
            project_id,
            api_conf,
            jobname,
            jobconf,
            dryrun,
            nosim,
            noupload,
            noisolation,
            context,
            first,
            len(scenarios),
        )
    except AuthenticationError:
        click.secho(
            f"[{jobname}] "
            + localise(
                "Unable to authenticate (Stage: Job initialisation), please check your project name and API key"
            ),
            err=True,
            bold=True,
        )
        raise click.Abort()

    job_success = True
    for scenario_n, scenario in enumerate(scenarios):
        click.echo(
            f"[{jobname}] "
            + localise("Starting scenario {sid}/{num}: {name}").format(
                sid=scenario_n + 1, num=len(scenarios), name=scenario["name"]
            )
        )
        try:
            run = job.new_run(scenario)
        except AuthenticationError:
            click.secho(
                f"[{jobname}] "
                + localise(
                    "Unable to authenticate (Stage: Job run), please check your project name and API key"
                ),
                err=True,
                bold=True,
            )
            raise click.Abort()
        if framework is not None and framework.startswith("ros2:"):
            from artefacts.cli.ros2 import run_ros2_tests
            from artefacts.cli.utils_ros import get_TestSuite_error_result

            if "ros_testfile" not in run.params:
                click.secho(
                    f"[{jobname}] "
                    + localise("Test launch file not specified for ros2 project"),
                    err=True,
                    bold=True,
                )
                result = get_TestSuite_error_result(
                    scenario["name"],
                    localise("launch_test file not specified error"),
                    localise(
                        "Please specify a `ros_testfile` in the artefacts.yaml scenario configuration."
                    ),
                )
                run.log_tests_results([result], False)
                run.stop()
                job.update(last_run_success=False)
                continue
            if dryrun:
                click.echo(f"[{jobname}] " + localise("Performing dry run"))
                results, success = {}, True
            else:
                try:
                    results, success = run_ros2_tests(run)
                except Exception as e:
                    run.stop()
                    job.update(last_run_success=False)
                    job.log_tests_result(False)
                    click.secho(e, bold=True, err=True)
                    click.secho(
                        f"[{jobname}] "
                        + localise("Artefacts failed to execute the tests"),
                        err=True,
                        bold=True,
                    )
                    continue
            if success is None:
                result = get_TestSuite_error_result(
                    scenario["name"],
                    localise("ROS2 environment error"),
                    localise(
                        "Not able to execute tests. Make sure that ROS2 is sourced and that your launch file syntax is correct."
                    ),
                )
                run.log_tests_results([result], False)
                run.stop()
                job.update(last_run_success=False)
                job.log_tests_result(job_success)
                click.secho(
                    f"[{jobname}] "
                    + localise(
                        "Not able to execute tests. Make sure that ROS2 is sourced and that your launch file syntax is correct."
                    ),
                    err=True,
                    bold=True,
                )
                continue
            if not success:
                job_success = False
        else:
            from artefacts.cli.other import run_other_tests

            if "run" not in run.params:
                click.secho(
                    f"[{jobname}] "
                    + localise("run command not specified for scenario"),
                    err=True,
                    bold=True,
                )
                run.stop()
                job.update(last_run_success=False)
                job.log_tests_result(False)
                continue
            if dryrun:
                click.echo(f"[{jobname}] " + localise("Performing dry run"))
                results, success = {}, True
            else:
                results, success = run_other_tests(run)
            if not success:
                job_success = False
            if type(run.params.get("metrics", [])) is str:
                run.log_metrics()

        # Add for upload any default output generated by the run
        add_output_from_default(run)

        run.stop()
        job.log_tests_result(job_success)
        job.update(last_run_success=run.success)
    click.echo(f"[{jobname}] " + localise("Done"))
    time.sleep(random.random() * 1)


@click.command()
@click.option(
    "--config",
    callback=config_validation,
    default="artefacts.yaml",
    help=localise("Artefacts configuration file."),
)
@click.option(
    "--description",
    default=None,
    help=localise("Optional description for this run"),
)
@click.option(
    "--skip-validation",
    is_flag=True,
    default=False,
    is_eager=True,  # Necessary for callbacks to see it.
    help=localise(
        "Skip configuration validation, so that unsupported settings can be tried out, e.g. non-ROS settings or simulators like SAPIEN."
    ),
)
@click.argument("jobname", metavar=localise("JOBNAME"))
def run_remote(config, description, jobname, skip_validation=False):
    """
    Run JOBNAME in the cloud by packaging local sources.
    if a `.artefactsignore` file is present, it will be used to exclude files from the source package.

    This command requires to have a linked GitHub repository
    """
    try:
        artefacts_conf = read_config(config)
    except FileNotFoundError:
        raise click.ClickException(
            localise("Project config file not found: {config}").format(config=config)
        )
    project_id = artefacts_conf["project"]
    api_conf = APIConf(project_id, __version__)
    project_folder = os.path.dirname(os.path.abspath(config))
    dashboard_url = urlparse(api_conf.api_url)
    dashboard_url = f"{dashboard_url.scheme}://{dashboard_url.netloc}/{project_id}"

    try:
        artefacts_conf["jobs"][jobname]
    except KeyError:
        raise click.ClickException(
            localise("Can't find a job named '{jobname}' in config '{config}'").format(
                jobname=jobname, config=config
            )
        )

    # Mutate job and then keep only the selected job in the config
    run_config = artefacts_conf.copy()
    job = artefacts_conf["jobs"][jobname]

    # Use the same logic as `run` for expanding scenarios based on array params
    job["scenarios"]["settings"], _ = generate_scenarios(job, None)

    run_config["jobs"] = {jobname: job}
    if "on" in run_config:
        del run_config["on"]

    click.echo(localise("Packaging source..."))

    with tempfile.NamedTemporaryFile(
        prefix=project_id.split("/")[-1], suffix=".tgz", delete=True
    ) as temp_file:
        # get list of patterns to be ignored in .artefactsignore
        ignore_file = Path(project_folder) / Path(".artefactsignore")
        try:
            ignore_matches = parse_gitignore(ignore_file)
        except FileNotFoundError:
            ignore_matches = lambda x: False  # noqa: E731
        with tarfile.open(fileobj=temp_file, mode="w:gz") as tar_file:
            for root, dirs, files in os.walk(project_folder):
                for file in files:
                    absolute_path = os.path.join(root, file)
                    relative_path = os.path.relpath(absolute_path, project_folder)
                    # ignore .git folder
                    if relative_path.startswith(".git/"):
                        continue
                    # ignore paths in ignored_paths
                    if ignore_matches(absolute_path):
                        continue
                    # Prevent artefacts.yaml from being included twice
                    if os.path.basename(absolute_path) == "artefacts.yaml":
                        continue
                    tar_file.add(absolute_path, arcname=relative_path, recursive=False)
            # Write the modified config file to a temp file and add it
            with tempfile.NamedTemporaryFile("w") as tf:
                yaml.dump(run_config, tf)
                tar_file.add(tf.name, arcname="artefacts.yaml", recursive=False)

        temp_file.flush()
        temp_file.seek(0)

        # Request signed upload URLs
        # TODO Horrible approach, but the endpoint is neither CRUD nor REST, etc.
        #      So the idea to remain horrible and change this soon.
        upload_urls_response = api_conf.direct("post")(
            f"{api_conf.api_url}/{project_id}/create_remote_job",
            json={
                "jobname": jobname,
                "params": json.dumps(job),
                "timeout": 3000,
            },
        )

        if not upload_urls_response.ok:
            try:
                result = upload_urls_response.json()
            except requests.exceptions.JSONDecodeError:
                raise click.ClickException(
                    localise(
                        "Apologies, problem in interacting with the Artefacts backend: {status_code} {reason}. Response text: {detail}."
                    ).format(
                        status_code=upload_urls_response.status_code,
                        reason=upload_urls_response.reason,
                        detail=upload_urls_response.text,
                    )
                )

            if (
                upload_urls_response.status_code == 403
                and result["message"] == "Not allowed"
            ):
                raise click.ClickException(
                    localise(
                        "Missing access! Please make sure your API key is added at {url}/settings"
                    ).format(url=dashboard_url)
                )

            if upload_urls_response.status_code == 402:
                raise click.ClickException(
                    localise(
                        "Billing issue, please go to {url}/settings to correct: {error}"
                    ).format(url=dashboard_url, error=result["error"])
                )

            if "message" in result:
                raise click.ClickException(
                    localise("Error getting project info: {message}").format(
                        message=result["message"]
                    )
                )
            elif "error" in result:
                raise click.ClickException(
                    localise("Error getting project info: {message}").format(
                        message=result["error"]
                    )
                )
            else:
                raise click.ClickException(
                    localise(
                        "Error getting project info: {status_code} {reason}. Response text: {detail}."
                    ).format(
                        status_code=upload_urls_response.status_code,
                        reason=upload_urls_response.reason,
                        detail=upload_urls_response.text,
                    )
                )

        upload_urls = upload_urls_response.json()["upload_urls"]
        url = ""
        # github specific logic should later be moved to the github action, and instead support additional options or env variables for configuration for payload
        if description is None:
            if "GITHUB_RUN_ID" in os.environ:
                description = os.environ.get("GITHUB_WORKFLOW")
                url = f"{os.environ.get('GITHUB_SERVER_URL')}/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{os.environ.get('GITHUB_RUN_ID')}"
            else:
                description = localise("Testing local source")
        # Mock the necessary parts of the GitHub event
        code_env = CodeEnvironment()
        integration_payload = {
            "head_commit": {
                # shown on the dashboard in the job details
                "message": description,
                "url": url,
            },
            "repository": {
                # used by the container-builder for creating the ecr repo name
                "full_name": os.environ.get("GITHUB_REPOSITORY", project_id),
            },
            # special key to distinguish the valid GitHub payload from these fabricated ones
            "ref": os.environ.get("GITHUB_REF", code_env.get_reference()),
            "after": os.environ.get("GITHUB_SHA", code_env.get_state()),
        }

        artefacts_yaml = yaml.dump(run_config)
        integration_payload_json = json.dumps(integration_payload)
        uploads = [
            ("archive.tgz", temp_file, os.path.getsize(temp_file.name)),
            ("artefacts.yaml", artefacts_yaml, sys.getsizeof(artefacts_yaml)),
            (
                "integration_payload.json",
                integration_payload_json,
                sys.getsizeof(integration_payload_json),
            ),
        ]
        total_size = sum([f[2] for f in uploads])

        with click.progressbar(
            uploads,
            length=total_size,
            label=f"Uploading {total_size / 1024 / 1024:.2f} MB of source code",
            item_show_func=lambda x: x and x[0],
        ) as bar:
            with ClickNetWatch(bar):
                for filename, file, _ in bar:
                    response = api_conf.upload(
                        upload_urls[filename]["url"],
                        upload_urls[filename]["fields"],
                        (filename, file),
                    )
                    if not response.ok:
                        raise click.ClickException(
                            f"Failed to upload {filename}: {response.text}"
                        )

        click.echo(
            localise(
                "Uploading complete! The new job will show up shortly at {url}"
            ).format(url=dashboard_url)
        )


@click.group()
@click.version_option(version=__version__)
def artefacts():
    """A command line tool to interface with ARTEFACTS"""
    pass


artefacts.add_command(config)
artefacts.add_command(hello)
artefacts.add_command(run)
artefacts.add_command(run_remote)
artefacts.add_command(containers.containers)


if __name__ == "__main__":
    artefacts()
