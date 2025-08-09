.. image:: https://gitlab.com/dpizetta/pqwidget/-/raw/develop/docs/images/scientific-spinbox-cover-resized.png

scientific-spinbox
==================

**ScientificSpinbox** is a Qt Widget based on QDoubleSpinBox that
enables users to insert and manipulate physical quantities naturally.

.. image:: https://badge.fury.io/py/scientific-spinbox.svg
  :target: https://badge.fury.io/py/scientific-spinbox
  :alt: PyPI - Release Version

.. image:: https://img.shields.io/pypi/dm/scientific-spinbox
  :alt: PyPI - Downloads

.. image:: https://img.shields.io/pypi/pyversions/scientific-spinbox
  :alt: PyPI - Python Version

.. image:: https://readthedocs.org/projects/pqwidget/badge/?version=latest
  :target: https://pqwidget.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://gitlab.com/dpizetta/pqwidget/badges/develop/coverage.svg?job=py310-test-supported
  :target: https://gitlab.com/dpizetta/pqwidget/badges/develop/coverage.svg?job=py310-test-supported
  :alt: Test job status

.. image:: https://dl.circleci.com/status-badge/img/circleci/6bTayJ8Qf8kDpwpwnEfEDY/9sGuva55EzD1oAP3e5ANMW/tree/main.svg?style=svg&circle-token=CCIPRJ_CBbDxYBL13frPixBp899VK_ec6483668be1ff9486b6e1b01327fb8e95fc4593
  :target: https://dl.circleci.com/status-badge/redirect/circleci/6bTayJ8Qf8kDpwpwnEfEDY/9sGuva55EzD1oAP3e5ANMW/tree/main
  :alt: CircleCI build status

Getting started
===============

This widget makes it easier for people from STEM (Science, Technology, 
Engineering, and Mathematics) fields to interact with
numeric inputs in a natural way with units and converstion between them, 
also allowing the usage of scientific notation and adding resources that highly
improve the user experience.

The backend that deals with units and their conversion can be set up/integrated
separately, but it is currently making use of the package `Pint <https://pint.readthedocs.io/en/stable/>`_.

This package also makes use of `QtPy <https://pypi.org/project/QtPy/>`_, 
an abstraction layer for PyQt/PySide, making it simple to interchange 
between those bindings and their versions.

Its main application is to be integrated with the `PyMR framework <https://doi.org/10.11606/T.76.2019.tde-06052019-103714>`_
to provide a better user interface when setting physical values
for Magnetic Resonance experiments, where it is necessary to use,
for example, frequency, degrees, voltage, and current.

Despite the specific use, we provided this package as an independent
one so more people can benefit from it. The final intention is to
integrate this special QSpinBox into the Qt/PySide/PyQt package,
if they have interest in the future.

Examples
========
Below is an example of a ScientificSpinBox widget used to insert values with units of time.
The **allowed units** are ``s``, ``ms`` and ``us`` and the **base unit** is ``ms``. The widget enables
the user to use scientific notation, edit the values using step up/step down and insert any desired number of decimal places.

Altough the user can play around with the units, the ``baseValue`` will always be the input converted to the **base unit**.

.. figure:: https://gitlab.com/dpizetta/pqwidget/-/raw/develop/docs/images/test-scientificspinbox.gif
  :alt: Testing ScientificSpinBox
  :align: center

  Example of a ScientificSpinBox with ``base_unit='ms'`` and ``allowed_units=['s','ms','us']``.

Installing, updating and uninstalling
=====================================

To install or update, do:

.. code-block:: bash
  
  pip install -U scientific-spinbox

To remove, do:

.. code-block:: bash

  pip uninstall scientific-spinbox

To install it in development mode, from a local clone, do:

.. code-block:: bash

  git clone https://gitlab.com/dpizetta/pqwidget.git scientific-spinbox
  cd scientific-spinbox && git checkout develop-v1.x
  pip install -e .

Testing
=======

To run automated tests for scientific-spinbox, you can use the ``test``
environment on ``tox``:

.. code-block:: bash

  tox -e test

The ``test`` environment runs with ``PyQt5`` by default.

There are environments for testing the widget with ``PyQt5``, ``PyQt6`` and ``PySide6``, as
well as ``Python 3.10`` and ``Python 3.11``.

.. code-block:: bash

  tox -e py310-test-pyside6
  tox -e py310-test-pyqt5
  tox -e py310-test-pyqt6


.. code-block:: bash

  tox -e py311-test-pyside6
  tox -e py311-test-pyqt5
  tox -e py311-test-pyqt6

Usage
=====

This widget is intended to be used within your own Qt application. Please read the documentation
to see examples of usage and details on how to use it and extend its functionalities.

Compatibility
=============

Currently works with PyQt5, PyQt6 and PySide6. There's no plans of implementing a compatibility
layer with PySide2 for now.

Support
=======

There is no warranty or support at all. Use it at your own risk.
If you find an issue, please report it and the maintainers will try or help to fix.

Contributing
============

Any contribution is welcome and appreciated.
Before contributing, please read the "Contributing" section of the documentation.

Authors and acknowledgment
==========================

This work was developed by the authors at the Centro de Imagens e Espectroscopia por 
Ressonância Magnética (CIERMag), at the `São Carlos Institute of Physics <https://www2.ifsc.usp.br/english/>`_, 
University of São Paulo, Brazil.


Maintainer(s)
-------------

These people were/are maintainers of this project.

- 2023-current - `Breno H. Pelegrin da S. <brenohqsilva@gmail.com>`_
- 2023-current - `Daniel C. Pizetta <daniel.pizetta@alumni.usp.br>`_
- 2018-2020 - `Eduardo R. Falvo <dudu.falvo@gmail.com>`_

Contributor(s)
--------------

These people contributed to bug fixes, improvements, and new features.

- 2023-current - `Breno H. Pelegrin da S. <brenohqsilva@gmail.com>`_ - All development since 2023
- 2018-2020 - `Eduardo R. Falvo <dudu.falvo@gmail.com>`_ - Initial development of the project

License
=======

This project is licensed under `GNU Lesser General Public License (LGPLv3) <https://www.gnu.org/licenses/lgpl-3.0.html>`_.

Project status
==============

This project is still on **Beta**.
It is being actively developed and should reach its first stable release soon.
