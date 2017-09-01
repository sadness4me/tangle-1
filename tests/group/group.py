#! /usr/bin/env python
# -*- coding: utf-8 -*-


class TestGroup(object):
    def __init__(self, name, size, usage):
        self.name = name
        self.size = size
        self.usage = usage

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size

    def get_usage(self):
        return self.usage

    def increase_size(self):
        self.size = self.size + 1

    def decrease_size(self):
        self.size = self.size -1


class TestBureau(object):

    def cal_sum(self, a, b, c):
        return a + b + c

    def cal_mul(self, a, b, c):
        return a * b * c

    def cal_min(self, a, b):
        return a - b
