import base64
from typing import Dict

from airspot_dev.pulumi_ import StackVar, is_stack_var
from . import BaseK8sResourceConfig

import pulumi
import pulumi_kubernetes as k8s

from airspot_dev import container


class SecretMapConfig(BaseK8sResourceConfig):
    data: Dict[str, str | StackVar]
    
    model_config = {"arbitrary_types_allowed": True}


def get_secret(config: SecretMapConfig, resource_name=None, depends_on=None):
    if not resource_name:
        resource_name = f"{config.name}-secret"
    new_data: dict = config.data.copy()
    output_data = {}

    for k in new_data:
        value = new_data[k]
        if is_stack_var(value):
            # StackVar is now a proper class, we can just pass it directly
            value = container.get_stack_var(value)

        # Check if the value is an Output object
        if isinstance(value, pulumi.Output):
            # For Output values, we use apply to transform the string after it resolves
            output_data[k] = value.apply(lambda s: base64.b64encode(s.encode()).decode())
        else:
            # For regular strings, encode directly
            output_data[k] = base64.b64encode(value.encode()).decode()

    # Handle dependencies
    options = pulumi.ResourceOptions(
        provider=container.k8s.namespaced_provider(),
        transforms=[*config.get_transforms()]
    )
    
    if depends_on:
        if isinstance(depends_on, list):
            options.depends_on = depends_on
        else:
            options.depends_on = [depends_on]

    return k8s.core.v1.Secret(
        resource_name=resource_name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=config.name,
        ),
        data=output_data,
        opts=options
    )
