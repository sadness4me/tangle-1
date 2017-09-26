#! /usr/bin/env python
# -*- coding: utf-8 -*-


class EventRegister(object):
    def __init__(self):
        self.registry = {}
        self.check_queue = []

    def init_register(self, index):
        self.registry[index] = [0]

    def clear(self):
        self.registry = {}

    def register(self, index, *args):
        mark = [1] + list(args)
        self.registry[index] = mark

    def check(self, index, *args):
        mark = self.registry.get(index, None)
        assert mark == [1] + list(args)
        self.init_register(index)

    def uncheck(self, index):
        mark = self.registry.get(index, None)
        assert mark is None or mark == [0]


def test_deco(test_func):
    def wrapped_test():
        print()
        print("*************")
        print("begin test ** %s **", test_func.__name__)
        test_func()
        print("end test ** %s **", test_func.__name__)
        print("*************")
        print()
    return wrapped_test
