Installation
============

From source (development)
-------------------------

.. code-block:: bash

   git clone https://github.com/nicholas9182/steer-core.git
   cd steer-core
   pip install -e ".[dev]"

From PyPI
---------

.. code-block:: bash

   pip install steer-core

Requirements
------------

- Python >= 3.10
- See ``pyproject.toml`` for the full dependency list.

Environment Variables
---------------------

.. list-table::
   :header-rows: 1

   * - Variable
     - Required
     - Default
     - Description
   * - ``OPENCELL_ENV``
     - No
     - ``production``
     - ``development`` = local SQLite, ``production`` = REST API
   * - ``API_URL``
     - In production
     - —
     - Base URL of the REST API
   * - ``API_TIMEOUT``
     - No
     - ``30``
     - HTTP request timeout in seconds
