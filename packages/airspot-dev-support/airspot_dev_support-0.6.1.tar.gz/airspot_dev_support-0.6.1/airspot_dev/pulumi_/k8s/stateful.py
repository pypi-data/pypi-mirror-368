from typing import Optional, Dict, List, Any, Union

from pydantic import BaseModel, Field

from airspot_dev.pulumi_ import StackVar, is_stack_var
from . import BaseK8sResourceConfig
from .pvc import PvcConfig, get_pvc
from airspot_dev.pulumi_.docker import ImageBuildConfig, get_image

import pulumi
import pulumi_kubernetes as k8s

from airspot_dev import container


class VolumeClaimTemplateConfig(BaseModel):
    """Configuration for StatefulSet PVC templates"""
    name: str
    storage_size: str = "10Gi"
    mount_path: str
    access_modes: List[str] = Field(default_factory=lambda: ["ReadWriteOnce"])
    storage_class_name: Optional[str] = None
    sub_path: Optional[str] = None
    read_only: bool = False
    
    model_config = {"arbitrary_types_allowed": True}


class StatefulAppConfig(BaseK8sResourceConfig):
    """Unified configuration for a stateful Kubernetes application"""
    # Image configuration
    image: Union[str, ImageBuildConfig]  # Either an image name/tag or build config
    
    # Basic StatefulSet config
    replicas: int = 1
    pod_management_policy: str = "OrderedReady"  # OrderedReady or Parallel
    service_name: Optional[str] = None  # Headless service name (if None, generated based on app name)
    update_strategy: str = "RollingUpdate"  # RollingUpdate or OnDelete
    
    # Resource requirements
    cpu_request: str = "200m"
    memory_request: str = "256Mi"
    cpu_limit: Optional[str] = "400m"
    memory_limit: Optional[str] = "1Gi"
    
    # Networking - simplified
    container_port: Optional[int] = None
    service_port: Optional[int] = None  # If set, a service will be created
    service_type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer, Headless
    protocol: str = "TCP"
    port_name: Optional[str] = None
    external_traffic_policy: Optional[str] = None  # Cluster or Local (for LoadBalancer/NodePort)
    
    # Storage
    volumes: List[VolumeClaimTemplateConfig] = Field(default_factory=list)
    
    # Environment variables
    env_vars: Dict[str, Union[str, StackVar]] = Field(default_factory=dict)
    env_from_secrets: List[str] = Field(default_factory=list)
    
    # Additional configuration
    command: Optional[List[str]] = None
    args: Optional[List[str]] = None
    
    # Persistence
    persistent_volume_claim_retention_policy: Optional[str] = None  # Delete or Retain
    
    model_config = {"arbitrary_types_allowed": True}


def get_stateful_application(config: StatefulAppConfig, resource_name=None, depends_on=None):
    """
    Creates a complete Kubernetes StatefulSet application with Service and volume claim templates.
    
    Args:
        config: The stateful application configuration
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
    
    # Headless service name (required for StatefulSet)
    headless_service_name = config.service_name or f"{config.name}-headless"
    
    # Create volume claim templates
    volume_claim_templates = []
    volume_mounts = []
    
    for vol in config.volumes:
        # Create volume template
        volume_claim_templates.append(k8s.core.v1.PersistentVolumeClaimArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=vol.name,
                labels=config.labels,
                annotations=config.annotations
            ),
            spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
                access_modes=vol.access_modes,
                resources=k8s.core.v1.ResourceRequirementsArgs(
                    requests={
                        "storage": vol.storage_size
                    }
                ),
                storage_class_name=vol.storage_class_name
            )
        ))
        
        # Create volume mount configuration
        mount_args = {
            "name": vol.name,
            "mount_path": vol.mount_path,
            "read_only": vol.read_only
        }
        
        if vol.sub_path:
            mount_args["sub_path"] = vol.sub_path
            
        volume_mounts.append(k8s.core.v1.VolumeMountArgs(**mount_args))
    
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
    
    # Create StatefulSet spec
    stateful_set_spec_args = {
        "replicas": config.replicas,
        "selector": k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": config.name}
        ),
        "service_name": headless_service_name,
        "pod_management_policy": config.pod_management_policy,
        "template": k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": config.name, **config.labels},
                annotations=config.annotations
            ),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(**container_args)]
            )
        ),
        "update_strategy": k8s.apps.v1.StatefulSetUpdateStrategyArgs(
            type=config.update_strategy
        )
    }
    
    # Add volume claim templates if defined
    if volume_claim_templates:
        stateful_set_spec_args["volume_claim_templates"] = volume_claim_templates
    
    # Add persistent volume claim retention policy if defined
    if config.persistent_volume_claim_retention_policy:
        # This is only available in newer Kubernetes versions
        policy = config.persistent_volume_claim_retention_policy
        stateful_set_spec_args["persistent_volume_claim_retention_policy"] = {
            "when_deleted": policy,
            "when_scaled": policy
        }
    
    # Handle dependencies
    options = pulumi.ResourceOptions(
        provider=container.k8s.namespaced_provider(),
        transforms=[*config.get_transforms()],
        depends_on=dependencies
    )
    
    # Create StatefulSet
    stateful_set = k8s.apps.v1.StatefulSet(
        f"{resource_name}-statefulset",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=config.name,
            labels=config.labels,
            annotations=config.annotations
        ),
        spec=k8s.apps.v1.StatefulSetSpecArgs(**stateful_set_spec_args),
        opts=options
    )
    
    resources["stateful_set"] = stateful_set
    
    # Always create a headless service for the StatefulSet
    headless_service_port = k8s.core.v1.ServicePortArgs(
        name=config.port_name or "default",
        port=config.container_port or 80,
        target_port=config.container_port or 80,
        protocol=config.protocol
    )
    
    headless_service = k8s.core.v1.Service(
        f"{resource_name}-headless-service",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=headless_service_name,
            labels=config.labels,
            annotations=config.annotations
        ),
        spec=k8s.core.v1.ServiceSpecArgs(
            cluster_ip="None",  # This makes it a headless service
            ports=[headless_service_port],
            selector={"app": config.name}
        ),
        opts=pulumi.ResourceOptions(
            provider=container.k8s.namespaced_provider(),
            transforms=[*config.get_transforms()],
            depends_on=[stateful_set] + dependencies
        )
    )
    
    resources["headless_service"] = headless_service
    
    # Create regular service if service_port is specified
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
        
        service = k8s.core.v1.Service(
            f"{resource_name}-service",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=config.name,
                labels=config.labels,
                annotations=config.annotations
            ),
            spec=service_spec,
            opts=pulumi.ResourceOptions(
                provider=container.k8s.namespaced_provider(),
                transforms=[*config.get_transforms()],
                depends_on=[stateful_set] + dependencies
            )
        )
        
        resources["service"] = service
    
    return resources
