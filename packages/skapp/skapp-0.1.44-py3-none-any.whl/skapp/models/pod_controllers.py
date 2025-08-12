import json
import os
from enum import Enum
from pprint import pprint
from typing import Generator, List, Optional, TypedDict, Union

from kubernetes import client
from kubernetes.client import (
    V1ConfigMapVolumeSource,
    V1Container,
    V1ContainerPort,
    V1EnvVar,
    V1EnvVarSource,
    V1HostPathVolumeSource,
    V1JobSpec,
    V1LabelSelector,
    V1LocalObjectReference,
    V1ObjectFieldSelector,
    V1ObjectMeta,
    V1PersistentVolumeClaimVolumeSource,
    V1Pod,
    V1PodSpec,
    V1PodTemplateSpec,
    V1PolicyRule,
    V1Role,
    V1RoleBinding,
    V1RoleRef,
    V1SecretKeySelector,
    V1Service,
    V1ServiceAccount,
    V1ServicePort,
    V1ServiceSpec,
    V1Volume,
    V1VolumeMount,
)
from kubernetes.client.models.rbac_v1_subject import RbacV1Subject
from rich import print

from skapp.models.base import Base
from skapp.models.resource import NamespacedResource, ResourceList
from skapp.utils import Fqdn, LazyString, Prefixed, merge


class Volumes(Base):
    pass


class VolumesList(ResourceList):
    pass


class Mounts(Base):
    pass


class MountsList(ResourceList):
    pass


