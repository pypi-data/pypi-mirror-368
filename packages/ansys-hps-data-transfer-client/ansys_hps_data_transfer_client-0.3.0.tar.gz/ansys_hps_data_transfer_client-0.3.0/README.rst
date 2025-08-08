PyHPS Data Transfer
==========================
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |ruff|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-hps-data-transfer-client?logo=pypi
   :target: https://pypi.org/project/ansys-hps-data-transfer-client/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-hps-data-transfer-client.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-hps-data-transfer-client
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/hps-data-transfer-client/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pyhps-data-transfer
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/hps-data-transfer-client/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pyhps-data-transfer/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


Overview
--------

PyHPS Data Transfer is a Python client library for the Ansys HPC Platform Services (HPS) data transfer service.

.. contribute_start

Installation
^^^^^^^^^^^^
You can use `pip <https://pypi.org/project/pip/>`_ to install PyHPS Data Transfer in user mode:

.. code:: bash

    pip install ansys-hps-data-transfer-client

To install the latest development version from the GitHub repository, run these commands:

.. code:: bash

    git clone https://github.com/ansys/pyhps-data-transfer/
    cd pyhps-data-transfer
    pip install -e .

For more information, see `Getting started`_.

Basic usage
^^^^^^^^^^^

The following sections show how to import PyHPS Data Transfer and use some basic capabilities.

Request access token
~~~~~~~~~~~~~~~~~~~~

The client library requires an access token to connect to the HPS Data Transfer service.

.. code:: python

    from ansys.hps.data_transfer.client.authenticate import authenticate

    auth_url = "https://localhost:8443/hps/auth/realms/rep"

    token = authenticate(username="repadmin", password="repadmin", verify=False, url=auth_url)
    token = token.get("access_token", None)

Connect to data transfer service client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After obtaining the access token, you can connect to the data transfer service client:

.. code:: python

    from ansys.hps.data_transfer.client import Client    # Import the Client class
    dt_url = f"https://localhost:8443/hps/dt/api/v1"
    client = Client()   # Create a client object
    client.binary_config.update(verbosity=3, debug=True, insecure=True, token=token, data_transfer_url=dt_url, log=True)
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)


For comprehensive usage information, see `Examples`_.

Documentation and issues
^^^^^^^^^^^^^^^^^^^^^^^^
Documentation for the latest stable release of PyHPS Data Transfer is hosted at `PyHPS Data Transfer documentation`_.

In the upper right corner of the documentation's title bar, there is an option for switching from
viewing the documentation for the latest stable release to viewing the documentation for the
development version or previously released versions.

On the `PyHPS Data Transfer Issues <https://github.com/ansys/pyhps-data-transfer/issues>`_ page,
you can create issues to report bugs and request new features. On the `PyHPS Data Transfer Discussions
<https://github.com/ansys/pyhps-data-transfer/projects>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <mailto:pyansys.core@ansys.com>`_.


.. LINKS AND REFERENCES
.. _Getting Started: https://data-transfer.hps.docs.pyansys.com/version/stable/getting_started/index.html
.. _Examples: https://data-transfer.hps.docs.pyansys.com/version/stable/examples/index.html
.. _PyHPS Data Transfer documentation: https://data-transfer.hps.docs.pyansys.com/
