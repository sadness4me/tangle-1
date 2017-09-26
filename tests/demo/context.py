#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tangle.m_event import BeanPostProcessor


class TestPostProcessor(BeanPostProcessor):
    def post_initialize(self, application_context, bean):
        setattr(bean, "_test_post_init", True)
