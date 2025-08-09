from typing import Optional, Dict, List, Any, Union

from pydantic import BaseModel, Field

from airspot_dev.pulumi_ import StackVar, is_stack_var
from . import BaseK8sResourceConfig
from .secrets import SecretMapConfig
from airspot_dev.pulumi_.docker import ImageBuildConfig, get_image

import pulumi
import pulumi_kubernetes as k8s

from airspot_dev import container


class ResourceRequirementsConfig(BaseModel):
    """Configuration for container resource requirements"""
    memory_request: str = "256Mi"
    cpu_request: str = "200m"
    memory_limit: Optional[str] = "1Gi"
    cpu_limit: Optional[str] = "400m"
    
    model_config = {"arbitrary_types_allowed": True}


class ContainerPortConfig(BaseModel):
    """Configuration for container ports"""
    name: str
    container_port: int
    protocol: str = "TCP"
    
    model_config = {"arbitrary_types_allowed": True}


class VolumeMountConfig(BaseModel):
    """Configuration for volume mounts"""
    name: str
    mount_path: str
    sub_path: Optional[str] = None
    read_only: bool = False
    
    model_config = {"arbitrary_types_allowed": True}


class EnvVarConfig(BaseModel):
    """Configuration for environment variables"""
    name: str
    value: Union[str, StackVar]
    
    model_config = {"arbitrary_types_allowed": True}


class VolumeConfig(BaseModel):
    """Base configuration for volumes"""
    name: str
    volume_type: str = "persistentVolumeClaim"  # Could be configMap, secret, etc.
    
    model_config = {"arbitrary_types_allowed": True}


class PvcVolumeConfig(VolumeConfig):
    """Configuration for PVC-based volumes"""
    claim_name: str
    read_only: bool = False
    
    model_config = {"arbitrary_types_allowed": True}


class DeploymentConfig(BaseK8sResourceConfig):
    """Configuration for Kubernetes Deployment resources"""
    image: str
    replicas: int = 1
    ports: List[ContainerPortConfig] = Field(default_factory=list)
    resources: ResourceRequirementsConfig = Field(default_factory=ResourceRequirementsConfig)
    volumes: List[VolumeConfig] = Field(default_factory=list)
    volume_mounts: List[VolumeMountConfig] = Field(default_factory=list)
    env_vars: List[EnvVarConfig] = Field(default_factory=list)
    env_from_secrets: List[str] = Field(default_factory=list)
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    
    model_config = {"arbitrary_types_allowed": True}


def get_deployment(config: DeploymentConfig, resource_name=None, depends_on=None):
    """
    Creates a Kubernetes Deployment resource.
    
    Args:
        config: The Deployment configuration
        resource_name: Optional resource name (defaults to {name}-deployment)
        depends_on: Optional resource dependencies
        
    Returns:
        A Pulumi Kubernetes Deployment resource
    """
    if not resource_name:
        resource_name = f"{config.name}-deployment"
    
    # Prepare container environment variables
    env_vars = []
    
    # Add individual environment variables
    for env_var in config.env_vars:
        value = env_var.value
        if is_stack_var(value):
            value = container.get_stack_var(value)
        
        env_vars.append(k8s.core.v1.EnvVarArgs(
            name=env_var.name,
            value=value
        ))
    
    # Add environment variables from secrets
    env_from = []
    for secret_name in config.env_from_secrets:
        env_from.append(k8s.core.v1.EnvFromSourceArgs(
            secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                name=secret_name
            )
        ))
    
    # Prepare container ports
    container_ports = []
    for port in config.ports:
        container_ports.append(k8s.core.v1.ContainerPortArgs(
            name=port.name,
            container_port=port.container_port,
            protocol=port.protocol
        ))
    
    # Prepare volume mounts
    volume_mounts = []
    for vm in config.volume_mounts:
        mount_args = {
            "name": vm.name,
            "mount_path": vm.mount_path,
            "read_only": vm.read_only
        }
        
        if vm.sub_path:
            mount_args["sub_path"] = vm.sub_path
            
        volume_mounts.append(k8s.core.v1.VolumeMountArgs(**mount_args))
    
    # Prepare volumes
    volumes = []
    for vol in config.volumes:
        if isinstance(vol, PvcVolumeConfig):
            volumes.append(k8s.core.v1.VolumeArgs(
                name=vol.name,
                persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                    claim_name=vol.claim_name,
                    read_only=vol.read_only
                )
            ))
        # Other volume types can be added here
    
    # Create container args
    container_args = {
        "name": config.name,
        "image": config.image,
        "resources": k8s.core.v1.ResourceRequirementsArgs(
            requests={
                "memory": config.resources.memory_request,
                "cpu": config.resources.cpu_request
            },
            limits={
                "memory": config.resources.memory_limit,
                "cpu": config.resources.cpu_limit
            }
        )
    }
    
    if container_ports:
        container_args["ports"] = container_ports
    
    if env_vars:
        container_args["env"] = env_vars
    
    if env_from:
        container_args["env_from"] = env_from
    
    if volume_mounts:
        container_args["volume_mounts"] = volume_mounts
    
    if config.command:
        container_args["command"] = config.command
    
    if config.args:
        container_args["args"] = config.args
    
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
            
    # Create deployment
    return k8s.apps.v1.Deployment(
        resource_name=resource_name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=config.name,
            labels=config.labels,
            annotations=config.annotations
        ),
        spec=k8s.apps.v1.DeploymentSpecArgs(
            replicas=config.replicas,
            selector=k8s.meta.v1.LabelSelectorArgs(
                match_labels={"app": config.name}
            ),
            template=k8s.core.v1.PodTemplateSpecArgs(
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    labels={"app": config.name, **config.labels},
                    annotations=config.annotations
                ),
                spec=k8s.core.v1.PodSpecArgs(
                    containers=[k8s.core.v1.ContainerArgs(**container_args)],
                    volumes=volumes if volumes else None
                )
            )
        ),
        opts=options
    )
