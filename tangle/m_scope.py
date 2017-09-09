#! /usr/bin/env python
# -*- coding: utf-8 -*-


class ClassLocal(object):

    def __init__(self, object_provider):
        self.object_provider = object_provider

    def __get__(self, instance, owner):
        if instance:
            owner = type(instance)
        return self.object_provider.get(owner)

    def __set__(self, instance, value):
        self.object_provider.set(type(instance), value)
