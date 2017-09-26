#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from tangle.m_annotation import Annotation, get_annotations, Annotated


class TestAnnotation(Annotation):
    def after_set_target(self, target):
        pass

    def __init__(self, fn="yy", name="test_anno", status=1):
        self.param = fn
        self.name = name
        self.status = status
        super(TestAnnotation, self).__init__()


class XXX(Annotation):
    def after_set_target(self, target):
        pass


class YYY(Annotation):
    def after_set_target(self, target):
        pass

    def __init__(self, sex="female", age=1):
        self.sex = sex
        self.age = age
        super(YYY, self).__init__()


@Annotated
class AnnotatedTest(object):

    @YYY("male", 2)
    @TestAnnotation("xx", "anno", 2)
    @XXX()
    def test_annotation(self):
        print("original!")

    @XXX()
    @TestAnnotation()
    def test_anno2(self):
        print("anno2")


def test_instantiate():
    with pytest.raises(Exception):
        Annotation()
    TestAnnotation()


@Annotated
class AnnotatedSub(AnnotatedTest):

    @TestAnnotation()
    def sss(self):
        pass


@Annotated
class AnnotatedSubB(object):

    @XXX()
    def jjj(self):
        pass

    @YYY()
    def aaa(self):
        pass


@Annotated
class AnnotatedSubC(AnnotatedSubB, AnnotatedSub):

    @YYY()
    def kkk(self):
        pass


def test_annotate():
    a = AnnotatedTest()
    [annotation, annotation2] = get_annotations(a)
    assert isinstance(annotation, YYY)
    assert isinstance(annotation2, XXX)
    [yyy, test_anno, xxx]= annotation.annotations.values()
    assert isinstance(xxx, XXX)
    assert isinstance(test_anno, TestAnnotation)
    assert isinstance(yyy, YYY)
    assert yyy.sex == "male"
    assert yyy.age == 2
    assert test_anno.name == "anno"
    assert test_anno.status == 2
    assert test_anno.param == "xx"
    assert isinstance(annotation2, XXX)
    [xxx2, test_anno2] = annotation2.get_annotations()
    assert isinstance(xxx2, XXX)
    assert isinstance(test_anno2, TestAnnotation)
    assert test_anno2.status == 1
    assert test_anno2.name == "test_anno"
    assert test_anno2.param == "yy"

    b = AnnotatedSub()
    [sub_anno_a, sub_anno_b, sub_anno_c] = get_annotations(b)
    assert [sub_anno_a, sub_anno_b] == [annotation, annotation2]
    assert isinstance(sub_anno_c, TestAnnotation)

    c = AnnotatedSubC()
    [p, q, r, s, t, l] = get_annotations(c)
    assert [sub_anno_a, sub_anno_b, sub_anno_c] == [r, s, t]
    assert isinstance(p, XXX) and p.target.__name__ == "jjj"
    assert isinstance(q, YYY) and q.target.__name__ == "aaa"
