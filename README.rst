======
tangle
======


.. image:: https://img.shields.io/pypi/v/tangle.svg
        :target: https://pypi.python.org/pypi/tangle

.. image:: https://img.shields.io/travis/fifman/tangle.svg
        :target: https://travis-ci.org/fifman/tangle

.. image:: https://readthedocs.org/projects/tangle/badge/?version=latest
        :target: https://tangle.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/fifman/tangle/shield.svg
        :target: https://pyup.io/repos/github/fifman/tangle/
        :alt: Updates

.. image:: https://coveralls.io/repos/github/fifman/tangle/badge.svg?branch=master
        :target: https://coveralls.io/github/fifman/tangle?branch=master

.. image:: https://sonarcloud.io/api/badges/measure?key=tangle&metric=vulnerabilities
    :target: https://sonarcloud.io/component_measures/metric/vulnerabilities/list?id=tangle

.. image:: https://sonarcloud.io/api/badges/measure?key=tangle&metric=bugs
    :target: https://sonarcloud.io/component_measures/metric/bugs/list?id=tangle


A python IoC and AOP framework.


* Free software: MIT license
* Documentation: https://tangle.readthedocs.io.


.. contents::

.. section-numbering::

Features
--------

* Decorator (annotation) based configuration support for AOP (aspect oriented programming) and bean (instance of python class) memebers (``Field``).
* Programmatic configuration support for bean construction and application context (i.e. IoC container) configuration.
* Supports application context inheritance, that is, a parent context can be specified to an application context. Note: multi-parents are not supported.
* Supports autowire
* supports the ``scope`` feature, which determines the lifecycle of the beans managed by the context, including the ``Singleton`` and ``Prototype`` scope.
* Context and bean lifecycle hooks support

Installation
------------------

See Installation_.

.. _Installation: docs/installation.rst

Usage
---------

See Usage_.

.. _Usage: docs/usage.rst

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

Inspired by `Spring Framework`_.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Spring Framework: https://github.com/spring-projects/spring-framework
