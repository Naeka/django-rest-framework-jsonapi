from __future__ import unicode_literals

from django.conf import settings
from django.utils.encoding import force_text
from rest_framework.compat import importlib
from rest_framework.serializers import ListSerializer, ManyRelatedField
from inflection import underscore, dasherize


def get_serializer(serializer):
    if isinstance(serializer, ListSerializer):
        return serializer.child
    if isinstance(serializer, ManyRelatedField):
        return serializer.child_relation
    return serializer


def get_resource_type(model):
    RESOURCE_TYPE_EXTRACTOR = getattr(
        settings, "REST_FRAMEWORK", None).get("RESOURCE_TYPE_EXTRACTOR", None)
    if RESOURCE_TYPE_EXTRACTOR:
        try:
            parts = RESOURCE_TYPE_EXTRACTOR.split(".")
            module_path, class_name = ".".join(parts[:-1]), parts[-1]
            module = importlib.import_module(module_path)
            return getattr(module, class_name)(model)
        except (ImportError, AttributeError) as e:
            msg = ("Could not import '{}' for API setting "
                   "'RESOURCE_TYPE_EXTRACTOR'. {}: {}.".format(
                       RESOURCE_TYPE_EXTRACTOR, e.__class__.__name__, e))
            raise ImportError(msg)
    return force_text(dasherize(underscore(model._meta.object_name)).strip())


def import_serializer(path):
    try:
        parts = path.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)()
    except (ImportError, AttributeError):
        raise ImportError("Could not import serializer '{}' from {}".format(
            class_name, path))
