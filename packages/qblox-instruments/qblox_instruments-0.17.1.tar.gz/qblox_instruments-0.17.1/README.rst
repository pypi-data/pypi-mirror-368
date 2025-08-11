|
|

.. figure:: https://gitlab.com/qblox/packages/software/qblox_instruments/-/raw/main/docs/images/qblox_logo.svg
    :width: 400px
    :target: https://qblox.com
    :align: center
    :alt: Qblox

|
|

.. image:: https://readthedocs.com/projects/qblox-qblox-instruments/badge/?version=main
    :target: https://qblox-qblox-instruments.readthedocs-hosted.com/en/main

.. image:: https://gitlab.com/qblox/packages/software/qblox_instruments/badges/main/pipeline.svg
    :target: https://gitlab.com/qblox/packages/software/qblox_instruments/pipelines/

.. image:: https://gitlab.com/qblox/packages/software/qblox_instruments/badges/main/coverage.svg
    :target: https://gitlab.com/qblox/packages/software/qblox_instruments/pipelines/

.. image:: https://img.shields.io/pypi/v/qblox-instruments.svg
    :target: https://pypi.org/pypi/qblox-instruments

.. image:: https://img.shields.io/badge/License-BSD%204--Clause-blue.svg
    :target: https://gitlab.com/qblox/packages/software/qblox_instruments/-/blob/main/LICENSE

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff

|

############################
Welcome to Qblox Instruments
############################

| The Qblox instruments package contains everything to get started with Qblox instruments (i.e. Python drivers, `documentation and tutorials <https://qblox-qblox-instruments.readthedocs-hosted.com/en/main/>`_).
| For a detailed changelog check `HISTORY.rst <https://gitlab.com/qblox/packages/software/qblox_instruments/-/blob/main/HISTORY.rst>`__


####################
Compatibility Matrix
####################

.. list-table::
   :header-rows: 1

   * - qblox-instruments releases
     - Cluster firmware releases
   * - `0.17.0 <https://pypi.org/project/qblox-instruments/0.17.0/>`__
     - `0.12.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.12.0>`__
   * - `0.16.0 <https://pypi.org/project/qblox-instruments/0.16.0/>`__
     - `0.11.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.11.0>`__
   * - `0.15.0 <https://pypi.org/project/qblox-instruments/0.15.0/>`__
     - `0.10.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.10.0>`__
   * - `0.14.1 <https://pypi.org/project/qblox-instruments/0.14.1/>`__
     - `0.9.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.9.1>`__
   * - `0.14.0 <https://pypi.org/project/qblox-instruments/0.14.0/>`__
     - `0.9.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.9.0>`__
   * - `0.13.0 <https://pypi.org/project/qblox-instruments/0.13.0/>`__
     - `0.8.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.8.0>`__
   * - `0.12.0 <https://pypi.org/project/qblox-instruments/0.12.0/>`__
     - `0.7.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.7.0>`__
   * - `0.11.2 <https://pypi.org/project/qblox-instruments/0.11.2/>`__
     - `0.6.2 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.6.2>`__
   * - `0.11.1 <https://pypi.org/project/qblox-instruments/0.11.1/>`__
     - `0.6.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.6.1>`__
   * - `0.11.0 <https://pypi.org/project/qblox-instruments/0.11.0/>`__
     - `0.6.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.6.0>`__
   * - `0.10.1 <https://pypi.org/project/qblox-instruments/0.10.1/>`__
     - `0.5.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.5.1>`__
   * - `0.10.0 <https://pypi.org/project/qblox-instruments/0.10.0/>`__
     - `0.5.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.5.0>`__
   * - `0.9.0 <https://pypi.org/project/qblox-instruments/0.9.0/>`__
     - `0.4.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.4.0>`__
   * - `0.8.2 <https://pypi.org/project/qblox-instruments/0.8.2/>`__
     - `0.3.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.3.1>`__
   * - `0.8.1 <https://pypi.org/project/qblox-instruments/0.8.1/>`__
     - `0.3.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.3.0>`__
   * - `0.8.0 <https://pypi.org/project/qblox-instruments/0.8.0/>`__
     - `0.3.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.3.0>`__
   * - `0.7.1 <https://pypi.org/project/qblox-instruments/0.7.1/>`__
     - `0.2.3 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.3>`__
   * - `0.7.0 <https://pypi.org/project/qblox-instruments/0.7.0/>`__
     - `0.2.2 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.2>`__
   * - `0.6.1 <https://pypi.org/project/qblox-instruments/0.6.1/>`__
     - `0.2.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.1>`__
   * - `0.6.0 <https://pypi.org/project/qblox-instruments/0.6.0/>`__
     - `0.2.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.0>`__



----------------------------

| This software is free to use under the conditions specified in the `license <https://gitlab.com/qblox/packages/software/qblox_instruments/-/blob/main/LICENSE>`_.
| For more information, please contact `support@qblox.com <support@qblox.com>`_.

----------------------------
