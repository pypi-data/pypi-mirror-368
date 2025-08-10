===================
pytest-awaiting-fix
===================

.. image:: https://img.shields.io/pypi/v/pytest-awaiting-fix.svg
    :target: https://pypi.org/project/pytest-awaiting-fix
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-awaiting-fix.svg
    :target: https://pypi.org/project/pytest-awaiting-fix
    :alt: Python versions

.. image:: https://github.com/kiebak3r/pytest-awaiting-fix/actions/workflows/main.yml/badge.svg
    :target: https://github.com/kiebak3r/pytest-awaiting-fix/actions/workflows/main.yml
    :alt: See Build Status on GitHub Actions

A simple plugin to use with pytest which helps retain traceability between automated tests and Jira statuses.
When a test is tagged with the @pytest.mark.awaiting_fix('test') decorator it will automatically skip this test
and comment which disabled automation tests are associated to the ticket

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Installation
------------

You can install "pytest-awaiting-fix" via `pip`_ from `PyPI`_::

    $ pip install pytest-awaiting-fix


Usage
-----
Once the package has been installed:
Tag any tests with the provided decorator pytest.mark.awaiting_fix('test-123')


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-awaiting-fix" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: https://opensource.org/licenses/MIT
.. _`BSD-3`: https://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: https://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: https://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/kiebak3r/pytest-awaiting-fix/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
