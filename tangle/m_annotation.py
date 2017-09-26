#! /usr/bin/env python
# -*- coding: utf-8 -*-
import types
import collections
import inspect
import itertools


class Annotated(object):
    """This decorator is used to decorate a owner class of annotations, making the annotations contained in the owner class being aware of it."""

    key_annotations = "_tangle_annotations"

    def __new__(cls, klass):
        annotations = [
            entry for entry in klass.__dict__.values()
            if isinstance(entry, Annotation) and not entry.owner_class
        ]
        for annotation in annotations:
            annotation.set_owner_class(klass)
        ancestor_annotations = list(itertools.chain(*list(
            getattr(base, Annotated.key_annotations) for base in klass.__bases__
            if hasattr(base, Annotated.key_annotations)
        )))
        setattr(
            klass,
            Annotated.key_annotations,
            ancestor_annotations + sorted(annotations, key=lambda x: x.create_order)
        )
        return klass


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


def get_annotations(obj, annotation_cls=None):
    if inspect.isclass(obj):
        return _get_annotations_from_class(obj, annotation_cls)
    return _get_annotations_from_class(type(obj), annotation_cls)


def _get_annotations_from_class(cls, annotation_cls):
    annotations = getattr(cls, Annotated.key_annotations, [])
    if not annotation_cls:
        return annotations
    return list(filter(lambda member: isinstance(member, annotation_cls), annotations))


class Annotation(object):
    _create_order = 0

    """
    There are two annotating models: class annotating and instance annotating.
    class annotating means that the annotator (a.k.a. decorator) is an annotation class (i.e. a subclass of `Annotation`).
    instance annotating means that the annotator is a instance of an annotation class.
    To support both of the models, the initialization method of annotation classes should be implemented a little bit tricky. You should leave the `__init__` method alone by not overriding it, and implement the `init_instance_annotate` abstract method instead. Also, in case you want to utilize the annotating target in initialization, you can implement the `after_set_target` abstract method which is an event callback. It is promised that `self.target` is set when `after_set_target` is invoked.

    """

    def __init__(self):
        assert not type(self) == Annotation
        self.target = None
        self.create_order = Annotation._create_order
        Annotation._create_order = Annotation._create_order + 1
        self.annotations = collections.OrderedDict()
        self.owner_class = None
        self.register_annotation(self)

    def init_annotation(self, annotation):
        self.target = annotation.target
        self.annotations.update(annotation.annotations)
        self.after_set_target(annotation.target)

    def init_function(self, target):
        self.target = target
        self.after_set_target(target)

    def after_set_target(self, target):
        """
        :return: should not return
        """

    def register_annotation(self, annotation):
        if not isinstance(annotation, Annotation):
            raise NotAnnotationError()
        if type(annotation) in self.annotations:
            raise AnnotationAlreadyRegisteredError()
        self.annotations[type(annotation)] = annotation

    def aware_owner_class(self, owner_class):
        """A lifecycle hook to trigger when the owner class (i.e. the class in which this annotation is contained) is created. Subclasses of :class:`Annotation` which want to be aware of the owner class should implement this method, and cooperate with :class:`Annotated`."""
        pass

    def set_owner_class(self, owner_class):
        self.owner_class = owner_class
        self.aware_owner_class(owner_class)

    def get_annotation(self, klass):
        if klass not in self.annotations:
            return None
        return self.annotations[klass]

    def get_annotations(self):
        return self.annotations.values()

    def __call__(self, target):
        if isinstance(target, Annotation):
            self.init_annotation(target)
        elif isinstance(target, types.FunctionType) or isinstance(target, classmethod) or isinstance(target,
                                                                                                     staticmethod):
            self.init_function(target)
        else:
            raise AnnotationCallUsageError()
        return self

    def get_featured_target(self):
        return self.target

    def get_instance_member(self, instance):
        target = self.get_featured_target()
        if isinstance(target, staticmethod) or isinstance(target, classmethod):
            return target.__get__(instance, type(instance))
        return types.MethodType(target, instance)

    def get_class_member(self, cls):
        target = self.get_featured_target()
        if isinstance(target, staticmethod) or isinstance(target, classmethod):
            return target.__get__(None, cls)
        return target

    def __get__(self, instance, owner):
        if not instance:
            return self.get_class_member(owner)
        return self.get_instance_member(instance)

    def is_annotation(self, cls):
        return True in (isinstance(x, cls) for x in self.annotations)

    @classmethod
    def get_annotations_from_owner(cls, owner):
        return filter(lambda x: x.is_annotation(cls), get_annotations(owner))
