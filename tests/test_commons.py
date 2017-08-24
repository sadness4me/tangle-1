#! /usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import types

import six


def test_arg():

    def arg_in(a, *args):
        print(a + " args: ")
        for arg in args:
            print(arg)
    print("\n")
    arg_in("xxx", *[1,2,3])


def test_return():

    def method1():
        return 1, 2

    a, b = method1()
    print(type(a))


def test_method():

    class Test(object):

        def fn(self):
            print(type(self))
            return 1

    def overload(self):
        print("overloaded!")
        print(type(self))
        return 2

    Test.fn = overload

    a = Test()
    assert 2 == a.fn()


def test_method_type():

    class Test(object):
        def __init__(self):
            self.x = 1

    a = Test()

    class TestCall(object):

        def __call__(self, inst):
            return inst.x

    a.get_x = types.MethodType(TestCall(), a)

    class Desc(object):
        def __get__(self, instance, owner):
            if not instance:
                return self
            return lambda : instance.x

    class Callable(object):
        def __call__(self):
            return 22

    Test.get_desc = Desc()
    Test.get_call = Callable()

    def get_func():
        return 33

    a.get_func = get_func

    print(inspect.getmodule(Test).__name__)

    print(a.get_x())
    print(inspect.ismethod(a.get_x))
    print(type(a.get_x))
    print(a.get_desc())
    print(type(Test.get_desc))
    print("#############")
    print(inspect.isclass(Test.get_call))
    print(inspect.ismethod(Test.get_call))
    print(inspect.isfunction(Test.get_call))
    print(inspect.isclass(a.get_call))
    print(inspect.ismethod(a.get_call))
    print(inspect.isfunction(a.get_call))
    print(inspect.isclass(a.get_func))
    print(inspect.ismethod(a.get_func))
    print(inspect.isfunction(a.get_func))
    print(a.get_call())
    print(a.get_func())

    print("#############")
    for name, member in inspect.getmembers(Test, six.callable):
        print(name)
    print("#############")
    for name, member in inspect.getmembers(Test):
        print(name)
