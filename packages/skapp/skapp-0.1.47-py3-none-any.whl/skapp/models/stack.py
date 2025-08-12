import importlib
import os
from distutils.version import LooseVersion, StrictVersion
from enum import Enum
from subprocess import STDOUT, CalledProcessError, check_output
from tempfile import TemporaryDirectory
from typing import List, Optional, Generator

import kubernetes
import yaml
from kubernetes import client, config
from pydantic import validator

from skapp.models.base import Base, YamlMixin
from skapp.models.pod_controllers import (
    CronjobList,
    DaemonsetList,
    DeploymentList,
    IngressList,
    StatefulsetList,
    VolumesList,
    JobList,
)
from skapp.models.build import Builds
from skapp.models.resource import Resource, ResourceList, ConfigMapList, ConfigMap
from skapp.utils import dict_to_yaml, load_yaml_files, parse_yaml, merge


def load_plugin(name):
    name = name.replace(":", ".")
    return importlib.import_module(f"{name}")


def load_plugins(defn):
    patch = {}
    to_pop = []
    for k, conf in defn.items():
        if ":" in k:
            # Couldn't pop while iterating
            to_pop.append(k)

            plugin = load_plugin(k)

            patch = dict(merge(patch, plugin.handler(conf)))

    for k in to_pop:
        defn.pop(k)

    if patch:
        defn = dict(merge(defn, patch))

    return defn


class Stack(Base, YamlMixin):
    class Config:
        arbitrary_types_allowed = True

    name: str
    environment: Optional[str]
    instance: Optional[str]
    description: Optional[str]
    version: Optional[StrictVersion]
    app_version: Optional[LooseVersion]
    deployments: Optional[DeploymentList] = []
    daemonsets: Optional[DaemonsetList] = []
    statefulsets: Optional[StatefulsetList] = []
    cronjobs: Optional[CronjobList] = []
    jobs: Optional[JobList] = []
    configs: Optional[ConfigMapList] = []
    volumes: Optional[VolumesList] = []
    ingress: Optional[IngressList] = []
    values: Optional[list[dict[str, str]]] = []
    custom: Optional[dict[str, dict]] = {}
    build: Optional[Builds] = {}

    @property
    def part_of(self):
        parts = self.name.split("-")
        return parts[0]

    @property
    def component(self):
        parts = self.name.split("-")
        if len(parts) > 1:
            return parts[1]
        return parts[0]

    @staticmethod
    def inject_defaults(defn):
        defaults = defn.pop("defaults", {})
        if defaults:
            for rt in ["deployments", "daemonsets", "statefulsets", "cronjobs", "jobs"]:
                for r in defn.get(rt, {}).values():
                    if r.get(".nodefaults"):
                        continue

                    for k, dv in defaults.items():
                        # Add if not present
                        if k not in r:
                            r[k] = dv
                            continue

                        # Merge only if it's a dict
                        if isinstance(r[k], dict):
                            r[k] = dict(merge(dv, r[k]))
        return defn

    @staticmethod
    def new(name: str, definition: str, environment: Optional[str] = "dev") -> "Stack":
        defn = load_plugins(parse_yaml(definition))
        defn = Stack.inject_defaults(defn)
        return Stack(name=name, environment=environment, **defn)

    @staticmethod
    def from_files(
        name: str,
        files: List[str],
        environment: Optional[str] = "dev",
        version: Optional[StrictVersion] = None,
        app_version: Optional[LooseVersion] = None,
        values: list[dict[str, str]] = {},
    ) -> "Stack":
        defn = dict(merge(load_yaml_files(*files), values))
        defn = Stack.inject_defaults(defn)
        defn = load_plugins(defn)

        if version:
            defn["version"] = version

        if app_version:
            defn["app_version"] = app_version

        return Stack(name=name, environment=environment, **defn)

    @property
    def chart(self):
        return HelmChart(stack=self, template_generator=self.yaml_files)

    def to_yaml(self, context: Optional[dict] = None) -> str:
        return super(Stack, self).to_yaml(
            context={"stack": self} if context is None else context
        )

    @property
    def get_all_resources(self):
        for k in self.__annotations__.keys():
            x = getattr(self, k)
            if isinstance(x, Resource):
                yield x
            if isinstance(x, ResourceList):
                for res in x:
                    yield res

    def generate(self, namespace: str = None):
        for k in self.__annotations__.keys():
            x = getattr(self, k)
            if hasattr(x, "generate"):
                for res in x.generate(namespace=namespace):
                    # breakpoint()
                    yield res
            elif k == "custom":
                for name, config in x.items():
                    config["metadata"][
                        "name"
                    ] = f"{self.name}-{config['metadata']['name']}"
                    yield config
                    # foo = dict_to_yaml(config, context={"stack": self})
                    # breakpoint()
                    # yield foo

    @validator(
        "deployments",
        "daemonsets",
        "statefulsets",
        "configs",
        "cronjobs",
        "jobs",
        "ingress",
        "build",
        pre=True,
        allow_reuse=True,
        check_fields=False,
    )
    def validate_stack_fields(cls, value, field):
        if isinstance(value, list):
            return field.type_(value)

        if isinstance(value, dict):
            dl = field.type_()
            for name, config in value.items():
                if isinstance(config, field.type_.item_class):
                    dl.append(config)
                else:
                    dl.append(field.type_.item_class.new(name=name, **config))

            return dl

        raise ValueError(f"Invalid value for {field.type_.__name__}")


