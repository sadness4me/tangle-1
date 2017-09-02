#! /usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import re
import six
import types

from tangle.m_annotation import Annotation


def process_aspects(bean, *aspects):
    advised_bean_wrapper = AdvisedBeanWrapper(bean)
    for aspect in aspects:
        aspect.process(advised_bean_wrapper)
    advised_bean_wrapper.extract()
    return advised_bean_wrapper


class Aspect(object):
    @property
    def advises(self):
        return list(
            member for name, member in inspect.getmembers(type(self), lambda member: isinstance(member, Advise)))

    def process(self, bean_adviser):
        for join_point in bean_adviser.join_points:
            self.advise_all(join_point)

    def advise_all(self, join_point):
        for advise in self.advises:
            advise.advise(join_point, self)


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

    @staticmethod
    def all():
        class SubPointcutAll(Pointcut):
            def match(self, join_point):
                return True

        return SubPointcutAll()

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
                    before_advise(inst, self.callable_in_advise, *args, **kwargs)
                result = self.callable_in_advise(*args, **kwargs)
                for return_advise in reversed(self.return_advises):
                    return_advise(result, inst, self.callable_in_advise, *args, **kwargs)
                return result
            except Exception as error:
                for error_advise in reversed(self.error_advises):
                    error_advise(error, inst, self.callable_in_advise, *args, **kwargs)
                six.raise_from(error, None)
            finally:
                for after_advise in reversed(self.after_advises):
                    after_advise(inst, self.callable_in_advise, *args, **kwargs)

        return advised_method


class AdvisedBeanWrapper(object):
    """Wrap the bean with corresponding join points. Processed by `Aspect` instances.
    each callable member in the bean except the ones prefixed with "__" is wrapped to a joint point. The ones match some pointcuts are marked as "advised" and corresponding advises will be applied to the bean.
    """

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


class Advise(Annotation):
    type_before = 0
    type_after = 1
    type_after_return = 2
    type_after_error = 3

    def __init__(self, pointcut, advise_type, args_solver=False):
        self.pointcut = None
        self.advise_method = None
        self.advise_type = advise_type
        if not args_solver:
            self.args_solver = ArgsSolver.ignore
        elif type(args_solver) == bool:
            self.args_solver = ArgsSolver.keep
        else:
            if not isinstance(args_solver, ArgsSolver):
                raise Exception("parameter `args_solver` should be an instance of class `ArgsSolver`!")
            self.args_solver = args_solver
        super(Advise, self).__init__(pointcut)

    def after_set_target(self, target):
        pass

    def init_instance_annotate(self, pointcut):
        self.pointcut = pointcut

    def init_class_annotate(self):
        self.pointcut = Pointcut.all()

    def advise(self, join_point, aspect):
        if not self.pointcut.match(join_point):
            return
        join_point.advised = True
        advise = {
            Advise.type_before: "before_advises",
            Advise.type_after: "after_advises",
            Advise.type_after_return: "return_advises",
            Advise.type_after_error: "error_advises"
        }.get(self.advise_type)

        def aspect_wrapped_advise_method(*args, **kwargs):
            inst, fn, input_args, excluded_args = args[0], args[1], list(args[2:]), []
            if self.advise_type in [self.type_after_return, self.type_after_error]:
                inst, fn, input_args, excluded_args = args[1], args[2], list(args[3:]), list(args[0:1])
            solved_args, solved_kwargs = self.args_solver.target(inst, fn, input_args, kwargs)
            solved_args = excluded_args + solved_args
            if isinstance(self.target, classmethod) or isinstance(self.target, staticmethod):
                return self.target.__get__(aspect, type(aspect))(*solved_args, **solved_kwargs)
            return self.target(aspect, *solved_args, **solved_kwargs)

        getattr(join_point, advise).append(aspect_wrapped_advise_method)

        # def get_instance_member(self, target, instance):
        #     return self.advise_method


class Before(Advise):
    def __init__(self, pointcut=Pointcut.all(), args_solver=False):
        super(Before, self).__init__(pointcut, Advise.type_before, args_solver)


class After(Advise):
    def __init__(self, pointcut=Pointcut.all(), args_solver=False):
        super(After, self).__init__(pointcut, Advise.type_after, args_solver)


class AfterError(Advise):
    def __init__(self, pointcut=Pointcut.all(), args_solver=False):
        super(AfterError, self).__init__(pointcut, Advise.type_after_error, args_solver)


class AfterReturn(Advise):
    def __init__(self, pointcut=Pointcut.all(), args_solver=False):
        super(AfterReturn, self).__init__(pointcut, Advise.type_after_return, args_solver)


class ArgsSolver(Annotation):
    ignore = None
    keep = None
    method = None

    def __init__(self, fn):
        super(ArgsSolver, self).__init__(fn)

    def init_instance_annotate(self, fn):
        raise Exception("Does not allow instance annotate mode!")

    def after_set_target(self, target):
        pass

    def init_class_annotate(self):
        pass


def _no_argument(inst, fn, args, kwargs):
    return [], {}


def _keep_argument(inst, fn, args, kwargs):
    return [inst, fn] + args, kwargs


def _keep_method(inst, fn, args, kwargs):
    return [inst, fn], {}


ArgsSolver.ignore = ArgsSolver(_no_argument)
ArgsSolver.keep = ArgsSolver(_keep_argument)
ArgsSolver.method = ArgsSolver(_keep_method)
