=====
Usage
=====

To use tangle in a project::

    import tangle

Basic Concept
===============

If you are familiar with the Spring Framework, you may find the idea and mechanism of this framework quite easy to understand. Let's start with ``application context`` and ``bean``:

* ``application context`` (a.k.a. ``context``): The IoC container which creates and manages the lifecycle of ``bean``.
* ``bean``: A python object which is an instance of some class.
* ``configuration source``: A class instance which defines a list of bean definitions.

Note that when we refer to ``bean``, we focus on class instances, although python objects can be of any types (e.g. function, number, string, etc.). What about a class object as we know that it is also an instance of class (i.e. metaclass)? Well theoretically it should be OK to register class objects as beans in a context, but it is not fully tested. Therefore, it is *NOT* recommended to use ``tangle`` to manage class objects (maybe in the future).

When you apply ``tangle`` to your python program, the program may contain one or several ``context``, and many ``bean``. If you want to use the beans, use the ``get(bean_id)`` method of the context to obtain a bean instance. The ``bean_id`` is provided by your ``configuration source``.

Context
========

context

Bean
========

bean

Bean management
================

Dependency
------------

Scope
--------

Autowire
---------

Event
========

event

Aspect
========

aspect
