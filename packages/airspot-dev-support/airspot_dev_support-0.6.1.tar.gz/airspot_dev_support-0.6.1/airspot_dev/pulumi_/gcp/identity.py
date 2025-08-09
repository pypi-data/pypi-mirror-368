from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, model_validator
import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
from airspot_dev.pulumi_ import BaseResourceConfig
from airspot_dev import container


class WorkloadIdentityConfig(BaseResourceConfig):
    """Service Account with Workload Identity binding"""
    
    # Modalità 1: Uso SA esistente
    use_gsa: Optional[str] = None           # Account ID del GSA esistente
    ksa_name: Optional[str] = None          # Nome del KSA esistente (required se use_gsa)
    
    # Modalità 2: Creazione automatica (se use_gsa è None)
    # Nessun parametro aggiuntivo - usa naming convention
    
    # Configurazione comune
    namespace: str                          # Namespace K8s (required)
    project_id: str                        # Progetto GCP (required)
    roles: List[str] = Field(default_factory=list)  # Roles da aggiungere
    
    model_config = {"arbitrary_types_allowed": True}
    
    @model_validator(mode='after')
    def validate_gsa_ksa(self):
        if self.use_gsa and not self.ksa_name:
            raise ValueError("ksa_name is required when use_gsa is specified")
        return self


def get_workload_identity(config: WorkloadIdentityConfig) -> Dict[str, Any]:
    """
    Gestisce Service Account e Workload Identity:
    - Se use_gsa: usa SA esistenti + aggiunge roles
    - Altrimenti: crea GSA + KSA + Workload Identity binding
    """
    
    if config.use_gsa:
        return _use_existing_service_accounts(config)
    else:
        return _create_service_accounts(config)


def _use_existing_service_accounts(config: WorkloadIdentityConfig) -> Dict[str, Any]:
    """Usa Service Account esistenti e aggiunge roles"""
    
    gsa_email = f"{config.use_gsa}@{config.project_id}.iam.gserviceaccount.com"
    
    # Aggiungi roles al GSA esistente se specificati
    role_bindings = []
    for role in config.roles:
        safe_role_name = role.replace('/', '-').replace('.', '-')
        role_binding = gcp.projects.IAMMember(
            f"{config.name}-{safe_role_name}",
            project=config.project_id,
            role=role,
            member=f"serviceAccount:{gsa_email}",
        )
        role_bindings.append(role_binding)
    
    return {
        "gsa_email": gsa_email,
        "ksa_name": config.ksa_name,
        "role_bindings": role_bindings,
        "existing": True
    }


def _create_service_accounts(config: WorkloadIdentityConfig) -> Dict[str, Any]:
    """Crea GSA + KSA + Workload Identity binding"""
    
    # Naming convention per creazione automatica
    base_name = config.name.lower().replace('_', '-')
    gsa_id = f"{base_name}-sa"
    ksa_name = f"{base_name}-ksa"
    
    # Create GCP Service Account
    gcp_sa = gcp.serviceaccount.Account(
        f"{config.name}-gsa",
        account_id=gsa_id,
        display_name=f"Service Account for {config.name}",
        project=config.project_id,
    )
    
    # Create K8s Service Account
    k8s_sa = k8s.core.v1.ServiceAccount(
        f"{config.name}-ksa",
        metadata={
            "name": ksa_name,
            "annotations": {
                "iam.gke.io/gcp-service-account": gcp_sa.email
            }
        },
        opts=pulumi.ResourceOptions(provider=container.k8s.namespaced_provider())
    )
    
    # Workload Identity Binding
    wi_binding = gcp.projects.IAMMember(
        f"{config.name}-workload-identity",
        project=config.project_id,
        role="roles/iam.workloadIdentityUser",
        member=pulumi.Output.format(
            "serviceAccount:{}.svc.id.goog[{}/{}]",
            config.project_id, config.namespace, ksa_name
        ),
        opts=pulumi.ResourceOptions(depends_on=[gcp_sa, k8s_sa])
    )
    
    # Add application roles
    role_bindings = []
    for role in config.roles:
        safe_role_name = role.replace('/', '-').replace('.', '-')
        role_binding = gcp.projects.IAMMember(
            f"{config.name}-{safe_role_name}",
            project=config.project_id,
            role=role,
            member=pulumi.Output.format("serviceAccount:{}", gcp_sa.email),
            opts=pulumi.ResourceOptions(depends_on=[gcp_sa])
        )
        role_bindings.append(role_binding)
    
    return {
        "gcp_service_account": gcp_sa,
        "k8s_service_account": k8s_sa,
        "gsa_email": gcp_sa.email,
        "ksa_name": ksa_name,
        "workload_identity_binding": wi_binding,
        "role_bindings": role_bindings,
        "existing": False
    }


def create_sa_patch_transform(ksa_name: str):
    """Transform per applicare automaticamente il service account al deployment"""
    def _patch(args: pulumi.ResourceTransformArgs) -> pulumi.ResourceTransformResult | None:
        if args.type_ in ("kubernetes:apps/v1:Deployment", "kubernetes:apps/v1:StatefulSet"):
            def _apply_patch(spec):
                spec["template"]["spec"]["serviceAccountName"] = ksa_name
            
            args.props.get("spec").apply(lambda x: _apply_patch(x))
            return pulumi.ResourceTransformResult(props=args.props, opts=args.opts)
        return None
    
    return _patch
