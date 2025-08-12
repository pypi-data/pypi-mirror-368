# Handler for CNPG Cluster
# apiVersion: postgresql.cnpg.io/v1
# kind: Cluster
# metadata:
#   name: main-db
#   namespace: default
# spec:
#   instances: 1

#   storage:
#     pvcTemplate:
#       accessModes:
#         - ReadWriteOnce
#       resources:
#         requests:
#           storage: 1Gi
#       storageClassName: local-storage


#   monitoring:
#     enablePodMonitor: true

from typing import Generator
from skapp.models.resource import NamespacedResource
from skapp.utils import merge


API_VERSION = 'postgresql.cnpg.io/v1'

# Sample input:
'''
thirdparty:cnpg:cluster:
    main-db:
        instances: 1
        storage:
            class: local-storage
            size: 1Gi
            access_mode: ReadWriteOnce
'''


class Cluster(NamespacedResource):
    api_version = API_VERSION
    _kind = 'Cluster'

    def generate(self, namespace: str = None) -> Generator:
        yield {}

class Clusters(ResourceList):
    pass

def handler(elements: dict[str, dict]) -> dict:
    patch = {}
    for elname, config in elements.items():
        cluster = Cluster(name=elname, **config)
        generated = list(cluster.generate())

        patch = dict(merge(patch, {"custom": generated}))
