from datetime import datetime, timezone
from functools import partial
from importlib.metadata import version, PackageNotFoundError
from types import FrameType
from typing import Optional
import copy
import glob
import json
import math
import os
import shutil
import signal
import sys
import textwrap

import click

from .config import APIConf
from .i18n import localise
from .parameters import iter_grid
from .logger import logger
from .utils import ClickNetWatch


try:
    __version__ = version("artefacts-cli")
except PackageNotFoundError:
    try:
        # Package is not installed, most likely dev/test mode
        from setuptools_scm import get_version

        __version__ = get_version()
    except Exception as e:
        logger.warning(
            localise(
                "Could not determine package version: {error_message}. Default to 0.0.0".format(
                    error_message=e
                )
            )
        )
        __version__ = "0.0.0"


class ArtefactsAPIError(Exception):
    """
    Tentative base error class for Artefacts API interactions
    """

    pass


class AuthenticationError(ArtefactsAPIError):
    """Raised when artefacts authentication failed"""

    pass


class Job:
    def __init__(
        self,
        project_id,
        api_conf: APIConf,
        jobname,
        jobconf,
        dryrun=False,
        nosim=False,
        noupload=False,
        noisolation=False,
        context=None,
        run_offset=0,
        n_subjobs=1,  # Total Number of Runs
    ):
        self.project_id = project_id
        self.job_id = os.environ.get("ARTEFACTS_JOB_ID", None)
        self.api_conf = api_conf
        self.start = datetime.now(timezone.utc).timestamp()
        self.uploads = {}
        self.jobname = jobname
        self.params = jobconf
        self.success = False
        self.n_runs = run_offset
        self.current_run = None
        self.dryrun = dryrun
        self.nosim = nosim
        self.noupload = noupload
        self.noisolation = noisolation
        self.context = context
        self.n_subjobs = n_subjobs

        if dryrun:
            self.job_id = "dryrun"
        if self.job_id is None:
            # Only create a new job if job_id is not specified
            data = {
                "project_id": self.project_id,
                "start": round(self.start),
                "status": "in progress",
                "params": json.dumps(self.params),
                "project": self.project_id,
                "jobname": self.jobname,
                "timeout": self.params.get("timeout", 5) * 60,
                "n_subjobs": self.n_subjobs,
            }
            if context is not None:
                data["message"] = context["description"]
                data["commit"] = context["commit"]
                data["ref"] = context["ref"]
            response = self.api_conf.create("job", data)
            if response.status_code != 200:
                if response.status_code == 403:
                    msg = response.json()["message"]
                    logger.warning(msg)
                    raise AuthenticationError(msg)
                logger.warning(
                    localise(
                        "Error on job creation: {status_code}".format(
                            status_code=response.status_code
                        )
                    )
                )
                logger.warning(response.text)
                raise ArtefactsAPIError(str(response.status_code))
            self.job_id = response.json()["job_id"]
        self.output_path = self.params.get("output_path", f"/tmp/{self.job_id}")
        os.makedirs(self.output_path, exist_ok=True)
        return

    def log_tests_result(self, success):
        self.success = success

    def update(self, last_run_success: bool) -> bool:
        end = datetime.now(timezone.utc).timestamp()
        if self.dryrun:
            return True
        # Log metadata
        data = {
            "project_id": self.project_id,
            "end": round(end),
            "duration": round(end - self.start),
            "success": last_run_success,
            "status": "finished",  # need to be determined based on all runs
        }
        response = self.api_conf.update("job", self.job_id, data)

        return response.status_code == 200

    def new_run(self, scenario):
        self.current_run = Run(self, scenario["name"], scenario, self.n_runs)
        self.n_runs += 1
        return self.current_run


