from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
import pulumi
import pulumi_kubernetes as k8s
from airspot_dev import container
from . import BaseK8sResourceConfig


class HealthCheckConfig(BaseModel):
    """Configuration for BackendConfig health check"""
    request_path: str = "/"
    port: Optional[int] = None  # If None, uses service port
    check_interval_sec: int = 15
    timeout_sec: int = 15
    healthy_threshold: int = 1
    unhealthy_threshold: int = 3
    type: str = "HTTP"  # HTTP or HTTPS
    
    model_config = {"arbitrary_types_allowed": True}


class BackendConfigConfig(BaseK8sResourceConfig):
    """Configuration for GCE BackendConfig"""
    health_check: Optional[HealthCheckConfig] = None
    # Future: Add CDN, IAP, etc. configurations here
    
    model_config = {"arbitrary_types_allowed": True}


def get_backend_config(config: BackendConfigConfig, service_port: Optional[int] = None) -> k8s.apiextensions.CustomResource:
    """
    Creates a GCE BackendConfig custom resource
    
    Args:
        config: The BackendConfig configuration
        service_port: The service port to use for health check if not specified in config
        
    Returns:
        The BackendConfig CustomResource
    """
    
    # Build spec
    spec = {}
    
    if config.health_check:
        hc = config.health_check
        health_check_port = hc.port or service_port
        
        if health_check_port is None:
            raise ValueError("Health check port must be specified either in health_check.port or service_port parameter")
        
        spec["healthCheck"] = {
            "checkIntervalSec": hc.check_interval_sec,
            "timeoutSec": hc.timeout_sec,
            "healthyThreshold": hc.healthy_threshold,
            "unhealthyThreshold": hc.unhealthy_threshold,
            "type": hc.type,
            "requestPath": hc.request_path,
            "port": health_check_port
        }
    
    # Create BackendConfig
    backend_config = k8s.apiextensions.CustomResource(
        f"{config.name}-backend-config",
        api_version="cloud.google.com/v1",
        kind="BackendConfig",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=f"{config.name}-backend-config",
            labels=config.labels,
            annotations=config.annotations
        ),
        spec=spec,
        opts=pulumi.ResourceOptions(
            provider=container.k8s.namespaced_provider(),
            transforms=[*config.get_transforms()]
        )
    )
    
    return backend_config