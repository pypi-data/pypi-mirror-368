from textwrap import dedent
from typing import ClassVar, Optional, Generator

import yaml
from kubernetes.client import V1ObjectMeta, V1ConfigMap

from skapp.models.base import Base, YamlMixin
from skapp.utils import Prefixed, merge, LazyString
from pydantic import BaseModel


class HelmMeta(BaseModel):
    hook: str = None
    resource_policy: str = "keep"
    delete_policy: str = "before-hook-creation"
    hook_weight: int = 0


class Resource(Base, YamlMixin):
    name: str
    _kind = None
    _apis = {}
    helm: HelmMeta = None

    @classmethod
    def new(cls, **config):
        return cls(**config)

    @property
    def _resource_defaults(self):
        return {
            "kind": self._kind,
            "api_version": self.api_version,
            "metadata": self.metadata,
        }

    @property
    def _metadata_defaults(self):
        return {
            "name": Prefixed(self.name),
            "labels": {
                "app.kubernetes.io/part-of": LazyString("{{ stack.part_of }}"),
                "app.kubernetes.io/name": Prefixed(self.name),
                "app.kubernetes.io/instance": LazyString(
                    "{{ stack.instance or stack.environment}}"
                ),
                "app.kubernetes.io/component": LazyString("{{ stack.component }}"),
                "app.kubernetes.io/version": LazyString("{{ stack.app_version }}"),
                "environment": LazyString("{{ stack.environment }}"),
            },
        }

    @property
    def _helm_metadata(self) -> dict:
        if self.helm is None:
            return {}
        annotations = {}
        if self.helm.hook is not None:
            annotations["helm.sh/hook"] = self.helm.hook
        # if self.helm.resource_policy is not None:
        #     annotations["helm.sh/resource-policy"] = self.helm.resource_policy
        # # if self.helm.hook_weight is not None:
        # #     annotations["helm.sh/hook-weight"] = self.helm.hook_weight
        # if self.helm.delete_policy is not None:
        #     annotations["helm.sh/hook-delete-policy"] = self.helm.delete_policy

        return {"annotations": annotations}

    @property
    def metadata(self):
        return V1ObjectMeta(**dict(merge(self._metadata_defaults, self._helm_metadata)))

    @property
    def kubernetes_loader(self):
        api_name = self._api.__name__
        if api_name not in self._apis:
            self._apis[api_name] = self._api()
        api = self._apis[api_name]
        return getattr(api, self._api_loader)

    def kubernetes_resource(self, stack: "Stack" = None):
        name = Prefixed(self.name).render(context={"stack": stack})
        return self.kubernetes_loader(name=name)

    def get_from_kubernetes(self, stack: "Stack" = None):
        return self.kubernetes_resource(stack=stack)


class ResourceList(list):
    def generate(self, namespace: str = None) -> Generator:
        for el in self:
            for res in el.generate(namespace=namespace):
                yield res


class NamespacedResource(Resource):
    namespace: Optional[str] = "default"

    @property
    def _metadata_defaults(self):
        return dict(
            merge(
                super(NamespacedResource, self)._metadata_defaults,
                {"namespace": self.namespace},
            )
        )

    def kubernetes_resource(self, stack: "Stack" = None):
        name = Prefixed(self.name).render(context={"stack": stack})
        return self.kubernetes_loader(namespace=self.namespace, name=name)


class ConfigMap(NamespacedResource):
    data: dict

    api_version: ClassVar = "v1"
    _kind: ClassVar = "ConfigMap"
    _api_resource_class: ClassVar = V1ConfigMap

    def generate(self, namespace: str = None):
        if namespace is not None:
            self.namespace = namespace

        yield self._api_resource_class(
            **self._resource_defaults, data=self.data
        ).to_dict()

    @classmethod
    def new(cls, name: str, **config):
        return cls(name=name, data=config)


class ConfigMapList(ResourceList):
    item_class = ConfigMap
