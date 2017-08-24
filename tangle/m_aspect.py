#! /usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import re
import six
import types


def process_aspect(bean, *aspects):
    bean_adviser = BeanAdviser(bean)
    for aspect in aspects:
        aspect.process(bean_adviser)
    bean_adviser.extract()
    return bean_adviser


class Aspect(object):
    def get_advises(self):

        def _initialize_advise(pair):
            advise = pair[1]
            advise.set_aspect(self)
            return advise

        return list(map(_initialize_advise, inspect.getmembers(type(self), lambda member: isinstance(member, Advise))))

    def __init__(self):
        self.advises = self.get_advises()

    def process(self, bean_adviser):
        for join_point in bean_adviser.join_points:
            self.advise_all(join_point)

    def advise_all(self, join_point):
        for advise in self.advises:
            advise.advise(join_point)


class Pointcut(object):
    @staticmethod
    def execute(class_pattern, method_pattern):
        class SubPointcut(Pointcut):
            def match_inst(self, inst):
                if not class_pattern:
                    return True
                class_regex = re.sub(r"\.", "\\.", class_pattern)
                class_regex = re.sub(r"\*", ".*", class_regex)
                klass = type(inst)
                return re.match(class_regex, inspect.getmodule(klass).__name__ + "." + klass.__name__) is not None

            def match_method(self, join_point):
                if not method_pattern:
                    return True
                method_regex = re.sub(r"\*", ".*", method_pattern)
                return re.match(method_regex, join_point.name) is not None

        return SubPointcut()

    def match(self, join_point):
        inst = join_point.bean
        return self.match_inst(inst) and self.match_method(join_point)

    def match_inst(self, inst):
        return True

    def match_method(self, join_point):
        return True

    def __and__(self, other):
        return self._create_operation_binary(other, lambda x, y: x and y)

    def __or__(self, other):
        return self._create_operation_binary(other, lambda x, y: x or y)

    def __invert__(self):
        return self._create_operation_unary(lambda x: not x)

    def __xor__(self, other):
        return self._create_operation_binary(other, lambda x, y: x is not y)

    def _create_operation_binary(self, other, match_operation):
        inst = self

        class PointcutOperation(Pointcut):
            def match(self, join_point):
                return match_operation(
                    inst.match(join_point),
                    other.match(join_point)
                )

        return PointcutOperation()

    def _create_operation_unary(self, match_operation):
        inst = self

        class PointcutOperation(Pointcut):
            def match(self, join_point):
                return match_operation(inst.match(join_point))

        return PointcutOperation()


class JoinPoint(object):
    def __init__(self, name, bean_callable, bean):
        self.bean = bean
        self.name = name
        self.before_advises = []
        self.after_advises = []
        self.return_advises = []
        self.error_advises = []
        self.callable_in_advise = bean_callable
        self.advised = False

    def get_advised_method(self):

        def advised_method(inst, *args, **kwargs):
            try:
                for before_advise in self.before_advises:
                    before_advise(inst, *args, **kwargs)
                result = self.callable_in_advise(*args, **kwargs)
                for return_advise in reversed(self.return_advises):
                    return_advise(inst, result, *args, **kwargs)
                return result
            except Exception as error:
                for error_advise in reversed(self.error_advises):
                    error_advise(inst, error, *args, **kwargs)
                six.raise_from(error, None)
            finally:
                for after_advise in reversed(self.after_advises):
                    after_advise(inst, *args, **kwargs)

        return advised_method


class BeanAdviser(object):
    def __init__(self, bean):
        self.bean = bean
        self.join_points = []
        for name, bean_callable in inspect.getmembers(bean, six.callable):
            if not name.startswith("__"):
                self.join_points.append(JoinPoint(name, bean_callable, bean))

    def extract(self):
        for join_point in self.join_points:
            if join_point.advised:
                setattr(self.bean, join_point.name, types.MethodType(join_point.get_advised_method(), self.bean))


class Advise(object):
    type_before = 0
    type_after = 1
    type_after_return = 2
    type_after_error = 3

    def __init__(self, pointcut, advise_type):
        self.pointcut = pointcut
        self.advise_method = None
        self.advise_type = advise_type
        self.aspect = None

    def __call__(self, fn):
        self.advise_method = fn
        return self

    def set_aspect(self, aspect):
        self.aspect = aspect
        fn = self.advise_method

        def aspect_wrapped_advise_method(inst, *args, **kwargs):
            return fn(aspect, inst, *args, **kwargs)

        self.advise_method = aspect_wrapped_advise_method

    def advise(self, join_point):
        if self.pointcut.match(join_point):
            join_point.advised = True
            advise = {
                Advise.type_before: "before_advises",
                Advise.type_after: "after_advises",
                Advise.type_after_return: "return_advises",
                Advise.type_after_error: "error_advises"
            }.get(self.advise_type)
            getattr(join_point, advise).append(self.advise_method)

    def __get__(self, instance, owner):
        if instance:
            return self.advise_method
        return self


class Before(Advise):
    def __init__(self, pointcut):
        super(Before, self).__init__(pointcut, Advise.type_before)


class After(Advise):
    def __init__(self, pointcut):
        super(After, self).__init__(pointcut, Advise.type_after)


class AfterError(Advise):
    def __init__(self, pointcut):
        super(AfterError, self).__init__(pointcut, Advise.type_after_error)


class AfterReturn(Advise):
    def __init__(self, pointcut):
        super(AfterReturn, self).__init__(pointcut, Advise.type_after_return)
