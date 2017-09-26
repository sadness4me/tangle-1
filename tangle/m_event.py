#! /usr/bin/env python
# -*- coding: utf-8 -*-


class ApplicationContextPostProcessor(object):
    def post_process(self, application_context):
        pass


class BeanPostProcessor(object):
    def post_initialize(self, application_context, bean):
        pass

    def post_process(self, application_context, bean):
        pass