class Run:
    def __init__(self, job: Job, name: str, params: dict, run_n: int):
        self.job = job
        self.start = datetime.now(timezone.utc).timestamp()
        self.uploads = {}
        self.scenario_name = name
        self.params = params
        self.metrics = {}
        self.run_n = run_n
        self.output_path = self.params.get(
            "output_path", f"{self.job.output_path}/{self.run_n}"
        )
        self.test_results = []
        self.success = False
        self.logger = logger
        os.makedirs(self.output_path, exist_ok=True)
        data = {
            "project_id": self.job.project_id,
            "job_id": job.job_id,
            "run_n": self.run_n,
            "start": round(self.start),
            "tests": [],
            "params": json.dumps(self.params),
            "scenario_name": self.scenario_name,
        }

        if self.job.dryrun:
            return

        response = self.job.api_conf.create("run", data)
        if response.status_code != 200:
            if response.status_code == 403:
                msg = response.json()["message"]
                self.logger.warning(msg)
                raise AuthenticationError(msg)
            self.logger.warning(
                localise(
                    "Error on scenario creation: {status_code}".format(
                        status_code=response.status_code
                    )
                )
            )
            self.logger.warning(response.text)
            raise ArtefactsAPIError(str(response.status_code))
        return

    def log_params(self, params):
        self.params = params

    def log_metric(self, name, value):
        self.metrics[name] = value

    def log_metrics(self):
        metrics = self.params.get("metrics", None)
        if type(metrics) is str:
            with open(f"{self.output_path}/{metrics}") as f:
                metric_values = json.load(f)
            for k, v in metric_values.items():
                self.log_metric(k, v)

    def log_post_process_metrics(self, post_process_folder):
        try:
            with open(f"{post_process_folder}/metrics.json") as f:
                metric_values = json.load(f)
            for k, v in metric_values.items():
                self.log_metric(k, v)
        except FileNotFoundError:
            # if the metrics.json file does not exist, do nothing
            pass

    def log_tests_results(self, test_results, success):
        self.test_results = test_results
        self.success = success

    def log_artifacts(self, output_path, prefix=None):
        """log all files within folder output_path"""

        def _get_filename(root_path, full_path):
            filename = full_path.split(f"{root_path}/")[-1]
            # print(root_path, full_path, filename)
            return filename

        files = [
            f
            for f in glob.glob(f"{output_path}/**", recursive=True)
            if "." in f and f[-1] != "/"
        ]
        # careful: glob with recursive sometimes returns non existent paths!
        # https://stackoverflow.com/questions/72366844/unexpected-result-with-recursive-glob-glob-using-pattern

        # update dictionary of uploads
        # key = filename: value = file path
        # Note: filename must not be empty string (happened when '.ros' in root path)
        if prefix is not None:
            self.uploads.update(
                {f"{prefix}/{_get_filename(output_path, f)}": f for f in files}
            )
        else:
            self.uploads.update(
                {
                    _get_filename(output_path, f): f
                    for f in files
                    if _get_filename(output_path, f) != ""
                }
            )

    def log_single_artifact(self, filename, prefix=None):
        """log a single file filename"""

        def _get_filename(path):
            return path.split("/")[-1]

        if prefix is not None:
            self.uploads.update({f"{prefix}/{_get_filename(filename)}": filename})
        else:
            self.uploads.update({_get_filename(filename): filename})

    def stop(self):
        end = datetime.now(timezone.utc).timestamp()

        if self.job.dryrun:
            return

        # Log metadata
        data = {
            "project_id": self.job.project_id,
            "job_id": self.job.job_id,
            "run_n": self.run_n,
            "start": math.floor(self.start),
            "params": json.dumps(self.params),
            "end": round(end),
            "duration": math.ceil(end - self.start),
            "tests": self.test_results,
            "success": self.success,
            "metrics": self.metrics,
            "scenario_name": self.scenario_name,
        }
        if not self.job.noupload:
            data["uploads"] = self.uploads

        response = self.job.api_conf.update("run", self.run_n, data)

        # use s3 presigned urls to upload the artifacts
        if self.job.noupload:
            print(
                localise(
                    "Files generated by the job are not uploaded to Artefacts, including the ones specified in output_dirs"
                )
            )
        else:
            upload_urls = response.json()["upload_urls"]
            total_size = sum(
                os.path.getsize(file_name) for file_name in self.uploads.values()
            )

            # Progress bar template
            # label, 2 spaces, width-wide bar, 2 spaces, 4 chars for %, 2 spaces, rest for file name
            label = f"Uploading {total_size / 1024 / 1024:.2f} MB of artifacts"
            terminal_width, _ = shutil.get_terminal_size()
            width = 30
            file_name_max = max([0, terminal_width - len(label) - width - 10])

            with click.progressbar(
                self.uploads.items(),
                length=total_size,
                label=label,
                item_show_func=lambda x: x
                and textwrap.shorten(x[0], width=file_name_max, placeholder="..."),
                show_eta=False,
                hidden=False,
                width=width,
            ) as bar:
                with ClickNetWatch(bar):
                    for filename, filepath in bar:
                        upload_info = upload_urls[filename]
                        try:
                            with open(filepath, "rb") as f:
                                self.job.api_conf.upload(
                                    upload_info["url"],
                                    upload_info["fields"],
                                    (filename, f),
                                )
                        except OverflowError:
                            self.logger.warning(
                                localise(
                                    "File too large: {filepath} could not be uploaded".format(
                                        filepath=filepath
                                    )
                                )
                            )
                        except Exception as e:
                            self.logger.warning(
                                localise(
                                    "Error uploading {filepath}: {error_message}, skipping".format(
                                        filepath=filepath, error_message=e
                                    )
                                )
                            )


