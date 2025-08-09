from airspot_dev.pulumi_ import StackVar, is_stack_var
from . import BaseK8sResourceConfig

import pulumi
import pulumi_kubernetes as k8s

from airspot_dev import container


class NamespaceConfig(BaseK8sResourceConfig):
    pass


def get_namespace(config: NamespaceConfig, resource_name=None, depends_on=None):
    if not resource_name:
        resource_name = f"{config.name}-ns"
    # Handle dependencies
    options = pulumi.ResourceOptions(
        provider=container.k8s.cluster_provider(),
        transforms=[*config.get_transforms()]
    )
    
    if depends_on:
        if isinstance(depends_on, list):
            options.depends_on = depends_on
        else:
            options.depends_on = [depends_on]
            
    return k8s.core.v1.Namespace(
        resource_name=resource_name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=config.name,
        ),
        opts=options
    )
