from typing import List, Callable
from pydantic import BaseModel
import pulumi


class StackVar(str):
    """A variable that references a stack output or configuration value.
    
    This is implemented as a proper class (subclass of str) to ensure it can be
    properly identified at runtime, while still being usable as a string.
    """
    def __new__(cls, value):
        return super(StackVar, cls).__new__(cls, value)
    
    def __repr__(self):
        return f"StackVar({super().__repr__()})"


def is_stack_var(x) -> bool:
    """Check if a value is a StackVar instance."""
    return isinstance(x, StackVar)


class BaseResourceConfig(BaseModel):
    name: str
    transforms: List[Callable[[pulumi.ResourceTransformArgs], pulumi.ResourceTransformResult]] = []

    def get_transforms(self) -> List[Callable[[pulumi.ResourceTransformArgs], pulumi.ResourceTransformResult]]:
        """
        Override this method to provide custom transformations in inherited classes
        :return:
        """
        return self.transforms
        
    model_config = {"arbitrary_types_allowed": True}


# Import debug utilities if they exist
try:
    from .debug import debug_stack_var, debug_container_get_stack_var, debug_direct_vs_stackvar, debug_stackvar_creation
    has_debug = True
except ImportError:
    has_debug = False


# Define exports based on what's available
__all__ = [
    'StackVar', 'is_stack_var',
    'BaseResourceConfig',
]

if has_debug:
    __all__.extend(['debug_stack_var', 'debug_container_get_stack_var', 'debug_direct_vs_stackvar', 'debug_stackvar_creation'])
