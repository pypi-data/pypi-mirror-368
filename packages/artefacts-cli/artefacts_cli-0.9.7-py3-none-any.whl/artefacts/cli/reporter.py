from datetime import datetime, timedelta, timezone
import errno
import os
from pathlib import Path
import traceback
from typing import Any

from .constants import CONFIG_DIR
from .helpers import get_global_property
from .i18n import localise
from .logger import logger


def _cleanup(
    config_dir: str = CONFIG_DIR,
    log_retention_max_days: int = int(get_global_property("log_retention_max_days", 7)),
    log_retention_max_files: int = int(
        get_global_property("log_retention_max_files", 3)
    ),
):
    """
    Internal cleanup routine to remove old logs mostly dedicated to CLI developers

    Old logs means how old their last modification is, as tracked by st_mtime.

    Logs are kept up to `log_retention_max_files` many files, and up to
    `log_retention_max_days` many days. These two parameters have default values
    and can be overriden in the `global` section of the `.artefacts/config` file.
    """
    log_retention_reference = int(
        (datetime.now() - timedelta(days=log_retention_max_days)).timestamp()
    )
    # Using os.walk as Path.walk appears only in Python 3.12
    for root, dirs, files in os.walk(Path(config_dir) / "projects"):
        for org in dirs:
            for project in (Path(root) / org).iterdir():
                log_dir = Path(root) / org / project / "logs"
                if log_dir.exists():
                    logs = sorted(
                        os.listdir(log_dir),
                        key=lambda f: (log_dir / f).stat().st_mtime,
                        reverse=True,
                    )
                    for idx, log in enumerate(
                        map(lambda path: log_dir / path, logs), 1
                    ):
                        if (
                            idx > log_retention_max_files
                            or int(log.stat().st_mtime) <= log_retention_reference
                        ):
                            log.unlink()


#
# On load, cleanup any log "too old"
#
_cleanup()


def _report_dir(project: str) -> Path:
    try:
        org, pname = project.split("/")
        path = Path(CONFIG_DIR) / "projects" / org / pname / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path
    except (AttributeError, ValueError):
        raise Exception(
            localise("Invalid project name: {project}".format(project=project))
        )
    except TypeError:
        raise Exception(
            localise(
                "Invalid value found, either: project={project}, or .artefacts path={home}".format(
                    project=project, home=CONFIG_DIR
                )
            )
        )


def fail_safe_report(
    project: str,
    message: Any,
    stack: traceback.StackSummary = None,
    top_error: Exception = None,
    local_error: Exception = None,
    locals_dict: dict = None,
) -> None:
    """
    Report of data to ~/.artefacts/projects/org/project/reports

    1. Fail safe: It must not hinder the UX
    2. Best effort: If we can successfully log, great. if not see 1.
    """
    try:
        with open(
            _report_dir(project) / f"{int(datetime.now(timezone.utc).timestamp())}.err",
            "a",
        ) as f:
            f.write("Stacktrace\n")
            if stack:
                f.write("".join(traceback.format_list(stack)))
            f.write("\n")

            f.write("Message\n")
            f.write("\t{m}\n".format(m=message.replace("\n", "\n\t")))
            f.write("\n")

            f.write("Top Error\n")
            if top_error:
                try:
                    _t = type(top_error)
                    if len(str(top_error)) == 0:
                        top_error = "This top error has an empty string message (not None)---this message is *not* the original value."
                    f.write(f"\t{_t}: {top_error}\n")
                except Exception as err:
                    f.write(
                        f"\tA top error object exists but could not be serialised. Ignoring (err={err})\n"
                    )
            else:
                f.write("\tNo object\n")
            f.write("\n")

            f.write("Local Error\n")
            if local_error:
                try:
                    f.write(f"\t{type(local_error)}: {local_error}\n")
                except Exception as err:
                    f.write(
                        f"\tA local error object exists but could not be serialised. Ignoring (err={err})\n"
                    )
            else:
                f.write("\tNo object\n")
            f.write("\n")

            f.write("Locals\n")
            if locals_dict:
                try:
                    for k, v in locals_dict.items():
                        if v and len(str(v)) == 0:
                            v = "This local variable has an empty string value (not None)---this message is *not* the original value."
                        f.write(
                            "\t- {key}={value}\n".format(
                                key=k, value=str(v).replace("\n", "\n\t")
                            )
                        )
                except Exception as err:
                    f.write(
                        f"\tA locals dict exists, but unable to serialise it. Ignoring (err={err})\n"
                    )
            else:
                f.write("\tNo data\n")
    except OSError as e:
        if e.errno == errno.ENOSPC:
            logger.warning(
                localise(
                    "No space available on device. Detailed error log not storable."
                )
            )
    except:  # noqa: E722
        # Failsafe: Reporting must not interfere with UX
        # TODO Improve so we can guarantee feedback
        pass
