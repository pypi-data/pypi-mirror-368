RF Surveillance Central
=======================

.. start-badges see https://shields.io/badges and collection see https://github.com/inttter/md-badges

| |build| |release_version| |wheel|
| |docs| |pylint| |supported_versions|
| |ruff| |gh-lic| |commits_since_specific_tag_on_main|

Radio Frequency Surveillance Central
------------------------------------
Receive signal strength, samples and central frequency from different  **RF Surveillance central**
Process them and extract different meta data
Display the high power signal on the console and give a warning (beep) in case
any frequency exceed the desired power defined when the RF Central application starts ( command line input)
This application does not contain a Machine Learning Model.
Signal Meta Data Extraction is done by **RF Analysis Engine**

|rf_central|

| RF Central displaying radio frequency data; red data which exceed the power threshold

|rf_central_console|



Change Log
==========
 `Change Log <https://github.com/alanmehio/rf-surveillance-central/blob/main/CHANGELOG.rst>`_.

Quickstart
==========
| `Usage <https://github.com/alanmehio/rf-surveillance-central/blob/main/docs/source/contents/usage.rst>`_.

License
=======


* `GNU Affero General Public License v3.0`_


License
=======

* Free software: GNU Affero General Public License v3.0



.. LINKS

.. _GNU Affero General Public License v3.0: https://github.com/alanmehio/rf-surveillance-central/blob/main/LICENSE



.. BADGE ALIASES

.. Build Status
.. Github Actions: Test Workflow Status for specific branch <branch>

.. |build| image::  https://github.com/alanmehio/rf-surveillance-central/actions/workflows/ci_cd.yaml/badge.svg
    :alt: GitHub Workflow Status (branch)
    :target: https://github.com/alanmehio/rf-surveillance-central/actions


.. Documentation

.. |docs| image::  https://img.shields.io/readthedocs/rf-surveillance-central/latest?logo=readthedocs&logoColor=lightblue
    :alt: Read the Docs (version)
    :target: https://rf-surveillance-central.readthedocs.io/en/latest/

.. PyLint

.. |pylint| image:: https://img.shields.io/badge/linting-pylint-yellowgreen
    :target: https://github.com/pylint-dev/pylint

.. PyPI

.. |release_version| image:: https://img.shields.io/pypi/v/rfcentral
    :alt: Production Version
    :target: https://pypi.org/project/rfcentral/

.. |wheel| image:: https://img.shields.io/pypi/wheel/rfcentral?color=green&label=wheel
    :alt: PyPI - Wheel
    :target: https://pypi.org/project/rfcentral

.. |supported_versions| image:: https://img.shields.io/pypi/pyversions/rfcentral?color=blue&label=python&logo=python&logoColor=%23ccccff
    :alt: Supported Python versions
    :target: https://pypi.org/project/rfcentral

.. Github Releases & Tags

.. |commits_since_specific_tag_on_main| image:: https://img.shields.io/github/commits-since/alanmehio/rf-surveillance-central/1.0.0/main?color=blue&logo=github
    :alt: GitHub commits since tagged version (branch)
    :target: https://github.com/alanmehio/rf-surveillance-central/compare/1.0.0..main

.. |commits_since_latest_github_release| image:: https://img.shields.io/github/commits-since/alanmehio/rf-surveillance-central/latest?color=blue&logo=semver&sort=semver
    :alt: GitHub commits since latest release (by SemVer)

.. LICENSE (eg AGPL, MIT)
.. Github License

.. |gh-lic| image:: https://img.shields.io/badge/license-GNU_Affero-orange
    :alt: GitHub
    :target: https://github.com/alanmehio/rf-surveillance-central/blob/main/LICENSE


.. Ruff linter for Fast Python Linting

.. |ruff| image:: https://img.shields.io/badge/codestyle-ruff-000000.svg
    :alt: Ruff
    :target: https://docs.astral.sh/ruff/

.. Local linux command: CTRL+Shift+Alt+R key


.. Local Image as link

.. |rf_central| image:: https://raw.githubusercontent.com/alanmehio/rf-surveillance-central/main/media/rf-central.jpeg
    :alt: RF Surveillance Central(Server)

.. |rf_central_console| image:: https://raw.githubusercontent.com/alanmehio/rf-surveillance-central/main/media/screen/rf-central-console.gif
    :alt: RF Surveillance Central(Server) console output


