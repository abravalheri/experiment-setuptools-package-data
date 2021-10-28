Description
===========

This is an experiment to verify the behaviour of the configuration of
setuptools, specifically the ``package_data`` and ``include_package_data``
fields.

The folder ``base`` contains a dummy Python package structure based on the
`packaging tutorial`_, with some ``.txt`` files added::

    base
    ├── LICENSE
    ├── README.md
    ├── pyproject.toml
    ├── setup.cfg
    └── src
        └── example_package
            ├── __init__.py
            ├── data
            ├── data.txt
            ├── example.py
            └── sub-dir
                └── other.txt

The ``test.py`` script will create different versions of
this base structure.
Then it will try different combinations of configurations for
``include_package_data`` (``True``/``False``), ``package_data`` (present/not
present) and ``MANIFEST.in`` (present/not present).

When present ``package_data`` will correspond to the following ``setup.cfg``
section::

    [options.package_data]
    * = *.txt, sub-dir/*.txt

When present, ``MANIFEST.in`` file will have the following contents::

    global-include *.py *.txt
    global-exclude *.py[cod]

To run the test file a virtualenv was created with Python 3.8::

    $ virtualenv -p py38 .venv
    $ source .venv/bin/activate
    $ pip install -U pip build
    $ python test.py


The following table summarises the results (that can be found in the
``results.txt`` file):

+----------------------+--------------+-------------+---------------------------+
| include_package_data | package_data | MANIFEST.in | Are ``*.txt`` included?   |
+======================+==============+=============+============+==============+
| ``False``            | No           | No          | wheel: No  | sdist: No    |
+----------------------+--------------+-------------+------------+--------------+
| ``False``            | No           | Yes         | wheel: No  | sdist: Yes   |
+----------------------+--------------+-------------+------------+--------------+
| ``False``            | Yes          | No          | wheel: Yes | sdist: Yes   |
+----------------------+--------------+-------------+------------+--------------+
| ``False``            | Yes          | Yes         | wheel: Yes | sdist: Yes   |
+----------------------+--------------+-------------+------------+--------------+
| ``True``             | No           | No          | wheel: No  | sdist: No    |
+----------------------+--------------+-------------+------------+--------------+
| ``True``             | No           | Yes         | wheel: Yes | sdist: Yes   |
+----------------------+--------------+-------------+------------+--------------+
| ``True``             | Yes          | No          | wheel: Yes | sdist: No    |
+----------------------+--------------+-------------+------------+--------------+
| ``True``             | Yes          | Yes         | wheel: Yes | sdist: Yes   |
+----------------------+--------------+-------------+------------+--------------+


.. _packaging tutorial: https://packaging.python.org/tutorials/packaging-projects/
