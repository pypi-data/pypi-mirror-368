from itertools import product
from typing import Iterable

# constants for internal temporary files

TMP_RUNTIME_PARAMS_YAML = "/tmp/runtime_params.yaml"
TMP_SCENARIO_PARAMS_YAML = "/tmp/scenario_params.yaml"
TMP_SCENARIO_PARAMS_JSON = "/tmp/scenario_params.json"


def iter_grid(grid_spec: dict) -> Iterable[dict]:
    """Iterate over the points defined by the `grid_spec`"""
    if not grid_spec:
        yield {}
    else:
        # Sort the keys of the dictionary, for reproducibility
        items = sorted(grid_spec.items())
        keys, values = zip(*items)
        # Make sure single values are converted to lists
        values = [x if type(x) is list else [x] for x in values]
        for v in product(*values):
            params = dict(zip(keys, v))
            yield params
