from dependency_injector import containers, providers

from .core import Core
from .kubernetes import Kubernetes

class Container(containers.DeclarativeContainer):

    core = providers.Container(Core)
    k8s = providers.Container(
        Kubernetes,
        core=core,
    )

    exports = providers.Callable(
        lambda c: [(k, v) for k, v in c.exports().items()],
        core,
    )

    get_stack_var = core.get_stack_var

