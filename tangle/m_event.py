#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tangle.m_aspect import Aspect


class ApplicationContextPostProcessor(object):
    def post_process(self, application_context):
        pass


class BeanPostProcessor(object):

    def post_initialize(self, application_context, bean):
        pass

    def post_process(self, application_context, bean):
        pass


class AspectBeanPostProcessor(BeanPostProcessor):

    def post_initialize(self, application_context, bean):
        beans = application_context.get_all_singleton_beans().values()
        for aspect in filter(lambda asp: isinstance(asp, Aspect), beans):
            print(aspect)
