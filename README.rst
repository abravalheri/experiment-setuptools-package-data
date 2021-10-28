Experiment
==========

This repository corresponds to the code used in an experiment to verify the
behaviour of the configuration of setuptools_, specifically the ``package_data``
and ``include_package_data`` fields.

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


Results
=======

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


We can derive a logic expression for this table using a 3-variable `Karnaugh
maps`_ for each one of the types of distributions. According to the notation:

:a: ``setup.cfg`` contains ``include_package_data=True``
:b: ``setup.cfg`` contains ``package_data`` and it is correctly set to add the "data files"
:c: ``MANIFEST.in`` exists and includes the "data files"
:w: "data files" included in the wheel distribution
:s: "data files" included in the sdist distribution


.. code-block:: python

    w = b or (a and c)
    s = c or (not(a) and b)


Therefore we can conclude that:

- In wheels, "data files" will be included if ``package_data`` includes them
  **OR** ``include_package_data=True`` **AND** ``MANIFEST.in`` includes them.
- In sdists, "data files" will be includes if ``MANIFEST.in`` includes them
  **OR** ``include_package_data=False`` (or not present) **AND**
  ``package_data`` includes them.


.. note:: The expression "data files" is used in a loose sense, meaning
   everything that is not a Python file. In the experiment they correspond to
   ``.txt`` files.


.. _setuptools: https://setuptools.pypa.io/en/latest/userguide/declarative_config.html
.. _packaging tutorial: https://packaging.python.org/tutorials/packaging-projects/
.. _Karnaugh maps: https://en.wikipedia.org/wiki/Karnaugh_map
