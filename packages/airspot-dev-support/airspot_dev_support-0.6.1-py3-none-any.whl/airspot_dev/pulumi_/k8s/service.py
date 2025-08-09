from typing import Optional, Dict, List, Any

from pydantic import BaseModel, Field

from airspot_dev.pulumi_ import StackVar, is_stack_var
from . import BaseK8sResourceConfig

import pulumi
import pulumi_kubernetes as k8s

from airspot_dev import container


class ServicePortConfig(BaseModel):
    """Configuration for service ports"""
    name: str
    port: int
    target_port: str  # Can be a name or a port number (as string)
    protocol: str = "TCP"
    node_port: Optional[int] = None
    
    model_config = {"arbitrary_types_allowed": True}


class ServiceConfig(BaseK8sResourceConfig):
    """Configuration for Kubernetes Service resources"""
    ports: List[ServicePortConfig]
    type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer
    selector_app: str  # Usually matches the deployment name
    external_traffic_policy: Optional[str] = None  # Cluster or Local (for LoadBalancer/NodePort)


def get_service(config: ServiceConfig, resource_name=None, depends_on=None):
    """
    Creates a Kubernetes Service resource.
    
    Args:
        config: The Service configuration
        resource_name: Optional resource name (defaults to {name}-service)
        depends_on: Optional resource dependencies
        
    Returns:
        A Pulumi Kubernetes Service resource
    """
    if not resource_name:
        resource_name = f"{config.name}-service"
    
    # Prepare service ports
    service_ports = []
    for port in config.ports:
        port_args = {
            "name": port.name,
            "port": port.port,
            "target_port": port.target_port,
            "protocol": port.protocol
        }
        
        if port.node_port:
            port_args["node_port"] = port.node_port
            
        service_ports.append(k8s.core.v1.ServicePortArgs(**port_args))
    
    # Create service spec
    service_spec = {
        "type": config.type,
        "ports": service_ports,
        "selector": {"app": config.selector_app}
    }
    
    if config.external_traffic_policy:
        service_spec["external_traffic_policy"] = config.external_traffic_policy
    
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
    
    return k8s.core.v1.Service(
        resource_name=resource_name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=config.name,
            labels=config.labels,
            annotations=config.annotations
        ),
        spec=service_spec,
        opts=options
    )
