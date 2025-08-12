from argparse import Namespace
import json
import os
from re import sub
from urllib.parse import urlparse

import requests
import yaml
from jinja2 import BaseLoader, Environment


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def merge(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(merge(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't merge it.
                # Value from second dict overrides one in first, then we
                # move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert
                # you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def parse_yaml(content):
    result = {}
    for partial in yaml.safe_load_all(content):
        if not partial:
            continue

        include = partial.pop("include", [])
        included = {}
        for child in include:
            child_dict = dict(load_yaml_files(child))
            included = dict(merge(included, child_dict))

        if include:
            partial = dict(merge(included, partial))

        result = dict(merge(result, partial))

    return {k: v for k, v in result.items() if not k.startswith(".")}


def load_yaml_files(*args):
    def load_yaml_file(filepath) -> str:
        if uri_validator(filepath):
            return requests.get(filepath).content

        with open(filepath) as f:
            return f.read()

    def _load_all_files():
        for filepath in args:
            yield load_yaml_file(filepath)

    return parse_yaml("\n---\n".join(_ for _ in _load_all_files() if _))


def camelize(key) -> str:
    """camelCase given key"""
    if key in ["shared_preload_libraries"]:
        return key

    if "_" not in key:
        return key
    enumerated = enumerate(key.lower().split("_"))
    return "".join(_ if i == 0 else _.capitalize() for i, _ in enumerated)


def snakelize(s):
    return "_".join(
        sub(
            "([A-Z][a-z]+)", r" \1", sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()


def dict_to_yaml(data, context: dict = None):
    def _format(res):
        if isinstance(res, dict):
            new = {}
            for k, v in res.items():
                if "{{" in k and "}}" in k:
                    k = _format(LazyString(k))

                if v is not None:
                    new[camelize(k)] = _format(v)

            return new

        elif isinstance(res, list):
            return [_format(_) for _ in res]

        elif isinstance(res, LazyString):
            return res.render(context)

        elif isinstance(res, str) and "{{" in res and "}}" in res:
            return _format(LazyString(res))

        elif hasattr(res, "to_dict"):
            return _format(res.to_dict())

        return res

    return yaml.safe_dump(_format(data))


class Context(object):
    def __init__(self, context):
        self.context = context

    def resolve(self, name):
        return name

    def prefix(self, name):
        if "{{" in name and "}}" in name:
            name = LazyString(name).render(self.context)

        if self.context["stack"].component == name:
            return self.context["stack"].name

        return f"{self.context['stack'].name}-{name}"

    def fqdn(self, name):
        return self.prefix(name + ".{{- .Release.Namespace -}}.svc.cluster.local")

    def helm(self, template):
        return "{{ " + template + " }}"

    def envvar(self, name):
        return os.environ.get(name)

    def product_namespace(self, product):
        stack: "Stack" = self.context["stack"]
        if stack.environment == "prod":
            # All products have a prod namespace named after themselves
            return product
        if stack.environment == "dev":
            # Dev environments should point to staging services, there's no persisten dev product instances
            return "staging"

        # Every otehr environment should point to the environment name, ideal for isolated instances
        return stack.environment


class LazyString(str):

    context: object = None

    def get_template(self):
        return self

    def render(self, context):
        rtemplate = Environment(loader=BaseLoader).from_string(self.get_template())
        images = {_.name: _.tag for _ in context["stack"].build}
        context = Context(context)

        return rtemplate.render(
            resolve=context.resolve,
            prefix=context.prefix,
            fqdn=context.fqdn,
            helm=context.helm,
            envvar=context.envvar,
            product_namespace=context.product_namespace,
            images=images,
            **context.context,
        )


class Prefixed(LazyString):
    def get_template(self):
        return "{{ prefix('%s') }}" % self


class Fqdn(LazyString):
    def get_template(self):
        return "{{ fqdn(prefix('%s')) }}" % self