class BasePodController(NamespacedResource):
    _api = client.AppsV1Api
    api_version: str = "apps/v1"
    image: str
    entrypoint: Optional[Union[list, None]] = None
    command: Optional[Union[list, None]] = None
    environment: Optional[dict]
    mounts: Optional[dict[str, dict]]
    expose: Optional[dict]
    image_pull_secrets: Optional[Union[list, None]] = None
    node_selector: Optional[dict[str, str]] = None
    restart_policy: str = "Always"
    tolerations: Optional[Union[list, None]] = None
    probes: Optional[dict] = None
    resources: Optional[dict] = None

    @property
    def _pod_controller_defaults(self):
        return dict(
            selector=self.pod_selector,
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels=self.metadata.labels),
                spec=V1PodSpec(
                    containers=self.containers,
                    tolerations=self.all_tolerations,
                    **self.pod_spec_extras,
                ),
            ),
        )

    @property
    def all_tolerations(self):
        if self.tolerations is None:
            return None

        # Tolerations is a list of strings in the form of "key=value:effect" or "key:effect"
        tolerations = []
        for tol in self.tolerations:
            if ":" in tol:
                key, effect = tol.split(":")
                tolerations.append(
                    client.V1Toleration(key=key, operator="Equal", effect=effect)
                )
            else:
                key, value, effect = tol.split("=")
                tolerations.append(
                    client.V1Toleration(
                        key=key, operator="Equal", value=value, effect=effect
                    )
                )

        return tolerations

    @property
    def pod_selector(self) -> V1LabelSelector:
        k8s_labels = ["part-of", "name", "instance", "component", "environment"]

        return V1LabelSelector(
            match_labels={
                k: v
                for k, v in self.metadata.labels.items()
                if k in [f"app.kubernetes.io/{_}" for _ in k8s_labels]
            }
        )

    @property
    def containers(self):
        return [
            V1Container(
                args=self.command,
                command=self.entrypoint,
                name=self.name,
                image=self.image,
                env=self._env,
                **self._container_extras,
            )
        ]

    @property
    def _env(self):
        def _var(args) -> V1EnvVar:
            k, v = args
            if isinstance(v, str):
                return dict(name=k, value=v)

            elif isinstance(v, dict):
                if "autosecret" in v:
                    v = {"secret": Prefixed(f"{self.name}-autosecret")}

                if "secret" in v:
                    secret = v["secret"]
                    _name = secret if isinstance(secret, str) else secret["name"]
                    name = (
                        _name
                        if isinstance(secret, dict) and secret.get("external", False)
                        else Prefixed(_name)
                    )
                    key = k if isinstance(secret, str) else secret["key"]

                    return V1EnvVar(
                        name=k,
                        value_from=V1EnvVarSource(
                            secret_key_ref=V1SecretKeySelector(key=key, name=name)
                        ),
                    )

                if "template" in v:
                    return {"name": k, "value": LazyString(v["template"])}

        service_name = LazyString(
            "{{ stack.part_of + '-' + stack.component +('-"
            + self.name
            + "' if '"
            + self.name
            + "' != stack.component else '')}}"
        )
        env = (
            [
                V1EnvVar(name="SERVICE_NAME", value=service_name),
                V1EnvVar(name="OTEL_SERVICE_NAME", value=service_name),
            ]
            + (list(map(_var, self.environment.items())) if self.environment else [])
            + [
                V1EnvVar(
                    name="POD_IP",
                    value_from=V1EnvVarSource(
                        field_ref=V1ObjectFieldSelector(field_path="status.podIP")
                    ),
                ),
                V1EnvVar(
                    name="HOST_IP",
                    value_from=V1EnvVarSource(
                        field_ref=V1ObjectFieldSelector(field_path="status.hostIP")
                    ),
                ),
                V1EnvVar(
                    name="NODE_NAME",
                    value_from=V1EnvVarSource(
                        field_ref=V1ObjectFieldSelector(field_path="spec.nodeName")
                    ),
                ),
                V1EnvVar(
                    name="RELEASE", value=LazyString("{{ helm('.Release.Name') }}")
                ),
                V1EnvVar(
                    name="ENVIRONMENT", value=LazyString("{{ stack.environment }}")
                ),
                V1EnvVar(
                    name="INSTANCE",
                    value=LazyString("{{ stack.instance or stack.environment }}"),
                ),
            ]
        )

        return list(filter(lambda x: x is not None, env))

    @property
    def _pod_controller_extras(self):
        return {}

    @property
    def pod_spec_extras(self):
        extras = {"restart_policy": self.restart_policy}

        if self.node_selector:
            extras["node_selector"] = self.node_selector
        if self.image_pull_secrets:
            extras["image_pull_secrets"] = [
                V1LocalObjectReference(name=_) for _ in self.image_pull_secrets
            ]

        if self.mounts:
            extras["volumes"] = []
            for cm, path in self.mounts.get("config", {}).items():
                extras["volumes"].append(
                    V1Volume(
                        name=Prefixed(cm),
                        config_map=V1ConfigMapVolumeSource(name=Prefixed(cm)),
                    )
                )

            for host_path, path in self.mounts.get("host", {}).items():
                extras["volumes"].append(
                    V1Volume(
                        host_path=V1HostPathVolumeSource(path=host_path),
                        name=host_path.replace("/", ""),
                    )
                )

            for pvname, path in self.mounts.get("pvc", {}).items():
                extras["volumes"].append(
                    V1Volume(
                        persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
                            claim_name=Prefixed(pvname)
                        ),
                        name=pvname,
                    )
                )

        return extras

    @property
    def _container_extras(self):
        extras = {}

        if self.resources:
            extras["resources"] = client.V1ResourceRequirements(**self.resources)

        if self.mounts:
            extras["volume_mounts"] = []
            for cm, path in self.mounts.get("config", {}).items():
                extras["volume_mounts"].append(
                    V1VolumeMount(mount_path=path, name=Prefixed(cm))
                )

            for host_path, path in self.mounts.get("host", {}).items():
                extras["volume_mounts"].append(
                    V1VolumeMount(
                        mount_path=path,
                        name=host_path.replace("/", ""),
                    )
                )

            for pvname, path in self.mounts.get("pvc", {}).items():
                extras["volume_mounts"].append(
                    V1VolumeMount(
                        mount_path=path,
                        name=pvname,
                    )
                )

        if self.expose:
            if self.expose["ports"]:
                extras["ports"] = [
                    V1ContainerPort(
                        container_port=port, protocol="TCP", name=f"port-{port}"
                    )
                    for port in self.expose["ports"]
                ]

        if self.probes:
            for kind, check in self.probes.items():
                assert kind in ["liveness", "readiness", "startup"]
                extras[f"{kind}_probe"] = client.V1Probe(**check)

        return extras

    @property
    def _api_resource_class(self):
        raise NotImplementedError()

    @property
    def _api_spec_class(self):
        raise NotImplementedError()

    def generate(self, namespace: str = None) -> Generator:
        # TODO: implement patch contextmanager
        if self.namespace is not None:
            self.namespace = namespace

        yield self._api_resource_class(
            **self._resource_defaults,
            spec=self._api_spec_class(
                **self._pod_controller_defaults, **self._pod_controller_extras
            ),
        ).to_dict()

        for el in self.generate_autosecret():
            if el is not None:
                yield el.to_dict()

    def generate_autosecret(self) -> Generator:
        if self.environment is None:
            return

        variables = []

        for var, val in self.environment.items():
            if isinstance(val, dict):
                if "autosecret" in val:
                    variables.append({"name": var, **val["autosecret"]})

        if variables:
            autosecret_name = f"{self.name}-autosecret"
            secret = {
                "secret": f"{{{{ prefix('{autosecret_name}') }}}}",
                "passwords": variables,
            }

            metadata = self.metadata
            metadata.name = Prefixed(autosecret_name)

            yield V1Role(
                api_version="rbac.authorization.k8s.io/v1",
                kind="Role",
                metadata=V1ObjectMeta(name=Prefixed("autosecret")),
                rules=[
                    V1PolicyRule(
                        api_groups=[""],
                        resources=["secrets"],
                        verbs=["get", "list", "patch", "create"],
                    )
                ],
            )

            yield V1ServiceAccount(
                api_version="v1",
                kind="ServiceAccount",
                metadata=V1ObjectMeta(name=Prefixed("autosecret")),
            )

            yield V1RoleBinding(
                api_version="rbac.authorization.k8s.io/v1",
                kind="RoleBinding",
                metadata=V1ObjectMeta(name=Prefixed("autosecret")),
                role_ref=V1RoleRef(
                    kind="Role",
                    name=Prefixed("autosecret"),
                    api_group="rbac.authorization.k8s.io",
                ),
                subjects=[
                    RbacV1Subject(
                        kind="User",
                        name=LazyString(
                            "system:serviceaccount:{{ helm('.Release.Namespace') }}:{{ prefix('autosecret') }}"
                        ),
                        api_group="rbac.authorization.k8s.io",
                    )
                ],
            )

            yield V1Pod(
                api_version="v1",
                kind="Pod",
                metadata=metadata,
                spec=V1PodSpec(
                    service_account=Prefixed("autosecret"),
                    restart_policy="Never",
                    containers=[
                        V1Container(
                            image="dmonroy/autosecret",
                            image_pull_policy="Always",
                            name="autosecret",
                            env=[
                                V1EnvVar(
                                    name="SECRETS",
                                    value=LazyString(json.dumps([secret])),
                                ),
                                V1EnvVar(
                                    name="KUBERNETES_NAMESPACE",
                                    value_from=V1EnvVarSource(
                                        field_ref=V1ObjectFieldSelector(
                                            field_path="metadata.namespace"
                                        )
                                    ),
                                ),
                            ],
                        )
                    ],
                ),
            )


