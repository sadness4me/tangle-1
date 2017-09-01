#! /usr/bin/env python
# -*- coding: utf-8 -*-


class TestUser(object):
    def __init__(self, name, sex, age):
        self.name = name
        self.sex = sex
        self.age = age

    def get_name(self):
        return self.name

    def get_sex(self):
        return self.sex

    def get_age(self):
        return self.age

    def change_sex(self):
        self.sex = not self.sex

    def increase_age(self):
        self.age = self.age + 1
        return self.age

    def increase_age_diff(self, *diff):
        self.age = self.age + sum(diff)
        return self.age

