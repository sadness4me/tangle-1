#! /usr/bin/env python
# -*- coding: utf-8 -*-
import inspect


class B(object):
    def __init__(self, fn):
        pass

    def __get__(self, instance, owner):
        if not instance:
            return 2
        return 1


class A(object):
    __slots__ = "xx"
    @B
    def test(self):
        pass


def test_decorator():
    a = A()
    print([member for name, member in inspect.getmembers(A) if name == "test"])
    print([member for name, member in inspect.getmembers(a) if name == "test"])
    print(A.__dict__)
