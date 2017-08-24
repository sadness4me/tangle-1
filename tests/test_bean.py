#! /usr/bin/env python
# -*- coding: utf-8 -*-
import inspect

from tangle.m_bean import Field


class TestClass(object):

    def __init__(self):
        self.prop = 1


class TestBean(object):

    def __init__(self):
        self.param = 9

    def __call__(self, fn):
        self.fn = fn

        def constructor(caller):
            self.before_instantiate()
            try:
                bean = self.fn(caller)
                return self.after_instantiate_return(bean)
            except Exception as ex:
                self.after_instantiate_exception(ex)
            finally:
                self.after_instantiate_finally()

        self.constructor = constructor
        setattr(constructor, "_bean_def", self)
        return constructor

    """
    def __get__(self, instance, owner):
        def method():
            return self.constructor(instance)
        return method
    """

    def before_instantiate(self):
        print("before and param is: " + str(self.param))

    def after_instantiate_exception(self, error):
        print("after exception")

    def after_instantiate_return(self, bean):
        print("after return")
        return bean

    def after_instantiate_finally(self):
        print("finally!")


class TestMD(object):

    def __get__(self, instance, owner):
        if instance is None:
            return self
        def method_md():
            print("method_md!")
        return method_md


class TestPD(object):

    def __get__(self, instance, owner):
        return 20

    def __set__(self, instance, value):
        pass


class TestContainer(object):

    class_prop = 20

    @TestBean()
    def create_object(self):
        print("class_prop: " + str(self.class_prop))
        return TestClass()

    test_md = TestMD()
    test_pd = TestPD()

    @Field(TestClass)
    def field_test(self):
        pass

    @property
    def property_test(self):
        return 10


def test_bean1():

    def check(prop):
        print(prop)
        # if "TestBean" in str(prop):
        #     print(prop)
        return isinstance(prop, TestBean)

    container = TestContainer()
    for name, constructor in inspect.getmembers(TestContainer):
        print("prop name: "+name)
        if name == "test_md":
            print(constructor)
        if name in ["test_pd", "field_test", "property_test"]:
            print(constructor)
        # print(constructor)
        # bean_definition = getattr(constructor, '_bean_def')
        # bean_definition.param = 10

    container.test_md()
    assert isinstance(container.create_object(), TestClass)
    print("test_pd="+str(container.test_pd))
