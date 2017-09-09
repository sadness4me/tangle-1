#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tangle.m_feature import FeaturedAnnotation, AnnotationFeature


def test_anno_feature():
    added = FeaturedAnnotation + AnnotationFeature()
    added(None)