class WorkloadPodController(BasePodController):
    def generate(self, namespace: str = None) -> Generator:
        yield from super().generate(namespace)

        svc = self.generate_service()
        if svc is not None:
            yield svc.to_dict()

    def generate_service(self) -> Optional[V1Service]:
        if self.expose:
            if self.expose["ports"]:
                return V1Service(
                    api_version="v1",
                    kind="Service",
                    metadata=self.metadata,
                    spec=V1ServiceSpec(
                        selector=self.pod_selector.match_labels,
                        type="ClusterIP",
                        ports=[
                            V1ServicePort(
                                name=f"port-{port}", port=port, target_port=port
                            )
                            for port in self.expose["ports"]
                        ],
                    ),
                )


class JobController(BasePodController):
    api_version: str = "batch/v1"
    restart_policy: str = "Never"
    backoff_limit: int = 1

    @property
    def _pod_controller_defaults(self):
        return dict(
            backoff_limit=self.backoff_limit,
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(labels=self.metadata.labels),
                spec=V1PodSpec(
                    containers=self.containers,
                    **self.pod_spec_extras,
                ),
            ),
        )


class ReplicaSetController(WorkloadPodController):
    replicas: int = 1

    @property
    def _pod_controller_defaults(self):
        return dict(
            merge(
                super(ReplicaSetController, self)._pod_controller_defaults,
                {"replicas": self.replicas},
            )
        )


class Deployment(ReplicaSetController):
    _kind = "Deployment"
    _api_resource_class = client.V1Deployment
    _api_spec_class = client.V1DeploymentSpec
    _api_loader = "read_namespaced_deployment"


