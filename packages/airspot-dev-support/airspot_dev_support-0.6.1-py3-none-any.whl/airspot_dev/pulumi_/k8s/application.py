from typing import Optional, Dict, List, Any, Union

from pydantic import BaseModel, Field

from airspot_dev.pulumi_ import StackVar, is_stack_var
from . import BaseK8sResourceConfig
from .pvc import PvcConfig, get_pvc
from .backend_config import BackendConfigConfig, get_backend_config
from airspot_dev.pulumi_.docker import ImageBuildConfig, get_image

import pulumi
import pulumi_kubernetes as k8s

from airspot_dev import container


class VolumeConfig(BaseModel):
    """Simplified configuration for volumes and mounts"""
    name: str
    storage_size: str = "10Gi"
    mount_path: str
    access_modes: List[str] = Field(default_factory=lambda: ["ReadWriteOnce"])
    storage_class_name: Optional[str] = None
    sub_path: Optional[str] = None
    read_only: bool = False
    
    model_config = {"arbitrary_types_allowed": True}


class ApplicationConfig(BaseK8sResourceConfig):
    """Unified configuration for a typical Kubernetes application"""
    # Image configuration
    image: Union[str, ImageBuildConfig]  # Either an image name/tag or build config
    
    # Basic deployment config
    replicas: int = 1
    
    # Resource requirements
    cpu_request: str = "200m"
    memory_request: str = "256Mi"
    cpu_limit: Optional[str] = "400m"
    memory_limit: Optional[str] = "1Gi"
    
    # Networking - simplified
    container_port: Optional[int] = None
    service_port: Optional[int] = None  # If set, a service will be created
    service_type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer
    protocol: str = "TCP"
    port_name: Optional[str] = None
    external_traffic_policy: Optional[str] = None  # Cluster or Local (for LoadBalancer/NodePort)
    
    # Storage
    volumes: List[VolumeConfig] = Field(default_factory=list)
    
    # Environment variables
    env_vars: Dict[str, Union[str, StackVar]] = Field(default_factory=dict)
    env_from_secrets: List[str] = Field(default_factory=list)
    
    # Additional configuration
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    
    # Health check configuration (optional)
    backend_config: Optional[BackendConfigConfig] = None
    
    model_config = {"arbitrary_types_allowed": True}


def get_application(config: ApplicationConfig, resource_name=None, depends_on=None):
    """
    Creates a complete Kubernetes application including Deployment, Service, and PVCs as needed.
    
    Args:
        config: The unified application configuration
        resource_name: Optional resource name prefix
        depends_on: Optional list of resources that this application depends on
        
    Returns:
        A dictionary containing all created resources
    """
    if not resource_name:
        resource_name = config.name
    
    # Initialize list of dependencies
    dependencies = []
    if depends_on:
        if isinstance(depends_on, list):
            dependencies.extend(depends_on)
        else:
            dependencies.append(depends_on)
    
    # Dictionary to store all created resources
    resources = {}
    
    # Process image, which could be a string or ImageBuildConfig
    if isinstance(config.image, ImageBuildConfig):
        image_resource = get_image(config.image)
        image_reference = image_resource.repo_digest
        resources["image"] = image_resource
    else:
        image_reference = config.image
    
    # Create PVCs for volumes
    pvcs = []
    volume_mounts = []
    k8s_volumes = []
    
    for vol in config.volumes:
        pvc = get_pvc(PvcConfig(
            name=f"{config.name}-{vol.name}",
            storage_size=vol.storage_size,
            access_modes=vol.access_modes,
            storage_class_name=vol.storage_class_name,
            labels=config.labels,
            annotations=config.annotations
        ))
        
        pvcs.append(pvc)
        resources[f"pvc_{vol.name}"] = pvc
        
        # Create volume mount configuration
        mount_args = {
            "name": vol.name,
            "mount_path": vol.mount_path,
            "read_only": vol.read_only
        }
        
        if vol.sub_path:
            mount_args["sub_path"] = vol.sub_path
            
        volume_mounts.append(k8s.core.v1.VolumeMountArgs(**mount_args))
        
        # Create volume configuration
        k8s_volumes.append(k8s.core.v1.VolumeArgs(
            name=vol.name,
            persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                claim_name=pvc.metadata.name
            )
        ))
    
    # Process container port and service
    container_ports = []
    
    # Only create container port if specified
    if config.container_port is not None:
        port_name = config.port_name or f"port-{config.container_port}"
        
        container_ports.append(k8s.core.v1.ContainerPortArgs(
            name=port_name,
            container_port=config.container_port,
            protocol=config.protocol
        ))
    
    # Process environment variables
    env_vars = []
    
    for name, value in config.env_vars.items():
        if is_stack_var(value):
            value = container.get_stack_var(value)
        
        env_vars.append(k8s.core.v1.EnvVarArgs(
            name=name,
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
    
    # Create container specification
    container_args = {
        "name": config.name,
        "image": image_reference,
        "resources": k8s.core.v1.ResourceRequirementsArgs(
            requests={
                "memory": config.memory_request,
                "cpu": config.cpu_request
            },
            limits={
                "memory": config.memory_limit,
                "cpu": config.cpu_limit
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
    
    # Create deployment
    deployment = k8s.apps.v1.Deployment(
        f"{resource_name}-deployment",
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
                    volumes=k8s_volumes if k8s_volumes else None
                )
            )
        ),
        opts=pulumi.ResourceOptions(
            provider=container.k8s.namespaced_provider(),
            transforms=[*config.get_transforms()],
            depends_on=pvcs + dependencies
        )
    )
    
    resources["deployment"] = deployment
    
    # Create BackendConfig if specified
    backend_config_resource = None
    if config.backend_config:
        backend_config_resource = get_backend_config(
            config.backend_config, 
            service_port=config.service_port
        )
        resources["backend_config"] = backend_config_resource
    
    # Create service if service_port is specified
    if config.service_port is not None:
        port_name = config.port_name or f"port-{config.container_port or config.service_port}"
        target_port = port_name if config.container_port is not None else config.service_port
        
        service_port = k8s.core.v1.ServicePortArgs(
            name=port_name,
            port=config.service_port,
            target_port=target_port,
            protocol=config.protocol
        )
        
        service_spec = {
            "ports": [service_port],
            "selector": {"app": config.name},
            "type": config.service_type
        }
        
        if config.external_traffic_policy:
            service_spec["external_traffic_policy"] = config.external_traffic_policy
        
        # Prepare service annotations
        service_annotations = dict(config.annotations)
        if backend_config_resource:
            # Use the correct GCP format: {"ports": {"PORT_NUMBER": "BACKEND_CONFIG_NAME"}}
            service_annotations["cloud.google.com/backend-config"] = f'{{\"ports\": {{\"{config.service_port}\": \"{config.backend_config.name}-backend-config\"}}}}'
        
        # Dependencies for service
        service_depends_on = [deployment] + dependencies
        if backend_config_resource:
            service_depends_on.append(backend_config_resource)
        
        service = k8s.core.v1.Service(
            f"{resource_name}-service",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=config.name,
                labels=config.labels,
                annotations=service_annotations
            ),
            spec=service_spec,
            opts=pulumi.ResourceOptions(
                provider=container.k8s.namespaced_provider(),
                transforms=[*config.get_transforms()],
                depends_on=service_depends_on
            )
        )
        
        resources["service"] = service
    
    return resources
