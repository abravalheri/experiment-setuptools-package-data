Experiment
==========

This repository corresponds to the code used in an experiment to verify the
behaviour of the configuration of setuptools_, specifically the ``package_data``
and ``include_package_data`` fields.

The folder ``base`` contains a dummy Python package structure based on the
`packaging tutorial`_, with some "data files" [#datafiles]_ added::

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

.. [#datafiles] The expression "data files" is used in a loose sense, meaning
   everything that is not a Python file. In the experiment they correspond to
   ``.txt`` files.

The ``test.py`` script will create different versions of
this base structure.
Then it will try different combinations of configurations for
``include_package_data`` (``True``/not present),
``exclude_package_data`` (present/not present),
``package_data`` (present/not present) and
``MANIFEST.in`` (present/not present).

When present ``package_data`` and ``exclude_package_data``
will correspond to a ``setup.cfg`` section::

    [options.<<package_data OR exclude_package_data>>]
    * = *.txt, sub-dir/*.txt

When present, ``MANIFEST.in`` file will have the following contents::

    global-include *.py *.txt
    global-exclude *.py[cod]

To run the test file, you will need to make sure your system has the ``tar``
and ``unzip`` commands available, and that a virtualenv was created with Python 3.8::

    $ which unzip
    $ which tar
    $ virtualenv -p py38 .venv
    $ source .venv/bin/activate
    $ pip install -U pip -r requirements.txt
    $ rm results.txt
    $ python test.py | tee results.txt


Results
=======

The following table summarises the results (empty cells mean that the
configuration is not present):

+------------------------+------------------------+----------------+---------------+----------------------+
|                        |                        |                |               | Are ``*.txt`` files  |
|                        |                        |                |               | in the distribution? |
|                        |                        |                |               +------------+---------+
| include_package_data   | exclude_package_data   | package_data   | MANIFEST.in   | wheel      | sdist   |
+========================+========================+================+===============+============+=========+
|                        |                        |                |               | No         | No      |
+------------------------+------------------------+----------------+---------------+------------+---------+
|                        |                        |                | Yes           | No         | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
|                        |                        | Yes            |               | Yes        | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
|                        |                        | Yes            | Yes           | Yes        | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
|                        | Yes                    |                |               | No         | No      |
+------------------------+------------------------+----------------+---------------+------------+---------+
|                        | Yes                    |                | Yes           | No         | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
|                        | Yes                    | Yes            |               | No         | No      |
+------------------------+------------------------+----------------+---------------+------------+---------+
|                        | Yes                    | Yes            | Yes           | No         | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   |                        |                |               | No         | No      |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   |                        |                | Yes           | Yes        | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   |                        | Yes            |               | Yes        | No      |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   |                        | Yes            | Yes           | Yes        | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   | Yes                    |                |               | No         | No      |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   | Yes                    |                | Yes           | No         | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   | Yes                    | Yes            |               | No         | No      |
+------------------------+------------------------+----------------+---------------+------------+---------+
| True                   | Yes                    | Yes            | Yes           | No         | Yes     |
+------------------------+------------------------+----------------+---------------+------------+---------+


The complete experiment log can be found in the ``results.txt`` file, and the
data corresponding to the table above in the ``results.json`` data.

We can derive a logic expression for this table using `Karnaugh maps`_ or the
`Quine-McCluskey algorithm`_ for each one of the types of distributions.

According to the notation:

:i: ``setup.cfg`` contains ``include_package_data=True``
:e: ``setup.cfg`` contains ``exclude_package_data`` and it is set to remove ``*.txt`` files
:p: ``setup.cfg`` contains ``package_data`` and it is set to include ``*.txt`` files
:m: ``MANIFEST.in`` exists and includes the ``*.txt`` files
:w: ``*.txt`` included in the wheel distribution
:s: ``*.txt`` included in the sdist distribution

:x': the negated form of ``x`` - ``x' = not(x)``
:x.y: logical ``and`` between ``x`` and ``y``
:x+y: logical ``or`` between ``x`` and ``y``

.. code-block:: haskell

    w = i.e'.m + e'.p  -- Which can be simplified => e' . (i.m + p)
    s = i'.e'.p + m    -- Which can be simplified => m + p.(i + e)'


Conclusion
==========

- In wheels:

  - ``exclude_package_data`` will **ALWAYS** prevent "data files" from being included in the distribution;
  - after considering that, "data files" will be included in the distribution if:

    - ``package_data`` lists them **OR**
    - ``include_package_data=True`` **AND** ``MANIFEST.in`` includes them.

- In sdists, "data files" will be included in the distribution if:

  - ``MANIFEST.in`` includes them **OR**
  - ``include_package_data=False`` (or not present)
    **AND** ``package_data`` lists them
    **AND** ``exclude_package_data`` does not list them


Please notice this considers the extreme case, when the data files are placed
inside directories that are not valid Python packages (e.g. missing
``__init__.py`` files or whose names are not valid python identifiers) [#doc1]_.
Also have in mind that "data files" outside the package directory are no longer
allowed [#doc2]_.

.. [#doc1] https://setuptools.pypa.io/en/latest/userguide/datafiles.html
.. [#doc2] https://setuptools.pypa.io/en/latest/userguide/datafiles.html#non-package-data-files


Reproducibility
===============

For maximum reproducibility the versions of the build requirements
are pinned in the ``pyproject.toml`` file. You can edit that file to try the
test with different versions.

The experiment was created and executed on Ubuntu 18.04.5 LTS with Python 3.8.0.


Final Notes
===========

Please notice that, as any work, the experiment presented here is subject to
errors. If you notice anything wrong, please go ahead open an issue or pull
request. Any review is appreciated.


.. _setuptools: https://setuptools.pypa.io/en/latest/userguide/declarative_config.html
.. _packaging tutorial: https://packaging.python.org/tutorials/packaging-projects/
.. _Karnaugh maps: https://en.wikipedia.org/wiki/Karnaugh_map
.. _Quine-McCluskey algorithm: https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm
