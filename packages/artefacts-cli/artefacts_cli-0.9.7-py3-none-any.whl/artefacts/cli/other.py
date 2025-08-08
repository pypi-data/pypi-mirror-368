import json
import yaml
import os
from .utils import run_and_save_logs
from .parameters import TMP_SCENARIO_PARAMS_YAML, TMP_SCENARIO_PARAMS_JSON


def generate_parameter_output(params: dict):
    """Store `params` in both json and yaml temporary files
    Note: fixed filenames will lead concurent executions to overwrite each other
    """
    with open(TMP_SCENARIO_PARAMS_JSON, "w") as f:
        json.dump(params, f)
    with open(TMP_SCENARIO_PARAMS_YAML, "w") as f:
        yaml.dump(params, f)


def run_other_tests(run):
    """Note: parameter names will be set as environment variables
    (must be letters, numbers and underscores), and saved into yaml and json files
    """
    scenario = run.params
    if "params" in scenario:
        generate_parameter_output(scenario["params"])
    full_env = {**os.environ, **scenario.get("params", {})}
    full_env["ARTEFACTS_SCENARIO_PARAMS_FILE"] = TMP_SCENARIO_PARAMS_YAML

    command = scenario["run"]
    run_and_save_logs(
        command,
        shell=True,
        env={k: str(v) for k, v in full_env.items()},
        output_path=os.path.join(run.output_path, "test_process_log.txt"),
    )

    results = []
    success = True
    run.log_artifacts(run.output_path)

    for output in scenario.get("output_dirs", []):
        run.log_artifacts(output)

    run.log_tests_results(results, success)
    return results, success
