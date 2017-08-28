#! /usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import types

import six as six


@six.add_metaclass(abc.ABCMeta)  # this class hould not be instantiated, should only instantiate subclasses.
class Annotation(object):

    def __init__(self, obj):
        self.target = None
        self.annotations = []
        self.annotations_look_up = {}
        if isinstance(obj, Annotation):
            self.init_annotation(obj)
        elif isinstance(obj, types.FunctionType):
            self.init_function(obj)
        else:
            if obj is not None:
                self.init_argument(obj)
        self.register_annotation(self)

    def init_annotation(self, annotation):
        self.target = annotation.target
        self.annotations_look_up = annotation.annotations_look_up
        self.annotations = annotation.annotations

    def init_function(self, fn):
        self.target = fn

    @abc.abstractmethod
    def init_argument(self, argument):
        pass

    def register_annotation(self, annotation):
        if not isinstance(annotation, Annotation):
            raise Exception()
        if type(annotation) in self.annotations_look_up:
            raise Exception()
        self.annotations_look_up[type(annotation)] = len(self.annotations)
        self.annotations.append(annotation)

    def get_annotation(self, klass):
        if klass not in self.annotations_look_up:
            return None
        return self.annotations[self.annotations_look_up[klass]]

    def __call__(self, target):
        if isinstance(target, Annotation):
            self.init_annotation(target)
        elif isinstance(target, types.FunctionType):
            self.init_function(target)
        else:
            raise Exception()
        return self

    def get_instance_member(self, instance):
        return types.MethodType(self.target, instance)

    def __get__(self, instance, owner):
        if not instance:
            return self
        return self.get_instance_member(instance)
