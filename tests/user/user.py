#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tangle.m_annotation import Annotated
from tangle.m_aspect import Aspect, Before, After, ArgsSolver, AfterReturn, Pointcut


class TestUser(object):
    def __init__(self, name, sex, age):
        self.name = name
        self.sex = sex
        self.age = age

    def get_name(self):
        return self.name

    def get_sex(self):
        return self.sex

    def get_age(self):
        return self.age

    def change_sex(self):
        self.sex = not self.sex

    def increase_age(self):
        self.age = self.age + 1
        return self.age

    def increase_age_diff(self, *diff):
        self.age = self.age + sum(diff)
        return self.age


class TestChair(object):
    def __init__(self):
        self.leg = "leg"
        self.type = "wood"
        self.name = "chair"
        self.num = 4

    def add_leg(self):
        self.num = self.num + 1

    def cut_leg(self):
        self.num = self.num - 1

    def increase(self, num):
        self.num = self.num + num

    def change_name(self, name):
        self.name = name

    def construct(self, name, type, leg, num=4):
        self.name = name
        self.type = type
        self.leg = leg
        self.num = self.num + num
        return [name, type, leg, self.num]


temp_cache = {}


def _solve_param(inst, fn, args, kwargs):
    return args[0:1], {}


@Annotated
class ChairAspect(Aspect):

    pc1 = Pointcut.execute("*user*", "*")
    pc2 = Pointcut.execute("*user*", "construct")
    pc3 = Pointcut.execute("*user*", "increase")

    @Before(pc1, args_solver=ArgsSolver.keep)
    def cache_args(self, inst, fn, *args, **kwargs):
        temp_cache["before__" + fn.__name__] = args

    @After(pc1 | pc2, args_solver=ArgsSolver.method)
    def cache_results(self, inst, fn):
        if not temp_cache.get("after__" + fn.__name__, None):
            temp_cache["after__" + fn.__name__] = 1
            return
        temp_cache["after__" + fn.__name__] = temp_cache["after__" + fn.__name__] + 1

    @Before(pc3, args_solver=_solve_param)
    def validate(self, arg):
        if arg < 0:
            raise ValueError("should be larger than 0")

    @AfterReturn(pc2)
    def validate_return(self, result):
        temp_cache["result"] = result
        assert len(result) == 4
