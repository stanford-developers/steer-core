# SPDX-License-Identifier: AGPL-3.0-only

import os

from .DataManager import DataManager


def is_development() -> bool:
    """Check if running in development mode (local SQLite).

    Controlled by the ``OPENCELL_ENV`` environment variable:

    - ``development`` — local SQLite database via ``steer_opencell_data``,
      no login button, guest-only functionality. Use this when developing
      new cells locally before publishing via the CLI migration tool.
    - ``production`` (default) — REST API via ``steer_core.Data.DataManager``,
      requires ``API_URL`` env var. Full auth flow with Cognito.
    """
    return os.environ.get("OPENCELL_ENV", "production").lower() == "development"
