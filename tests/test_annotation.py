#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from tangle.m_annotation import Annotation, get_annotations


class TestAnnotation(Annotation):
    def __init__(self, fn=None):
        super(TestAnnotation, self).__init__(fn)

    def init_argument(self, argument):
        raise Exception()


class Annotated(object):

    @TestAnnotation
    def test_annotation(self):
        print("original!")


def test_instantiate():
    with pytest.raises(Exception):
        Annotation(None)
    TestAnnotation()


def test_annotate():
    a = Annotated()
    [annotation] = get_annotations(a)
    assert isinstance(annotation, TestAnnotation)