class Daemonset(BasePodController):
    _kind = "DaemonSet"
    _api_resource_class = client.V1DaemonSet
    _api_spec_class = client.V1DaemonSetSpec
    _api_loader = "read_namespaced_daemon_set"

    def generate(self, namespace: str = None) -> Generator:
        yield from super().generate(namespace)

        svc = self.generate_service()
        if svc is not None:
            yield svc.to_dict()

    def generate_service(self) -> Optional[V1Service]:
        if self.expose:
            if self.expose["ports"]:
                return V1Service(
                    api_version="v1",
                    kind="Service",
                    metadata=self.metadata,
                    spec=V1ServiceSpec(
                        selector=self.pod_selector.match_labels,
                        type="ClusterIP",
                        ports=[
                            V1ServicePort(
                                name=f"port-{port}", port=port, target_port=port
                            )
                            for port in self.expose["ports"]
                        ],
                    ),
                )


class Statefulset(ReplicaSetController):
    _kind = "StatefulSet"
    _api_resource_class = client.V1StatefulSet
    _api_spec_class = client.V1StatefulSetSpec
    _api_loader = "read_namespaced_stateful_set"

    @property
    def _pod_controller_extras(self):
        return {"service_name": Prefixed(self.name)}


class ConcurrencyPolicy(Enum):
    ALLOW = "Allow"
    FORBID = "Forbid"
    REPLACE = "Replace"


class CronJob(JobController):
    _kind = "CronJob"
    _api_resource_class = client.V1CronJob
    _api_spec_class = client.V1CronJobSpec
    _api_loader = "read_namespaced_cron_job"

    schedule: str = None
    concurrency_policy: ConcurrencyPolicy = ConcurrencyPolicy.ALLOW
    successful_jobs_history_limit: int = 1
    failed_jobs_history_limit: int = 1
    starting_deadline_seconds: int = None

    @property
    def _pod_controller_defaults(self):
        return {
            "job_template": {"spec": super(CronJob, self)._pod_controller_defaults},
            "schedule": self.schedule,
            "concurrency_policy": self.concurrency_policy.value,
            "successful_jobs_history_limit": self.successful_jobs_history_limit,
            "failed_jobs_history_limit": self.failed_jobs_history_limit,
            "starting_deadline_seconds": self.starting_deadline_seconds,
        }


class Job(JobController):
    _kind = "Job"
    _api_resource_class = client.V1Job
    _api_spec_class = client.V1JobSpec
    _api_loader = "read_namespaced_job"


class DeploymentList(ResourceList):
    item_class = Deployment


class DaemonsetList(ResourceList):
    item_class = Daemonset


class StatefulsetList(ResourceList):
    item_class = Statefulset


class CronjobList(ResourceList):
    item_class = CronJob


class JobList(ResourceList):
    item_class = Job


