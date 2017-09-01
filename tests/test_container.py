#! /usr/bin/env python
# -*- coding: utf-8 -*-
import inspect


def get_function_arguments_spec(fn):
    if inspect.getfullargspec:
        args, varargs, keywords, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(fn)
    else:
        args, varargs, keywords, defaults = inspect.getargspec(fn)
        kwonlyargs = None
        kwonlydefaults = None
        annotations = None
    return args, varargs, keywords, defaults, kwonlyargs, kwonlydefaults, annotations


def test_func(name, male, test="aa", job="programmer", *args, **kwargs):
    print("name="+str(name))
    print("male="+str(male))
    print("args="+str(args))
    print("kwargs="+str(kwargs))


def test_bean_container():
    print(get_function_arguments_spec(test_func))
    test_func(1, 2, test="3", testkkk="xx")
