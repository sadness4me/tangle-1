#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from tangle.m_annotation import Annotated
from tangle.m_bean import get_fields, Field
from tests.common_utils import EventRegister


_register = EventRegister()


class Alpha(object):
    pass


@Annotated
class TestBean(object):

    @Field()
    def field1(self):
        _register.register(1)

    @Field(Alpha, True)
    def field2(self):
        _register.register(2)

    @Field(autowire=True)
    def field3(self):
        _register.register(3)

    @field1.setter
    def set_field1(self, value):
        _register.register(4, value)


def test_field():
    field1, field2, field3 = get_fields(TestBean)
    assert field1.name == "field1"
    assert not field1.klass
    assert not field1.autowire
    assert field2.klass == Alpha
    assert field2.name == "field2"
    assert field2.autowire
    assert field3.autowire
    assert not field3.klass
    _register.clear()


def test_instance():
    tb = TestBean()
    _register.uncheck(4)
    tb.field1 = 1
    _register.check(4, 1)
    _register.uncheck(1)
    assert tb.field1 == 1
    _register.check(1)
    with pytest.raises(TypeError):
        tb.field2 = True
    alpha = Alpha()
    tb.field2 = alpha
    _register.uncheck(2)
    assert tb.field2 == alpha
    _register.check(2)
    tb.field3 = "test"
    _register.uncheck(3)
    assert tb.field3 == "test"
    _register.check(3)
