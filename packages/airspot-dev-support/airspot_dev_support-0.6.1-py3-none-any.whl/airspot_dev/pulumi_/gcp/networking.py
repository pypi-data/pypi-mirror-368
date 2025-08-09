from typing import Optional, Dict, Any, Union
import pulumi
import pulumi_gcp as gcp
from airspot_dev.pulumi_ import BaseResourceConfig


class StaticIPConfig(BaseResourceConfig):
    """Static IP configuration"""
    project_id: str
    existing_ip_name: Optional[str] = None  # Se specificato, usa IP esistente
    region: Optional[str] = None  # Se specificato, usa IP regionale invece di globale
    
    model_config = {"arbitrary_types_allowed": True}


class DNSConfig(BaseResourceConfig):
    """DNS configuration"""
    domain: str
    project_id: str                    # Progetto per DNS
    managed_zone_name: str             # Nome della zona DNS
    ip_address: Optional[Union[str, pulumi.Output]] = None  # IP da associare - opzionale, popolato automaticamente
    
    model_config = {"arbitrary_types_allowed": True}


def get_static_ip(config: StaticIPConfig) -> Union[gcp.compute.GlobalAddress, gcp.compute.Address]:
    """Crea o referenzia IP statico globale o regionale"""
    if config.existing_ip_name:
        # Usa IP esistente - reference per nome
        if config.region:
            # IP regionale esistente
            return gcp.compute.Address.get(
                f"{config.name}-ip-ref",
                config.existing_ip_name,
                project=config.project_id,
                region=config.region
            )
        else:
            # IP globale esistente
            return gcp.compute.GlobalAddress.get(
                f"{config.name}-ip-ref",
                config.existing_ip_name,
                project=config.project_id
            )
    else:
        # Crea nuovo IP statico
        if config.region:
            # Crea IP regionale
            return gcp.compute.Address(
                f"{config.name}-ip",
                name=f"{config.name}-{pulumi.get_stack()}",
                project=config.project_id,
                region=config.region
            )
        else:
            # Crea IP globale
            return gcp.compute.GlobalAddress(
                f"{config.name}-ip",
                name=f"{config.name}-{pulumi.get_stack()}",
                project=config.project_id,
            )


def get_dns_record(config: DNSConfig, ip_address: Union[str, pulumi.Output] = None) -> gcp.dns.RecordSet:
    """Crea record DNS"""
    # Use provided ip_address or fall back to config.ip_address
    dns_ip = ip_address if ip_address is not None else config.ip_address
    
    if dns_ip is None:
        raise ValueError("ip_address must be provided either in config or as parameter")
    
    # Handle both string and Output for ip_address
    rrdatas = [dns_ip] if isinstance(dns_ip, str) else [dns_ip]
    
    return gcp.dns.RecordSet(
        f"{config.name}-dns",
        project=config.project_id,
        managed_zone=config.managed_zone_name,
        name=f"{config.domain}.",
        type="A",
        ttl=300,
        rrdatas=rrdatas,
    )
