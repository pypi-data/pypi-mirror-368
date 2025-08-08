import getpass
import os
import platform
import subprocess
from typing import Optional


class CodeEnvironment:
    """
    A CodeEnvironment exposes helpers to learn about the source code where
    the CLI is executed. Typically it compiles information of interest from a
    Git repository or directory without version control.
    """

    # Current directory where the environment has been populated.
    _cwd: Optional[str] = None

    # Memo to keep track of whether the environment is a Git repo.
    _is_git_memo: Optional[bool] = None

    def __init__(self):
        self._cwd = os.getcwd()
        self._is_git_memo = self.is_git_repository()

    def is_git_repository(self) -> bool:
        """
        Check whether the runtime executes in a Git repository. The test
        relies on shelling out a command at this point.

        The result is memoised for future reference without expensive external
        command. The memo is updated each time the current working directory
        changes, to update whether we are still in a Git repo.
        """
        if self._cwd != os.getcwd() or not self._is_git_memo:
            try:
                result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"])
                self._is_git_memo = result.returncode == 0
                self._cwd = os.getcwd()
            except subprocess.CalledProcessError as e:
                raise Exception("Unable to interact with Git: {error}".format(error=e))
        return self._is_git_memo

    def get_git_revision_hash(self, short: bool = True) -> Optional[str]:
        if self.is_git_repository():
            try:
                h = (
                    subprocess.check_output(["git", "rev-parse", "HEAD"])
                    .decode("ascii")
                    .strip()
                )
                if short:
                    return h[:8]
                else:
                    return h
            except subprocess.CalledProcessError as e:
                raise Exception("Unable to interact with Git: {error}".format(error=e))
        else:
            return None

    def get_git_revision_branch(self) -> Optional[str]:
        if self.is_git_repository():
            try:
                return (
                    subprocess.check_output(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"]
                    )
                    .decode("ascii")
                    .strip()
                )
            except subprocess.CalledProcessError as e:
                raise Exception("Unable to interact with Git: {error}".format(error=e))
        else:
            return None

    def has_unstaged_changes(self) -> Optional[bool]:
        if self.is_git_repository():
            try:
                result = subprocess.run(["git", "diff-files", "--quiet"])
                return result.returncode != 0
            except subprocess.CalledProcessError as e:
                raise Exception(
                    "Unable to detect unstaged changes by interacting with Git: {error}".format(
                        error=e
                    )
                )
        else:
            return None

    def has_staged_changes(self) -> Optional[bool]:
        if self.is_git_repository():
            try:
                result = subprocess.run(
                    ["git", "diff-index", "--quiet", "--cached", "HEAD", "--"]
                )
                return result.returncode != 0
            except subprocess.CalledProcessError as e:
                raise Exception(
                    "Unable to detect staged changes by interacting with Git: {error}".format(
                        error=e
                    )
                )
        else:
            return None

    def has_untracked_changes(self) -> Optional[bool]:
        if self.is_git_repository():
            try:
                result = subprocess.run(
                    ["git", "ls-files", "--exclude-standard", "--others"],
                    capture_output=True,
                )
                return result.stdout is not None and len(result.stdout) > 0
            except subprocess.CalledProcessError as e:
                raise Exception(
                    "Unable to detect untracked changes by interacting with Git: {error}".format(
                        error=e
                    )
                )
        else:
            return None

    def get_state(self) -> str:
        if self.is_git_repository():
            suffix = ""
            if (
                self.has_untracked_changes()
                or self.has_staged_changes()
                or self.has_unstaged_changes()
            ):
                suffix = "~"
            return self.get_git_revision_hash(short=True) + suffix
        else:
            if "ARTEFACTS_CODE_STATE" in os.environ:
                # Special env var, typically used in CLI-managed containers.
                return os.environ["ARTEFACTS_CODE_STATE"]
            else:
                # We can certainly do better by watching the files declared
                # in artefacts.yaml, but left for later.
                return None

    def get_reference(self) -> Optional[str]:
        execution_context = getpass.getuser() + "@" + platform.node()
        if self.is_git_repository():
            return self.get_git_revision_branch() + "~" + execution_context
        else:
            if "ARTEFACTS_CODE_REFERENCE" in os.environ:
                # Special env var, typically used in CLI-managed containers.
                return os.environ["ARTEFACTS_CODE_REFERENCE"]
            else:
                return None
