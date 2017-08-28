#! /usr/bin/env python
# -*- coding: utf-8 -*-

from tangle import Field, Bean, BaseApplicationContext


class Alpha(object):

    @Field(Beta)
    def field_a(self):
        pass

    @Field(Beta)
    def field_b(self):
        pass

    @Field(Gamma)
    def field_c(self):
        pass

    @Field(Delta)
    def field_d(self):
        pass


class Beta(object):
    pass


class Gamma(object):
    pass


class Delta(object):
    pass


class Application(object):

    @Bean
    def alpha(self):
        bean = Alpha()
        bean.field_a = self.beta()
        return Alpha()

    @Bean
    def beta(self):
        return Beta()

