from typing import Optional, Dict, List, Any, Union
from pydantic import Field
import pulumi
import pulumi_kubernetes as k8s
from airspot_dev.pulumi_ import BaseResourceConfig
from airspot_dev import container


class GCEIngressConfig(BaseResourceConfig):
    """GCE Ingress with Managed Certificate"""
    domain: str
    static_ip_name: Optional[Union[str, pulumi.Output]] = None  # Nome IP statico - opzionale, popolato automaticamente
    service_name: Optional[str] = None                          # Nome service - opzionale, popolato automaticamente
    service_port: int
    
    # Certificate options
    use_managed_cert: bool = True
    cert_domains: Optional[List[str]] = None  # Default: [domain]
    
    # Load balancer type
    use_regional_ip: bool = False  # If True, use regional IP instead of global
    
    # Advanced options
    additional_annotations: Dict[str, str] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}


def get_gce_ingress(config: GCEIngressConfig, static_ip_name: Union[str, pulumi.Output] = None, service_name: str = None, service_port_name: str = None) -> Dict[str, Any]:
    """Crea Managed Certificate + GCE Ingress"""
    
    # Use provided parameters or fall back to config values
    ingress_static_ip_name = static_ip_name if static_ip_name is not None else config.static_ip_name
    ingress_service_name = service_name if service_name is not None else config.service_name
    
    # Validate required parameters
    if ingress_static_ip_name is None:
        raise ValueError("static_ip_name must be provided either in config or as parameter")
    if ingress_service_name is None:
        raise ValueError("service_name must be provided either in config or as parameter")
    
    resources = {}
    
    if config.use_managed_cert:
        cert_domains = config.cert_domains or [config.domain]
        
        managed_cert = k8s.apiextensions.CustomResource(
            f"{config.name}-managed-cert",
            api_version="networking.gke.io/v1",
            kind="ManagedCertificate",
            metadata={"name": f"{config.name}-managed-cert"},
            spec={"domains": cert_domains},
            opts=pulumi.ResourceOptions(provider=container.k8s.namespaced_provider())
        )
        resources["managed_certificate"] = managed_cert
    
    # Ingress annotations
    annotations = {
        "kubernetes.io/ingress.class": "gce",
        **config.additional_annotations
    }
    
    # Add appropriate IP annotation based on type
    if config.use_regional_ip:
        annotations["kubernetes.io/ingress.regional-static-ip-name"] = ingress_static_ip_name
    else:
        annotations["kubernetes.io/ingress.global-static-ip-name"] = ingress_static_ip_name
    
    if config.use_managed_cert:
        annotations["networking.gke.io/managed-certificates"] = f"{config.name}-managed-cert"
    
    # Create Ingress
    ingress = k8s.networking.v1.Ingress(
        f"{config.name}-ingress",
        metadata={
            "name": f"{config.name}-ingress",
            "annotations": annotations
        },
        spec={
            "rules": [{
                "host": config.domain,
                "http": {
                    "paths": [{
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {
                            "service": {
                                "name": ingress_service_name,
                                "port": {"name": service_port_name} if service_port_name else {"number": config.service_port}
                            }
                        }
                    }]
                }
            }]
        },
        opts=pulumi.ResourceOptions(
            provider=container.k8s.namespaced_provider(),
            depends_on=list(resources.values())
        )
    )
    resources["ingress"] = ingress
    
    return resources
