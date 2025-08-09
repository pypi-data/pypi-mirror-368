from typing import Optional, Dict, Any

from airspot_dev.pulumi_ import StackVar, is_stack_var
from . import BaseK8sResourceConfig

import pulumi
import pulumi_kubernetes as k8s

from airspot_dev import container


class PvcConfig(BaseK8sResourceConfig):
    """Configuration for Kubernetes PersistentVolumeClaim resources"""
    storage_size: str = "10Gi"
    access_modes: list[str] = ["ReadWriteOnce"]
    storage_class_name: Optional[str] = None


def get_pvc(config: PvcConfig, resource_name=None, depends_on=None):
    """
    Creates a Kubernetes PersistentVolumeClaim resource.
    
    Args:
        config: The PVC configuration
        resource_name: Optional resource name (defaults to {name}-pvc)
        depends_on: Optional resource dependencies
        
    Returns:
        A Pulumi Kubernetes PersistentVolumeClaim resource
    """
    if not resource_name:
        resource_name = f"{config.name}-pvc"
    
    pvc_spec = {
        "accessModes": config.access_modes,
        "resources": {
            "requests": {
                "storage": config.storage_size
            }
        }
    }
    
    if config.storage_class_name:
        pvc_spec["storageClassName"] = config.storage_class_name
    
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
    
    return k8s.core.v1.PersistentVolumeClaim(
        resource_name=resource_name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=config.name,
            labels=config.labels,
            annotations=config.annotations
        ),
        spec=pvc_spec,
        opts=options
    )
