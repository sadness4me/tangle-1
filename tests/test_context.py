#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from tangle.m_annotation import Annotated
from tangle.m_bean import Field
from tangle.m_container import Bean
from tangle.m_support import BaseApplicationContext
from tests import common_utils
from tests.demo.context import TestPostProcessor
from tests.user.user import TestChair, ChairAspect, temp_cache


class BeanA(object):
    pass


class BeanB(object):
    def __init__(self, bean_a):
        self.bean_a = bean_a


@Annotated
class BeanC(object):
    @Field(BeanA, True)
    def test(self):
        pass

    @Field(BeanB)
    def test2(self):
        pass


@Annotated
class TestConfig(object):
    @Bean()
    def beana(self):
        return BeanA()

    @Bean()
    def beanb(self):
        return BeanB(self.beana())

    @Bean(scope=Bean.Prototype)
    def beanc(self):
        return BeanC()

    @Bean()
    def container(self):
        return self

    @Bean()
    def bean_post_test(self):
        return TestPostProcessor()


test_config = TestConfig()
context = BaseApplicationContext(test_config)
context.build()


@Annotated
class TestAspect(object):
    @Bean()
    def test_chair(self):
        return TestChair()

    @Bean(Bean.Prototype)
    def test_chair2(self):
        return TestChair()

    @Bean()
    def chair_aspect(self):
        return ChairAspect()


test_aspect_inst = TestAspect()
aspect_context = BaseApplicationContext(test_aspect_inst, parent=context)
aspect_context.build()


@common_utils.test_deco
def test_config_factory():
    assert test_config.beanc().test == test_config.beana()
    assert test_config.beana() == test_config.beanb().bean_a
    instc = test_config.beanc()
    assert not instc == test_config.beanc()
    assert getattr(instc, "_test_post_init")
    assert instc.test == test_config.beana()

    with pytest.raises(AttributeError) as ex:
        print(test_config.beanc().test2)
    assert "not set yet" in ex.value.args[0]


@common_utils.test_deco
def test_aspect():
    test_chair = test_aspect_inst.test_chair()
    assert test_chair == aspect_context.get("test_chair")
    test_chair.add_leg()
    assert not temp_cache.get("before__add_leg")
    assert temp_cache.get("after__add_leg") == 1
    test_chair.add_leg()
    assert temp_cache.get("after__add_leg") == 2
    test_chair.change_name("xxx")
    assert temp_cache.get("before__change_name") == ("xxx",)
    with pytest.raises(ValueError) as ex:
        test_chair.increase(-3)
    assert "larger than 0" in ex.value.args[0]
    test_chair.construct("chair2", "steel", "leg3", 2)
    assert temp_cache["result"][3] == 8
    assert test_chair._test_post_init
    test_chair2 = test_aspect_inst.test_chair2()
    assert test_chair2._test_post_init
    with pytest.raises(ValueError) as ex:
        test_chair2.increase(-3)
    assert "larger than 0" in ex.value.args[0]