class HelmChart(Base, YamlMixin):
    class TypeEnum(str, Enum):
        application = "application"
        library = "library"

    stack: Stack
    type: TypeEnum = TypeEnum.application
    description: Optional[str] = "A Helm chart for Kubernetes created dynamically"

    def generate(self, namespace: str = None):
        return self.stack.generate(namespace=namespace)

    def generate_files(self, namespace: str = None) -> Generator:
        yield self.generate_info_file()
        for filename, template in self.yaml_files(
            namespace=namespace, context={"stack": self.stack, "namespace": namespace}
        ):
            yield f"templates/{filename}", template

    def generate_info_file(self):
        return "Chart.yaml", dict_to_yaml(
            {
                "name": self.stack.name,
                "description": self.stack.description,
                "version": self.stack.version or "0.1.0",
                "app_version": self.stack.app_version or self.stack.version or "0.1.0",
            },
            context=None,
        )

    def dump(self, folder, namespace: str = None) -> None:
        for filename, content in self.generate_files(namespace=namespace):
            absolute_filename = os.path.join(folder, filename)
            if "/" in filename:
                file_folder = absolute_filename.rsplit("/", 1)[0]
                os.makedirs(file_folder, exist_ok=True)

            with open(absolute_filename, "w") as f:
                f.write(content)

    def check_compatibility(self):
        server = client.VersionApi().get_code()
        library_version = StrictVersion(kubernetes.__version__)
        assert abs(int(server.minor) - library_version.version[0]) <= 1, (
            f"kubernetes library {library_version} is not "
            f"compatible with server version {server.git_version}"
        )

    def rollout(
        self,
        location: Optional[str] = None,
        namespace: str = None,
        create_namespace=False,
    ) -> "HelmRelease":
        # Load kubernetes config
        config.load_kube_config()

        self.check_compatibility()

        def _rollout(loc: str) -> HelmRelease:
            # print(loc)
            self.dump(loc, namespace=namespace)
            # breakpoint()
            self.exec(
                self.rollout_command(
                    loc, namespace=namespace or None, create_namespace=create_namespace
                )
            )

        if location:
            return _rollout(location)

        with TemporaryDirectory() as location:
            return _rollout(location)

    def rollout_command(self, location, namespace=None, create_namespace=False):
        cmd = ["helm", "upgrade", "--install", "--force", self.stack.name, location]

        if namespace:
            cmd += ["--namespace", namespace]

        if create_namespace:
            cmd += ["--create-namespace"]

        return cmd

    def uninstall(self):
        return self.exec(["helm", "delete", self.stack.name])

    def exec(self, command: str):
        def _log(output):
            for line in output.decode("utf-8").splitlines():
                print(line)

        try:
            _log(check_output(command, stderr=STDOUT))
        except CalledProcessError as e:
            _log(e.output)
            raise e

    def get_kubernetes_resources(self):
        for res in self.stack.get_all_resources:
            yield res.get_from_kubernetes(stack=self.stack)


class HelmRelease(Base):
    resource_definitions: dict

    @classmethod
    def load(cls, name) -> "HelmRelease":
        command = ["helm", "get", "manifest", name]
        try:
            yaml_resources = check_output(command, stderr=STDOUT)
        except CalledProcessError as e:
            print(e.output)
            raise e

        return HelmRelease(
            resource_definitions={
                f"{res['kind']}/{res['metadata']['name']}": res
                for res in yaml.safe_load_all(yaml_resources)
            }
        )

    def refresh(self):
        for name, resource in self.resource_definitions.keys():
            pass
