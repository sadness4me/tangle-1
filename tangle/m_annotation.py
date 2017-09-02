#! /usr/bin/env python
# -*- coding: utf-8 -*-
import abc, types, six
import inspect


class Annotated(object):
    """This decorator is used to decorate a owner class of annotations, making the annotations contained in the owner class being aware of it."""
    def __new__(cls, annotated_cls):
        annotations = get_annotations(annotated_cls)
        for annotation in annotations:
            annotation.aware_owner_class(annotated_cls)
        return annotated_cls


class NotAnnotationClassError(TypeError):
    def __init__(self):
        super(NotAnnotationClassError, self).__init__("Input class object should be a subclass of Annotation!")


class NotAnnotationError(TypeError):
    def __init__(self):
        super(NotAnnotationError, self).__init__(
            "Only instance of Annotation class can be registered. Please check the input type!")


class AnnotationAlreadyRegisteredError(Exception):
    def __init__(self):
        super(AnnotationAlreadyRegisteredError, self).__init__(
            "An annotation with the same class is already registered!")


class AnnotationCallUsageError(Exception):
    def __init__(self):
        super(AnnotationCallUsageError, self).__init__("You should not explicitly invoke an annotation instance call!")


def get_annotations(obj):
    if inspect.isclass(obj):
        return _get_annotations_from_class(obj)
    return _get_annotations_from_class(type(obj))


def _get_annotations_from_class(cls):
    return list(member for (name, member) in inspect.getmembers(cls, lambda member: isinstance(member, Annotation)))


@six.add_metaclass(abc.ABCMeta)  # this class should not be instantiated, should only instantiate subclasses.
class Annotation(object):
    """
    There are two annotating models: class annotating and instance annotating.
    class annotating means that the annotator (a.k.a. decorator) is an annotation class (i.e. a subclass of `Annotation`).
    instance annotating means that the annotator is a instance of an annotation class.
    To support both of the models, the initialization method of annotation classes should be implemented a little bit tricky. You should leave the `__init__` method alone by not overriding it, and implement the `init_instance_annotate` abstract method instead. Also, in case you want to utilize the annotating target in initialization, you can implement the `after_set_target` abstract method which is an event callback. It is promised that `self.target` is set when `after_set_target` is invoked.

    """

    def __init__(self, obj, *args):
        self.target = None
        self.annotations = []
        self.annotations_look_up = {}
        self.register_annotation(self)
        self._owner_registered = False
        if isinstance(obj, Annotation):
            self.init_annotation(obj)
            self.init_class_annotate()
            return
        if inspect.isfunction(obj) or isinstance(obj, classmethod) or isinstance(obj, staticmethod):
            self.init_function(obj)
            self.init_class_annotate(*args)
            return
        self.init_instance_annotate(obj, *args)

    def init_annotation(self, annotation):
        self.target = annotation.target
        self.annotations_look_up = annotation.annotations_look_up
        self.annotations = annotation.annotations
        self.after_set_target(annotation.target)

    def init_function(self, fn):
        self.target = fn
        self.after_set_target(fn)

    @abc.abstractmethod
    def init_class_annotate(self, *args):
        pass

    @abc.abstractmethod
    def init_instance_annotate(self, obj, *args):
        """The actual init method which should be implemented by subclasses of `Annotation`.

        It is invoked in `__init__` of the base class `Annotation`.
        It should support calls with no arguments (i.e. `init_instance_annotate()`) to support class annotating.

        :param args: it depends on the inputs (`*init_args, **kwargs`) of `__init__`:

            1. If `len(init_args)>0 and isinstance(init_args[0], Annotation)`, that is, the target of the annotation is also an annotation, the inputs `args = init_args[1:]`
            2. If `len(init_args)>0 and inspect.isfunction(init_args[0])`, that is, the target of the annotation is a class member of the owner class. the inputs `args = init_args[1:]`
            3. Otherwise `args = init_args`

        :return: should not return
        """
        pass

    @abc.abstractmethod
    def after_set_target(self, target):
        """
        :return: should not return
        """
        pass

    def register_annotation(self, annotation):
        if not isinstance(annotation, Annotation):
            raise NotAnnotationError()
        if type(annotation) in self.annotations_look_up:
            raise AnnotationAlreadyRegisteredError()
        self.annotations_look_up[type(annotation)] = len(self.annotations)
        self.annotations.append(annotation)

    def aware_owner_class(self, owner_class):
        """A lifecycle hook to trigger when the owner class (i.e. the class in which this annotation is contained) is created. Subclasses of :class:`Annotation` which want to be aware of the owner class should implement this method, and cooperate with :class:`Annotated`."""
        pass

    def get_annotation(self, klass):
        if klass not in self.annotations_look_up:
            return None
        return self.annotations[self.annotations_look_up[klass]]

    def __call__(self, target):
        if isinstance(target, Annotation):
            self.init_annotation(target)
        elif isinstance(target, types.FunctionType) or isinstance(target, classmethod) or isinstance(target, staticmethod):
            self.init_function(target)
        else:
            raise AnnotationCallUsageError()
        return self

    def get_instance_member(self, target, instance):
        if isinstance(target, staticmethod) or isinstance(target, classmethod):
            return target.__get__(instance, type(instance))
        return types.MethodType(target, instance)

    def __get__(self, instance, owner):
        if not instance:
            return self
        return self.get_instance_member(self.target, instance)
