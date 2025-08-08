Pypjt - Python Project Template
===============================

Pypjt is a project to create python project template.

Docs: https://pypjt.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/v/pypjt.svg
   :target: https://pypi.org/project/pypjt/
   :alt: PyPI version

.. image:: https://static.pepy.tech/badge/pypjt
   :target: https://pepy.tech/projects/pypjt
   :alt: PyPI downloads

.. image:: https://github.com/sleeping-in-bed/pypjt/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/sleeping-in-bed/pypjt/actions/workflows/test.yml
   :alt: Test status

.. image:: https://codecov.io/github/sleeping-in-bed/pypjt/graph/badge.svg?token=HEIMHMX0PK
   :target: https://codecov.io/github/sleeping-in-bed/pypjt
   :alt: Codecov

Installation
------------

To install **pypjt**, use pip:

.. code-block:: console

   $ python -m pip install pypjt

Quickstart
----------

To get started, simply run:

.. code-block:: console

   $ pypjt

If running it as a script doesn't work, you can run it as a module instead:

.. code-block:: console

   $ python -m pypjt

It's safe to run—**it will not overwrite any existing directories**.

Once launched, you’ll be prompted to answer a few questions about the project you want to create.

The **project name** is the most important and required field.
You can leave the other fields empty or accept their default values.
All of these settings can be changed later in ``pyproject.toml`` or other configuration files.

After you’ve completed the prompts, your project will be generated
and saved under the current working directory.

Great! You can now start coding within the newly created folder,
or further customize the structure to fit your needs.
