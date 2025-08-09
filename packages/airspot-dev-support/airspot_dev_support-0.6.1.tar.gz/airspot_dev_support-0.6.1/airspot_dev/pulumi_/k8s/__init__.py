from typing import Dict, List, Callable

import pulumi

from airspot_dev.pulumi_ import BaseResourceConfig


class BaseK8sResourceConfig(BaseResourceConfig):
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}

    def get_transforms(self) -> List[Callable[[pulumi.ResourceTransformArgs], pulumi.ResourceTransformResult]]:
        transforms = super().get_transforms()

        return transforms


class BaseResourceTransform:
    def __init__(self, config: BaseK8sResourceConfig):
        self._config = config

    def __call__(self, args: pulumi.ResourceTransformArgs) -> pulumi.ResourceTransformResult:
        pulumi.log.info(f"== Got Transform for {args.type_}:{args.name}")
        metadata = args.props.get("metadata", {})
        labels = metadata.get("labels", {})
        labels.update(self._config.labels)
        annotations = metadata.get("annotations", {})
        annotations.update(self._config.annotations)

        return pulumi.ResourceTransformResult(
            props=args.props,
            opts=args.opts,
        )


from .secrets import get_secret, SecretMapConfig
from .namespace import get_namespace, NamespaceConfig
from .pvc import get_pvc, PvcConfig
from .deployment import get_deployment, DeploymentConfig, PvcVolumeConfig, ContainerPortConfig, VolumeMountConfig, EnvVarConfig, ResourceRequirementsConfig
from .service import get_service, ServiceConfig, ServicePortConfig
from .application import get_application, ApplicationConfig, VolumeConfig
from .stateful import get_stateful_application, StatefulAppConfig, VolumeClaimTemplateConfig
from .backend_config import get_backend_config, BackendConfigConfig, HealthCheckConfig

__all__ = [
    'BaseK8sResourceConfig',
    'get_secret', 'SecretMapConfig',
    'get_namespace', 'NamespaceConfig',
    'get_pvc', 'PvcConfig',
    'get_deployment', 'DeploymentConfig', 'PvcVolumeConfig', 'ContainerPortConfig', 'VolumeMountConfig', 'EnvVarConfig', 'ResourceRequirementsConfig',
    'get_service', 'ServiceConfig', 'ServicePortConfig',
    'get_application', 'ApplicationConfig', 'VolumeConfig',
    'get_stateful_application', 'StatefulAppConfig', 'VolumeClaimTemplateConfig',
    'get_backend_config', 'BackendConfigConfig', 'HealthCheckConfig',
]
