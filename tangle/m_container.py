#! /usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import inspect
import types

from tangle.m_annotation import Annotation


class Bean(Annotation):
    Singleton = 1
    Prototype = 2

    def __init__(self, scope=Singleton, bean_id=None, is_config=False):
        self.scope = None
        self.bean_id = bean_id
        self.klass = None
        self.container_class = None
        self.bean_container = None
        self.is_config = is_config
        self.creator = None
        self.wrapped_creator = None
        super(Bean, self).__init__(scope, bean_id, is_config)

    def init_instance_annotate(self, scope, bean_id, is_config):
        pass

    def init_class_annotate(self):
        self.scope = Bean.Singleton

    def after_set_target(self, fn):
        if not self.bean_id:
            self.bean_id = fn.__name__

        def create(inst):
            if self.scope == Bean.Singleton:
                bean = self.bean_container.singleton_bean_dict.get(self.bean_id, None)
                if bean:
                    return bean
            self.bean_container.before_bean_instantiate(self)
            bean = fn(inst)
            self.klass = type(bean)
            if self.scope == Bean.Singleton:
                self.bean_container.register_bean_instance(self.bean_id, bean)
            self.bean_container.after_bean_instantiate(self, bean)
            return bean

        self.wrapped_creator = create

    def get_instance_member(self, target, instance):
        return types.MethodType(self.wrapped_creator, instance)

    def aware_owner_class(self, owner):
        self.container_class = owner


class BeanContainer(object):
    def __init__(self):
        self.bean_definition_dict = collections.OrderedDict()
        self.singleton_bean_dict = collections.OrderedDict()
        self.config_source_dict = collections.OrderedDict()
        self.prototype_beans_referenced = []

    def register_config_source(self, config_source):
        config_class = type(config_source)
        config_source_id = config_class.__name__
        assert config_class not in self.config_source_dict, "the config source class is already registered!"
        config_bean_definition = Bean(bean_id=config_source_id, is_config=True)
        config_bean_definition.klass = config_class
        self._register_bean_definition(config_bean_definition)
        self._register_bean_instance(config_source_id, config_source)
        self.post_register_config_source(config_bean_definition, config_source)
        self.config_source_dict[config_class] = config_source_id

    def load_config_source(self, config_source):
        bean_definitions = inspect.getmembers(type(config_source), lambda member: isinstance(member, Bean))
        for name, bean_definition in bean_definitions:
            self.register_bean_definition(bean_definition)

    def register_bean_definition(self, bean_definition):
        assert bean_definition.bean_id is not None, "bean_id of bean definition should not be null"
        self._register_bean_definition(bean_definition)
        self.post_register_bean_definition(bean_definition)

    def _register_bean_definition(self, bean_definition):
        bean_definition.bean_container = self
        self.bean_definition_dict[bean_definition.bean_id] = bean_definition

    def register_bean_instance(self, bean_id, bean):
        assert bean_id is not None, "bean_id should not be null"
        self.singleton_bean_dict[bean_id] = bean
        self.post_register_bean_instance(self.get_bean_definition(bean_id), bean)

    def _register_bean_instance(self, bean_id, bean):
        self.singleton_bean_dict[bean_id] = bean

    def get_bean(self, bean_id):
        bean_definition = self.bean_definition_dict.get(bean_id, None)
        assert bean_definition is not None, "input bean_id is not registered!"
        if bean_definition.scope == Bean.Prototype:
            return self.create_bean(bean_definition)
        else:
            bean = self.singleton_bean_dict.get(bean_id, None)
            if bean is None:
                bean = self.create_bean(bean_definition)
                self.register_bean_instance(bean_id, bean)
            return bean

    def get_bean_dict(self):
        return self.singleton_bean_dict

    def get_all_beans(self):
        return list(self.singleton_bean_dict.values()) + self.prototype_beans_referenced

    def get_bean_definition_dict(self):
        return self.bean_definition_dict

    def get_bean_definition(self, bean_id):
        return self.bean_definition_dict.get(bean_id, None)

    def create_bean(self, bean_definition):
        config_bean = self.singleton_bean_dict[self.config_source_dict[bean_definition.container_class]]
        return bean_definition.wrapped_creator(config_bean)

    def post_register_config_source(self, config_bean_definition, config_bean):
        pass

    def post_register_bean_definition(self, bean_definition):
        pass

    def post_register_bean_instance(self, bean_definition, bean):
        pass

    def before_bean_instantiate(self, bean_definition):
        pass

    def after_bean_instantiate(self, bean_definition, bean):
        pass
