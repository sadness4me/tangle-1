#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tangle.m_annotation import Annotated
from tests.common_utils import EventRegister
from tests.group.group import TestGroup, TestBureau
from tests.user.user import TestUser
from tangle.m_aspect import Pointcut, Aspect, Before, After, process_aspects, ArgsSolver, AfterReturn, AfterError, \
    JoinPoint


pc1 = Pointcut.execute("*", "get*")
pc2 = Pointcut.execute("*group.*", "*")
pc3 = Pointcut.execute("*", "cal*")
pc4 = Pointcut.execute("*user*", "*")
pc5 = Pointcut.execute("*", "get*")


_event_register = EventRegister()


@Annotated
class TestAspectBefore(Aspect):
    def __init__(self):
        super(TestAspectBefore, self).__init__()

    @Before(pc1 & pc2)
    def advise(self):
        _event_register.register(1)

    @Before(pc1 | pc2, ArgsSolver.method)
    def advise2(self, inst, fn):
        _event_register.register(2, inst)

    @Before()
    @staticmethod
    def advise3():
        _event_register.register(3)

    @Before(args_solver=ArgsSolver.keep)
    def advise4(self, inst, fn, *args, **kwargs):
        _event_register.register(4, inst, args, kwargs)


def _solve(inst, fn, args, kwargs):
    args_size = len(args) if args else 0
    kwargs_size = len(kwargs) if kwargs else 0
    return [args_size, kwargs_size], {}


@Annotated
class TestAspectAfter(Aspect):
    @After(pc4, ArgsSolver.method)
    def advise(self, inst, fn):
        _event_register.register(5, inst)

    @After()
    def advise2(self):
        _event_register.register(6)

    @After(pc5, _solve)
    @staticmethod
    def advise3(count_args, count_kwargs):
        _event_register.register(7, count_args + count_kwargs)

    @AfterError(pc3, ArgsSolver.keep)
    @classmethod
    def test_classmethod_advise(cls, error, inst, fn, *args, **kwargs):
        _event_register.register(8, error, inst, args, kwargs)

    @AfterReturn(pc3)
    @staticmethod
    def test_staticmethod_advise(result):
        _event_register.register(9, result)


def _exe_test_call(expect_error, inst, fn, *args, **kwargs):
    join_point = JoinPoint(fn.__name__, fn, inst)
    error = None
    result = None
    if expect_error:
        try:
            result = fn(*args, **kwargs)
        except Exception as error1:
            error = error1
    else:
        result = fn(*args, **kwargs)
    if (pc1 & pc2).match(join_point):
        _event_register.check(1)
    if (pc1 | pc2).match(join_point):
        _event_register.check(2, inst)
    _event_register.check(3)
    _event_register.check(4, inst, args, kwargs)
    if pc4.match(join_point):
        _event_register.check(5, inst)
    _event_register.check(6)
    if pc5.match(join_point):
        _event_register.check(7, len(args)+len(kwargs))
    if pc3.match(join_point):
        _event_register.check(8, inst, error, inst, args, kwargs)
    if pc3.match(join_point):
        _event_register.check(9, result)
    _event_register.clear()
    return error


def test_aspect_process():
    inst_group = TestGroup("group", 10, "dept")
    inst_user = TestUser("jack", True, 20)
    inst_cal = TestBureau()
    aspect = TestAspectBefore()
    aspect1 = TestAspectAfter()
    advised_group = process_aspects(inst_group, aspect, aspect1)
    advised_user = process_aspects(inst_user, aspect, aspect1)
    advised_cal = process_aspects(inst_cal, aspect, aspect1)

    _exe_test_call(False, inst_group, inst_group.get_name)
    _exe_test_call(False, inst_group, inst_group.decrease_size)
    _exe_test_call(False, inst_user, inst_user.get_sex)
    _exe_test_call(False, inst_user, inst_user.increase_age_diff, 3, 4)
    _exe_test_call(False, inst_cal, inst_cal.cal_sum, 1, 2, c=3)
    _exe_test_call(False, inst_cal, inst_cal.cal_mul, 1, b=2, c=3)
    _exe_test_call(False, inst_cal, inst_cal.cal_min, 1, 2)
    error = _exe_test_call(True, inst_cal, inst_cal.cal_min, 1, "xxx")
    assert isinstance(error, TypeError)

