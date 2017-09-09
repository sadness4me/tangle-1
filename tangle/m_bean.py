#! /usr/bin/env python
# -*- coding: utf-8 -*-
import six
from tangle.m_annotation import Annotation, get_annotations


def get_fields(obj):
    return list(filter(lambda entry: isinstance(entry, Field), get_annotations(obj)))


class Field(Annotation):
    def __init__(self, klass=None, autowire=False):
        self.klass = None
        self.autowire = autowire
        self.cb_set = None
        self.name = None
        super(Field, self).__init__(klass)

    def init_class_annotate(self):
        self.klass = None

    def init_instance_annotate(self, klass):
        self.klass = klass

    def get_instance_member(self, instance):
        return self.get(instance)

    def get_class_member(self, cls):
        return self

    def __set__(self, obj, value):
        self.set(obj, value)
        if self.cb_set:
            self.cb_set(obj, value)

    def after_set_target(self, target):
        self.name = target.__name__

    def get(self, inst):
        try:
            self.target(inst)   # getter callback
            return getattr(inst, "_" + self.name)
        except AttributeError:
            six.raise_from(AttributeError("property (%s) not set yet!" % self.name), None)

    def set(self, inst, value):
        if self.klass and not isinstance(value, self.klass):
            raise TypeError("set property type (%s) wrong!" % self.klass.__name__)
        setattr(inst, "_" + self.name, value)

    def setter(self, fn):
        """ set the setter callback function. It is invoked when the field is set (i.e. `{field}={value}`).

        :param fn: the callback function to set
        :return: should not return
        """
        self.cb_set = fn
