#! /usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import types

from tangle.m_annotation import Annotated
from tangle.m_container import BeanContainer, Bean


class AAA(object):
    pass


class BBB(object):
    pass


@Annotated
class TestConfig(object):

    @Bean
    def constructor_class_annotation(self):
        return AAA()

    @Bean(bean_id="bean_id_specified")
    def constructor_instance_annotation(self):
        return BBB()

    @staticmethod
    def _func_as_bean():
        return 10

    @Bean
    def constructor_4_func(self):
        return self._func_as_bean

    @Bean(Bean.Prototype)
    def constructor_prototype(self):
        return AAA()


config = TestConfig()
container = BeanContainer()
container.register_config_source(config)
container.load_config_source(config)
container.instantiate_beans()


def test_bean_definition():
    bean_def1 = container.get_bean_definition("constructor_class_annotation")
    assert bean_def1.scope == Bean.Singleton
    assert bean_def1.klass == AAA
    bean_def2 = container.get_bean_definition("bean_id_specified")
    assert bean_def2.klass == BBB
    bean_def3 = container.get_bean_definition("constructor_4_func")
    assert bean_def3.klass == types.FunctionType
    bean_def4 = container.get_bean_definition("constructor_prototype")
    assert bean_def4.scope == Bean.Prototype


def test_bean_instance():
    assert config.bean_container == container
    assert config.constructor_class_annotation() == container.get_bean("constructor_class_annotation")
    assert config.constructor_class_annotation() == config.constructor_class_annotation()
    assert config.constructor_instance_annotation() == config.constructor_instance_annotation()
    assert config.constructor_instance_annotation() == container.get_bean("bean_id_specified")
    assert inspect.isfunction(config.constructor_4_func())
    assert config.constructor_4_func() == config.constructor_4_func()
    assert config.constructor_4_func() == container.get_bean("constructor_4_func")
    assert not config.constructor_prototype() == container.get_bean("constructor_prototype")
    assert not container.get_bean("constructor_prototype") == container.get_bean("constructor_prototype")
    assert not config.constructor_prototype() == config.constructor_prototype()
    assert isinstance(container.get_bean("constructor_prototype"), AAA)
    assert config.constructor_4_func()() == 10

