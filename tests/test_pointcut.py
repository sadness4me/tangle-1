#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tangle import m_event, m_container
from tangle.m_aspect import Pointcut, JoinPoint


class PointcutA(Pointcut):
    def match(self, join_point):
        return join_point > 10


class PointcutB(Pointcut):
    def match(self, join_point):
        return join_point < 20


class PointcutZ(Pointcut):
    def match(self, join_point):
        return 30 > join_point > 15


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


def test_pointcut():
    bean1 = m_event.BeanPostProcessor()
    join_point1 = JoinPoint("post_initialize", bean1.post_initialize, bean1)
    join_point2 = JoinPoint("post_process", bean1.post_process, bean1)

    bean2 = m_container.BeanContainer()
    join_point3 = JoinPoint("get_all_beans", bean2.get_all_beans, bean2)
    join_point4 = JoinPoint("get_bean", bean2.get_bean, bean2)

    bean3 = m_container.BeanContainer()
    join_point5 = JoinPoint("register_bean_instance", bean3.register_bean_instance, bean3)

    pointcut = Pointcut.execute("tangle.m_event.*", "post*")

    assert pointcut.match(join_point1)
    assert pointcut.match(join_point2)
    assert not pointcut.match(join_point3)
    assert not pointcut.match(join_point4)
    assert not pointcut.match(join_point5)