class Ingress(NamespacedResource):
    _api = client.AppsV1Api

    host: Optional[str] = None
    hosts: Optional[List[str]] = None
    port: int = 80
    rules: List[dict] = []
    certificate: Optional[dict] = {}
    class_name: Optional[str] = "istio"
    https_redirect: bool = True
    websockets: bool = False

    def generate_istio(self):
        ssl = self.certificate.get("manage", False)
        yield {
            "api_version": "networking.istio.io/v1alpha3",
            "kind": "Gateway",
            "metadata": {"name": Prefixed(f"{self.metadata.name}-gateway")},
            "spec": {
                "selector": {"istio": "ingressgateway"},
                "servers": [
                    (
                        {
                            "port": {
                                "number": 443,
                                "name": "https",
                                "protocol": "HTTPS",
                            },
                            "hosts": [self.host],
                            "tls": {
                                "mode": "SIMPLE",
                                "credential_name": Prefixed(
                                    f"{self.metadata.name}-cert"
                                ),
                            },
                        }
                        if ssl
                        else {
                            "port": {"number": 80, "name": "http", "protocol": "HTTP"},
                            "hosts": [self.host],
                        }
                    )
                ],
            },
        }
        yield {
            "api_version": "networking.istio.io/v1alpha3",
            "kind": "VirtualService",
            "metadata": {"name": Prefixed(f"{self.metadata.name}")},
            "spec": {
                "hosts": [self.host],
                "gateways": [Prefixed(f"{self.metadata.name}-gateway")],
                "http": [
                    {
                        "match": [{"uri": {"prefix": rule["path"]}}],
                        "route": [
                            {
                                "destination": {
                                    "port": {"number": rule.get("port") or self.port},
                                    "host": Prefixed(rule["service"]),
                                }
                            }
                        ],
                        "headers": (
                            {
                                "request": {
                                    "set": {
                                        "x-forwarded-host": self.host,
                                        "x-forwarded-proto": "https",
                                        "x-forwarded-port": "443",
                                    }
                                }
                            }
                            if ssl
                            else {}
                        ),
                    }
                    for rule in self.rules
                ],
            },
        }

    def generate(self, namespace: str) -> Generator:
        if self.certificate.get("manage", False):
            yield {
                "kind": "Certificate",
                "api_version": "cert-manager.io/v1",
                "metadata": {
                    "namespace": namespace,
                    "name": Prefixed(self.metadata.name),
                },
                "spec": {
                    "common_name": self.host,
                    "dns_names": [self.host],
                    "issuer_ref": {"kind": "ClusterIssuer", "name": "letsencrypt"},
                    "secret_name": Prefixed(f"{self.metadata.name}-cert"),
                },
            }

        if self.class_name == "istio":
            for el in self.generate_istio():
                yield el

        elif self.class_name == "nginx":
            for el in self.generate_nginx(namespace=namespace):
                yield el

    def generate_nginx(self, namespace):
        assert self.host or self.hosts

        if self.hosts:
            for host in self.hosts:
                for el in self.generate_nginx_host(namespace, host):
                    yield el
        else:
            for el in self.generate_nginx_host(namespace, self.host):
                yield el

    def generate_nginx_host(self, namespace, host):
        paths = []
        for rule in self.rules:
            paths.append(
                client.V1HTTPIngressPath(
                    path=rule["path"],
                    path_type=rule.get("type") or "Prefix",
                    backend=client.V1IngressBackend(
                        service=client.V1IngressServiceBackend(
                            port=client.V1ServiceBackendPort(
                                number=rule.get("port") or self.port,
                            ),
                            name=(
                                rule["service"]
                                if rule.get("external")
                                else Prefixed(rule["service"])
                            ),
                        )
                    ),
                )
            )

            # This points to a service on a different namespace
            rns = rule.get("namespace")
            if rns:
                rmd = self.metadata
                rmd.name = Prefixed(rule["service"])
                rmd.namespace = namespace
                yield V1Service(
                    api_version="v1",
                    kind="Service",
                    metadata=rmd,
                    spec=V1ServiceSpec(
                        type="ExternalName",
                        external_name=LazyString(
                            f"{rule['service']}.{rns}.svc.cluster.local"
                        ),
                        ports=[
                            V1ServicePort(
                                name=f"port-{rule['port']}",
                                port=rule["port"],
                                target_port=rule["port"],
                            )
                        ],
                    ),
                ).to_dict()

        ingress_rule = client.V1IngressRule(
            host=host,
            http=client.V1HTTPIngressRuleValue(paths=paths),
        )

        # tls = None
        # if self.certificate.get("manage", False):
        tls = []
        if self.https_redirect:
            tls = [
                client.V1IngressTLS(
                    hosts=[host],
                    secret_name=Prefixed(f"{host.replace('*', 'x')}-cert"),
                )
            ]

        metadata = self.metadata
        metadata.name = Prefixed(
            f"{self.name}-{host.replace('*', 'x').replace('.', '')}"
        )
        metadata.namespace = namespace
        metadata.annotations["cert-manager.io/issuer"] = "letsencrypt-cloudflare-issuer"
        if self.websockets:
            # metadata.annotations["nginx.ingress.kubernetes.io/rewrite-target"] = '/'
            metadata.annotations["nginx.ingress.kubernetes.io/proxy-read-timeout"] = (
                "3600"
            )
            metadata.annotations["nginx.ingress.kubernetes.io/proxy-send-timeout"] = (
                "3600"
            )

        yield client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=metadata,
            spec=client.V1IngressSpec(rules=[ingress_rule], tls=tls),
        ).to_dict()

    @property
    def _metadata_defaults(self):
        defaults = super()._metadata_defaults

        defaults = dict(
            merge(
                defaults,
                {
                    "annotations": {
                        "kubernetes.io/ingress.class": self.class_name,
                        "nginx.ingress.kubernetes.io/ssl-redirect": (
                            "true" if self.https_redirect else "false"
                        ),
                    }
                },
            )
        )

        return defaults


class IngressList(ResourceList):
    item_class = Ingress
