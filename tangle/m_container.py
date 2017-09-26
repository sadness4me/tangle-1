#! /usr/bin/env python
# -*- coding: utf-8 -*-
import collections
from tangle.m_annotation import Annotation, get_annotations


class Bean(Annotation):
    """
    This annotation class annotates the target as a bean. The annotated target should be a callable member (i.e. constructor) of a class (which is called a context config class). When a :class:`tangle.m_context.ApplicationContext` instance reads a instance of the context config class, the context instance fetches all of the annotations contained in the context config class, extract the constructor from each annotation, and then invoke the constructor (note that the constructor is now a method of the config class instance) and register the returned value as a bean.

    Attributes:

        scope(`Bean.Prototype` or `Bean.Singletn`): bean scope.
        bean_id(str): bean id.
        klass(class): bean type.
        owner_class(class): the config class which contains this annotation. Available only when the config class is decorated with :class:`tangle.m_annotation.Annotated`.
        creator(function): the original function which is the bean annotation target
        wrapped_creator(method): a :class:`types.MethodType` instance that is a method of the config instance. It accepts the bean container which loads the config instance as the only argument

    """

    Singleton = 1
    Prototype = 2

    def __init__(self, scope=Singleton, bean_id=None):
        """Init the bean instance

        :param scope: bean scope. Its value can be `Bean.Singleton` or `Bean.Prototype`.
        :param bean_id: set the id of the bean. The bean id should be unique in a context.

        """
        self.scope = scope  # bean scope
        self.featured_target = None
        self.bean_id = bean_id  # bean id
        self.klass = None  # bean type, which is set when the bean instance is created
        self.creator = None
        self.is_config = False  # only for internal use, indicates whether the bean itself is a config instance.
        super(Bean, self).__init__()

    def after_set_target(self, fn):
        if isinstance(fn, staticmethod) or isinstance(fn, classmethod):
            raise Exception("cannot annotate staticmethod or classmethod!")
        if not self.bean_id:
            self.bean_id = fn.__name__

        def create(inst):
            bean_container = inst.bean_container
            if self.scope == Bean.Singleton:
                bean = bean_container.singleton_bean_dict.get(self.bean_id, None)
                if bean:
                    return bean
            bean_container.before_bean_instantiate(self)
            bean = fn(inst)
            self.klass = type(bean)
            if self.scope == Bean.Singleton:
                bean_container.register_bean_instance(self.bean_id, bean)
            bean_container.after_bean_instantiate(self, bean)
            return bean

        self.featured_target = create

    def get_featured_target(self):
        return self.featured_target


class BeanContainer(object):
    """The bean container which stores bean definitions and singleton bean instances. Each :class:`tangle.m_context.ApplicationContext` instance contains just one bean container.
    It is only for internal usage of tangle.
    """

    def __init__(self):
        self.bean_definition_dict = collections.OrderedDict()
        self.singleton_bean_dict = collections.OrderedDict()
        self.config_source_dict = collections.OrderedDict()
        self._prototype_beans_referenced = []
        self.beans_instantiated = False

    def register_config_source(self, config_source):
        config_source.bean_container = self      # register the bean container to the config instance
        config_class = type(config_source)
        config_source_id = config_class.__name__
        assert config_class not in self.config_source_dict, "the config source class is already registered!"
        config_bean_definition = Bean(bean_id=config_source_id)
        config_bean_definition.is_config = True
        config_bean_definition.klass = config_class
        self._register_bean_definition(config_bean_definition)
        self._register_bean_instance(config_source_id, config_source)
        self.post_register_config_source(config_bean_definition, config_source)
        self.config_source_dict[config_class] = config_source_id

    def load_config_source(self, config_source):
        bean_definitions = list(filter(lambda member: isinstance(member, Bean), get_annotations(config_source)))
        for bean_definition in bean_definitions:
            self.register_bean_definition(bean_definition)

    def instantiate_beans(self):
        for bean_definition in self.bean_definition_dict.values():
            if not bean_definition.is_config and not bean_definition.scope == Bean.Prototype:
                self.create_bean(bean_definition)
        self.beans_instantiated = True

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
        return list(self.singleton_bean_dict.values()) + self._prototype_beans_referenced

    def get_bean_definition_dict(self):
        return self.bean_definition_dict

    def get_bean_definition(self, bean_id):
        return self.bean_definition_dict.get(bean_id, None)

    def create_bean(self, bean_definition):
        config_bean = self.singleton_bean_dict[self.config_source_dict[bean_definition.owner_class]]
        return bean_definition.get_featured_target()(config_bean)

    def post_register_config_source(self, config_bean_definition, config_bean):
        pass

    def post_register_bean_definition(self, bean_definition):
        pass

    def post_register_bean_instance(self, bean_definition, bean):
        pass

    def before_bean_instantiate(self, bean_definition):
        pass

    def after_bean_instantiate(self, bean_definition, bean):
        if bean_definition.scope == Bean.Singleton:
            return
        if not self.beans_instantiated:
            self._prototype_beans_referenced.append(bean)
