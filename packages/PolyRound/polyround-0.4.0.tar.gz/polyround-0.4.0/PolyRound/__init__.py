"""
PolyRound package metadata
--------------------------

* Uses the modern ``importlib.metadata`` API instead of the soon-to-be-removed
  ``pkg_resources``.
* Falls back to the ``importlib_metadata`` back-port on Python < 3.8.
* Keeps the old safety check that raises when a *different* installed
  PolyRound shadows the source tree you are running from.
"""

from __future__ import annotations

import os
import pathlib
from typing import TYPE_CHECKING

try:  # Python ≥ 3.8
    from importlib.metadata import version, PackageNotFoundError, distribution
except ImportError:  # pragma: no cover – only hit on Python < 3.8
    from importlib_metadata import (  # type: ignore
        version,
        PackageNotFoundError,
        distribution,
    )

_PROJECT = "PolyRound"
__version__ = "0.4.0"

try:

    # ── Is the file we’re executing inside the distribution we just looked up? ──
    dist_root = pathlib.Path(distribution(_PROJECT).locate_file("")).resolve()
    here = pathlib.Path(__file__).resolve()

    # On Windows we have to normalise case to match pkg_resources' behaviour
    if os.name == "nt":
        dist_root = pathlib.Path(os.path.normcase(dist_root))
        here = pathlib.Path(os.path.normcase(here))

    if not str(here).startswith(str(dist_root)):
        # A *different* PolyRound is installed somewhere on sys.path
        raise PackageNotFoundError

except PackageNotFoundError:
    __version__ = "Please install this project with using pip or pyproject.toml"

__author__ = "Axel Theorell, Johann Fredrik Jadebeck"

if TYPE_CHECKING:  # silence “unused” warnings in static analysers
    reveal_type(__version__)  # noqa: T201