def _sigint_handler(
    job: Job, sig: signal.Handlers, curr_stack_frame: Optional[FrameType]
):
    """
    Attempt to quickly "cancel" any existing job, and its current run.

    Cancellation tries to be quick by ensuring uploads are ignored.
    """
    if type(job) is Job:
        if job.current_run:
            if not job.noupload:
                job.current_run.uploads = {}
            job.current_run.stop()
        job.update(False)
    # Note click.Abort() works sometimes, but is ignored
    #   by some code that keeps looping. So we exit.
    sys.exit(0)


def init_job(
    project_id: str,
    api_conf: APIConf,
    jobname: str,
    jobconf: dict,
    dryrun: bool = False,
    nosim: bool = False,
    noupload: bool = False,
    noisolation: bool = False,
    context: Optional[dict] = None,
    run_offset=0,
    n_subjobs: int = 1,
):
    job = Job(
        project_id,
        api_conf,
        jobname,
        jobconf,
        dryrun,
        nosim,
        noupload,
        noisolation,
        context,
        run_offset,
        n_subjobs,
    )
    signal.signal(signal.SIGINT, partial(_sigint_handler, job))
    return job


def generate_scenarios(jobconf, scenario_n=None):
    """Create each scenario conf by:
    1. selecting only named scenario specified by scenario_n (for parallel processing)
    2. merging default values to each scenario
    3. generating parameter grids
    """
    scenarios = sorted(jobconf["scenarios"]["settings"], key=lambda x: x["name"])
    defaults = jobconf["scenarios"].get("defaults", {})
    first_scenario = 0
    last_scenario = None
    generated_scenarios = []
    for n, scenario_settings in enumerate(scenarios):
        if scenario_n is not None:
            if n == scenario_n:
                first_scenario = len(generated_scenarios)
            if n == scenario_n + 1:
                last_scenario = len(generated_scenarios)
        # add `settings` keys on top of `defaults` keys
        # (taking special care to merge the `params` keys)
        scenario = copy.deepcopy(defaults)  # deepcopy mandatory
        for k in scenario_settings.keys():
            # merge scenario dict values into default dict values
            if k == "params" or k == "launch_arguments":
                scenario[k] = {
                    **scenario.get(k, {}),
                    **scenario_settings[k],
                }
            else:
                # add all other keys (overwriting defaults if already present)
                scenario[k] = scenario_settings[k]

        # generate scenarios for each combination of parameter values (grid coverage)
        if "params" in scenario.keys():
            grid_values = iter_grid(scenario["params"])
            for value in grid_values:
                grid_scenario = scenario.copy()
                grid_scenario["params"] = value
                generated_scenarios.append(grid_scenario)

        else:
            generated_scenarios.append(scenario)
    return generated_scenarios[first_scenario:last_scenario], first_scenario
