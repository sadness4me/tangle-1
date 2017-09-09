#! /usr/bin/env python
# -*- coding: utf-8 -*-
import six as six
from tangle.m_annotation import Annotation


class FeatureMeta(type):
    def __new__(mcs, name, bases, namespace):
        return super(FeatureMeta, mcs).__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        super(FeatureMeta, cls).__init__(name, bases, namespace)

    def __add__(self, other):
        featured_class = self.__class__("FeaturedClass", (self,), dict())
        return other(featured_class)


class AnnotationFeature(object):
    def featuring_target(self, get_featured_target):
        return get_featured_target

    def enhance(self, featured_class):
        pass

    def __call__(self, featured_class):
        featured_class.get_featured_target = self.featuring_target(featured_class.get_featured_target)
        self.enhance(featured_class)
        return featured_class


@six.add_metaclass(FeatureMeta)
class FeaturedAnnotation(Annotation):
    pass


class AspectFeature(object):
    pass
