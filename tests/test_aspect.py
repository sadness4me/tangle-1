#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tangle import m_event
from tangle import m_container

from tangle.m_aspect import Pointcut, Aspect, Before, After, process_aspect, JoinPoint


class PointcutA(Pointcut):
    def match(self, join_point):
        return join_point > 10


class PointcutB(Pointcut):
    def match(self, join_point):
        return join_point < 20


class PointcutZ(Pointcut):
    def match(self, join_point):
        return join_point < 30 and join_point > 15


def test_operation():
    a = PointcutA()
    b = PointcutB()
    z = PointcutZ()
    c = a & b
    d = a | b
    e = ~ a
    f = a ^ b
    y = a & b & z

    assert isinstance(c, Pointcut)
    assert c.match(15)
    assert not c.match(9)
    assert not c.match(33)
    assert d.match(15)
    assert d.match(9)
    assert d.match(33)
    assert e.match(9)
    assert not e.match(33)
    assert not f.match(15)
    assert f.match(9)
    assert f.match(33)
    assert y.match(17)
    assert not y.match(23)
    assert not y.match(12)


class TestAspect(Aspect):

    test1 = Pointcut.execute("*", "*ww")
    test2 = Pointcut.execute("tests.*", "*")

    def __init__(self):
        super(TestAspect, self).__init__()
        self.x = 1

    @Before(test1 & test2)
    def advise(self, inst):
        print("before advise " + str(self.x))

    @Before(test1 | test2)
    def advise2(self, inst):
        print("before 2222 " + str(self.x))


class TestAspect1(Aspect):

    test2 = Pointcut.execute("tests.*", "as_*")

    @After(test2)
    def advise(self, inst):
        print("after advise")


class Instance(object):

    def as_fdsafas(self):
        print("in execution!")
        return 1

    def as_www(self):
        print("www")
        return 2

    def no_as_test(self):
        return 3

def test_aspect_process():
    instance = Instance()
    aspect = TestAspect()
    aspect1 = TestAspect1()
    bean_adviser = process_aspect(instance, aspect, aspect1)

    print("\n")
    print(instance.as_fdsafas())
    print(instance.as_www())
    print(instance.no_as_test())


def test_pointcut():
    bean1 = m_event.BeanPostProcessor()
    join_point1 = JoinPoint("post_initialize", bean1.post_initialize, bean1)
    join_point2 = JoinPoint("post_process", bean1.post_process, bean1)

    bean2 = m_container.BeanContainer()
    join_point3 = JoinPoint("get_all_beans", bean2.get_all_beans, bean2)
    join_point4 = JoinPoint("get_bean", bean2.get_bean, bean2)

    bean3 = m_container.BeanContainer()
    join_point5 = JoinPoint("register_bean_instance", bean3.register_bean_instance, bean3)

    pointcut = Pointcut.execute("tangle.event.*", "post*")
    print("\n")
    for jp in [join_point1, join_point2, join_point3, join_point4, join_point5]:
        print(pointcut.match(jp))
