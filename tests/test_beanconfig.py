#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from tangle.m_annotation import Annotated
from tangle.m_bean import Field
from tangle.m_container import Bean
from tangle.m_event import BeanPostProcessor
from tangle.m_support import BaseApplicationContext


class BeanA(object):
    pass


class BeanB(object):
    def __init__(self, bean_a):
        self.bean_a = bean_a


class BeanC(object):
    @Field(BeanA, True)
    def test(self):
        pass

    @Field(BeanB)
    def test2(self):
        pass


@Annotated
class TestConfig(object):
    @Bean
    def beana(self):
        return BeanA()

    @Bean
    def beanb(self):
        return BeanB(self.beana())

    @Bean
    def beanc(self):
        return BeanC()

    @Bean
    def container(self):
        return self


class TestBeanPostProcessor(BeanPostProcessor):
    def post_porcess(self, application_context, bean):
        print("test post:")
        print(bean)

test_config = TestConfig()
context = BaseApplicationContext(test_config)
context.build()


def test_config_factory():
    assert test_config.beanc().test == test_config.beana()
    assert test_config.beana() == test_config.beanb().bean_a
    with pytest.raises(AttributeError) as ex:
        print(test_config.beanc().test2)
    assert "not set yet" in ex.value.args[0]
