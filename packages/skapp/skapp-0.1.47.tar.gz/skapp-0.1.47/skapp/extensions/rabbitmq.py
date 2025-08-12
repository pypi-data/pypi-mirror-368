from os import stat
import string
from textwrap import dedent

from skapp.utils import LazyString, merge

DEFAULT_CONFIG = """
## DEFAULT SETTINGS ARE NOT MEANT TO BE TAKEN STRAIGHT INTO PRODUCTION
## see https://www.rabbitmq.com/configure.html for further information
## on configuring RabbitMQ

## allow access to the guest user from anywhere on the network
## https://www.rabbitmq.com/access-control.html#loopback-users
## https://www.rabbitmq.com/production-checklist.html#users
loopback_users.guest = false

## Send all logs to stdout/TTY. Necessary to see logs when running via
## a container
log.console = true
"""


def get_cluster_config(name: str, replicas: int) -> str:
    config = [dedent(
        """
        cluster_formation.peer_discovery_backend = classic_config

        # the backend can also be specified using its module name
        # cluster_formation.peer_discovery_backend = rabbit_peer_discovery_classic_config
        """
    )]

    for i in range(replicas):
        config.append(f"cluster_formation.classic_config.nodes.{i} = "
                      f"rabbit@{name}-{i}.{name}.{{{{ namespace }}}}.svc.cluster.local")

    return '\n'.join(config)


def handler(elements: dict) -> dict:
    patch = {
        'statefulsets': {},
        'configs': {}
    }

    for elname, config in elements.items():
        replicas = config.pop('replicas', 1)
        version = config.pop('version', 'latest')
        ui = config.pop('ui', False)
        assert isinstance(ui, bool)

        if ui and version == 'latest':
            version = 'management'
        elif ui:
            version = f'{version}-management'

        name = f'rabbitmq-{elname}'

        cluster_config = LazyString(
            get_cluster_config(
                "{{ prefix('%s') }}" % name,
                replicas
            )
        )

        patch['configs'][name] = {
            '10-defaults.conf': DEFAULT_CONFIG,
            '20-cluster-formation.conf': cluster_config
        }

        statefulset = {
            'image': f'rabbitmq:{version}',
            'entrypoint': [
                '/bin/bash',
                '-c'
            ],
            'command': [
                'RABBITMQ_NODENAME=rabbit@$(hostname -f) rabbitmq-server'
            ],
            'environment': {
                'RABBITMQ_USE_LONGNAME': 'true',
                'RABBITMQ_DIST_PORT': '25672',
                'RABBITMQ_DEFAULT_USER': 'admin',
                'RABBITMQ_ERLANG_COOKIE': {
                    'autosecret': {'length': 64}
                },
                'RABBITMQ_DEFAULT_PASS': {
                    'autosecret': {
                        'length': 16,
                        'alphabet': string.ascii_letters + string.digits
                    }
                }
            },
            'replicas': replicas,
            'expose': {
                'ports': [5672, 4369, 35197, 2379, 15692, 25672, 15672] if ui else [2379, 5672, 15692, 25672]
            },
            'mounts': {
                'config': {
                    name: '/etc/rabbitmq/conf.d/'
                }
            }
        }

        statefulset = dict(merge(statefulset, config))
        patch['statefulsets'][name] = statefulset

    return patch

