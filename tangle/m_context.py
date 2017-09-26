#! /usr/bin/env python
# -*- coding: utf-8 -*-
import six
import six.moves
import logging
from tangle import m_aspect, m_bean, m_container, m_event


class BeanIdError(ValueError):
    def __init__(self):
        super(BeanIdError, self).__init__(
            "bean id has not been found in application context, check if you input the wrong id!")


class WireUtils(object):

    def __init__(self, application_context):
        self.application_context = application_context
        self.logger = logging.getLogger(__name__)

    def _select_wire_bean(self, expectation):
        for bean_id, bean_definition in six.iteritems(self.application_context.get_all_bean_definitions()):
            if expectation(bean_definition):
                return self.application_context.get(bean_definition.bean_id)
        return None

    def _wire_class(self, klass):
        return self._select_wire_bean(lambda bean_definition: issubclass(bean_definition.klass, klass))

    def wire(self, field):
        wired_bean = self._wire_class(field.klass)
        return wired_bean

    def autowire(self, bean):
        for field in m_bean.get_fields(bean):
            if field.autowire:
                wired_bean = self.wire(field)
                if wired_bean:
                    field.set(bean, wired_bean)
                else:
                    self.logger.warning("The field '%s' of the bean '%s' with type %s cannot be autowired!", field.name, bean.bean_id, type(bean).__name__)


class BeanHook(object):

    def __init__(self, application_context):
        self.application_context = application_context

    def post_load_definition(self, bean_definition):
        pass

    def post_instantiate(self, bean):
        pass

    def initialize(self, bean):
        self.application_context.wire_utils.autowire(bean)

    def post_initialize(self, bean):
        # self.application_context.wire_utils.autowire(bean)
        context = self.application_context
        for bpp in context.bean_post_processors:
            bpp.post_initialize(context, bean)

    def post_process(self, bean):
        m_aspect.process_aspects(bean, *self.application_context.aspects)


class ApplicationContext(object):
    def __init__(self, config_sources=(), parent=None):
        """
        Only instantiate the context and provides some basic properties.
        :param config_sources: array of config classes
        """
        self.config_sources = config_sources
        self.bean_container = self.create_bean_container()
        self.parent = parent
        self.wire_utils = WireUtils(self)
        self.bean_post_processors = []
        self.contained_beans = []
        self.aspects = []
        self._bean_hook = BeanHook(self)

    def build(self):
        self.register_config_sources()
        self.load_bean_definitions()
        self.post_load_bean_definitions()
        self.instantiate_beans()
        self.post_instantiate_beans()
        self.initialize_beans()
        self.post_initialize_beans()
        self.post_process_context()

    def create_bean_container(self):
        context = self

        class WrappedBeanContainer(m_container.BeanContainer):

            def post_register_bean_definition(self, bean_definition):
                super(WrappedBeanContainer, self).post_register_bean_definition(bean_definition)

            def post_register_config_source(self, config_bean_definition, config_bean):
                super(WrappedBeanContainer, self).post_register_config_source(config_bean_definition, config_bean)

            def post_register_bean_instance(self, bean_definition, bean):
                super(WrappedBeanContainer, self).post_register_bean_instance(bean_definition, bean)

            def before_bean_instantiate(self, bean_definition):
                context._bean_hook.post_load_definition(bean_definition)

            def after_bean_instantiate(self, bean_definition, bean):
                super(WrappedBeanContainer, self).after_bean_instantiate(bean_definition, bean)
                if bean_definition.scope == m_container.Bean.Singleton or not self.beans_instantiated:
                    return
                bean_hook = context._bean_hook
                bean_hook.post_instantiate(bean)
                bean_hook.initialize(bean)
                bean_hook.post_initialize(bean)
                bean_hook.post_process(bean)

        return WrappedBeanContainer()

    def register_config_sources(self):
        for config_source in self.config_sources:
            self.bean_container.register_config_source(config_source)

    def load_bean_definitions(self):
        for config_source in self.config_sources:
            self.bean_container.load_config_source(config_source)

    def post_load_bean_definitions(self):
        for bean_definition in self.get_all_bean_definitions():
            self._bean_hook.post_load_definition(bean_definition)

    def instantiate_beans(self):
        self.bean_container.instantiate_beans()

    def post_instantiate_beans(self):
        for bean in self.get_contained_beans():
            self._bean_hook.post_initialize(bean)

    def initialize_beans(self):
        for bean in self.get_contained_beans():
            self._bean_hook.initialize(bean)

    def post_initialize_beans(self):
        beans = self.get_all_singleton_beans().values()
        self.bean_post_processors = list(filter(lambda bpp: isinstance(bpp, m_event.BeanPostProcessor), beans))
        for bean in self.get_contained_beans():
            self._bean_hook.post_initialize(bean)

    def post_process_context(self):
        beans = self.get_all_singleton_beans().values()
        self.aspects = list(filter(lambda aspect: isinstance(aspect, m_aspect.Aspect), beans))
        for bean in self.get_contained_beans():
            m_aspect.process_aspects(bean, *self.aspects)

    def get_parent(self):
        return self.parent

    def get(self, bean_id):
        bean = self.bean_container.get_bean(bean_id)
        if bean:
            return bean
        parent = self.get_parent()
        if not parent:
            raise BeanIdError()
        return parent.get(bean_id)

    def get_all_singleton_beans(self):
        """ get all singleton scope beans contained in the application context, including ancestor application contexts. """
        beans = {}
        if self.get_parent():
            beans.update(self.get_parent().get_all_singleton_beans())
        beans.update(self.bean_container.get_bean_dict())
        return beans

    def get_all_bean_definitions(self):
        """ get all bean definitions contained in the application context, including ancestor application contexts. """
        bean_definitions = {}
        if self.get_parent():
            bean_definitions.update(self.get_parent().get_all_bean_definitions())
        bean_definitions.update(self.bean_container.get_bean_definition_dict())
        return bean_definitions

    def get_contained_beans(self):
        return self.bean_container.get_all_beans()

    def exec_bean_post_instantiate(self, bean):
        pass

    def exec_post_instantiate(self):
        pass


class RootApplicationContext(ApplicationContext):
    pass


class AbstractApplicationContext(ApplicationContext):
    _root_application_context = RootApplicationContext()

    def __init__(self, config_sources=(), parent=_root_application_context):
        super(AbstractApplicationContext, self).__init__(config_sources, parent=parent)
