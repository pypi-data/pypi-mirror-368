import gettext
import importlib.resources
import os
import locale
import sys


# Ensure env var requirements for gettext are fulfilled
if sys.platform.startswith("win"):
    if os.getenv("LANG") is None:
        lang, _ = locale.getdefaultlocale()
        os.environ["LANG"] = lang


# Get path to the locale directory
try:
    _localedir = importlib.resources.files("artefacts.cli") / "locales"
except FileNotFoundError:
    #
    # Encountered in our trials with Python 3.10 and 3.11, so fallback to pkg_resources
    #
    # pkg_resources is removed from setuptools in Python 3.12. From there, importlib works.
    #
    from pkg_resources import resource_filename

    _localedir = str(resource_filename("artefacts.cli", "locales"))


# Setup the GNU gettext API
gettext.bindtextdomain("artefacts", _localedir)
gettext.textdomain("artefacts")


# Expose for other modules to import
localise = gettext.gettext
