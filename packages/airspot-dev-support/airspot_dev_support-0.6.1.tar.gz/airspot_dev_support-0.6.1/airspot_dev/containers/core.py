import pulumi
import pulumi.runtime
from pulumi import StackReference, Config, log, Output
from typing import Optional, List, Dict, Any

from dependency_injector import containers, providers

DEFAULT_ORG = "organization"


# --- Helper Function (Keep) ---
# resolve_stack_name remains unchanged as it's useful for resolving the base stack name
def resolve_stack_name(stack_input: str, default_org: str) -> Optional[str]:
    """
    Resolves a potentially partial stack name string into a fully qualified name.
    (Implementation is the same as previous versions)
    """
    if not stack_input:
        log.warn("Received empty stack_input for resolution.")
        return None
    parts = stack_input.strip('/').split('/')
    current_stack = pulumi.get_stack()
    num_parts = len(parts)
    try:
        if num_parts == 1 and parts[0]:
            project_name = parts[0]
            stack_name = current_stack
            org_name = default_org
            log.debug(
                f"Resolved stack input '{stack_input}' as Project: '{org_name}/{project_name}/{stack_name}' (current stack)")
        elif num_parts == 2 and all(parts):
            project_name = parts[0]
            stack_name = parts[1]
            org_name = default_org
            log.debug(
                f"Resolved stack input '{stack_input}' as Project/Stack: '{org_name}/{project_name}/{stack_name}'")
        elif num_parts == 3 and all(parts):
            org_name = parts[0]
            project_name = parts[1]
            stack_name = parts[2]
            log.debug(
                f"Resolved stack input '{stack_input}' as Org/Project/Stack: '{org_name}/{project_name}/{stack_name}'")
        else:
            log.warn(f"Invalid stack input format: '{stack_input}'. Detected parts: {parts}. Skipping this input.")
            return None
        if not org_name or not project_name or not stack_name:
            raise ValueError(f"Resolution of stack input '{stack_input}' resulted in empty parts: "
                             f"org='{org_name}', project='{project_name}', stack='{stack_name}'")
        return f"{org_name}/{project_name}/{stack_name}"
    except ValueError as e:
        log.error(f"Error resolving stack name '{stack_input}': {e}")
        return None


# --- Function to get ONLY the Base Stack Reference ---
def get_base_stack_reference(config: Config, default_org: str) -> Optional[StackReference]:
    """
    Reads 'base_stack' from config, resolves it, and returns a single StackReference or None.
    """
    base_stack_config_value = config.get("base_stack")
    if not base_stack_config_value:
        log.info("'base_stack' configuration not found or empty.")
        return None

    qualified_name = resolve_stack_name(base_stack_config_value, default_org)

    if qualified_name:
        log.info(f"Resolved base_stack '{base_stack_config_value}' to StackReference: '{qualified_name}'")
        return StackReference(qualified_name)
    else:
        log.warn(f"Could not resolve base_stack name: '{base_stack_config_value}'")
        return None


def _get_stack_var_implementation(key: str,
                                  current_config: Config,
                                  base_stack_ref: Optional[StackReference],  # Takes the single base stack ref
                                  exports: Dict[str, Any],
                                  propagate: bool,
                                  propagate_as: str) -> Optional[Any]:
    """
    (Internal Implementation) Retrieves an output value using the original simplified priority:
    1. Current stack's configuration (synchronous).
    2. If not found locally, the base stack's output (if base_stack_ref is valid, asynchronous Output).
    """
    # Support for StackVar objects by converting them to strings
    if hasattr(key, '__class__') and key.__class__.__name__ == 'StackVar':
        key = str(key)
    
    # 1. Check current stack's config first (Synchronous)
    value = current_config.get(key)
    if value is not None:
        log.debug(f"Found key '{key}' in current stack's config.")
        if propagate:
            exports[key] = value
        return value

    # 2. If not found locally, check the provided base_stack_ref
    if base_stack_ref is not None:
        log.debug(f"Key '{key}' not found in current config, returning Output from base stack")
        output_value = base_stack_ref.get_output(key)  # Returns an Output
        if propagate or propagate_as:
            if propagate_as is None:
                propagate_as = key
            exports[propagate_as] = output_value  # Store the Output object itself
        return output_value
    else:
        # Key not found locally and no valid base_stack_ref provided
        log.debug(f"Key '{key}' not found in current config and no valid base stack reference available.")
        return None


# --- Dependency Injection Setup (Simplified) ---
class Core(containers.DeclarativeContainer):  # Class name is Core

    config = providers.Singleton(Config)

    default_organization = providers.Factory(
        lambda: pulumi.get_organization() or DEFAULT_ORG
    )

    # Provider that resolves ONLY the base stack reference
    base_stack = providers.Singleton(
        get_base_stack_reference,  # Use the dedicated function
        config=config,
        default_org=default_organization
    )

    # Dictionary to store propagated outputs
    exports = providers.Singleton(dict)

    # Callable provider named 'get_output' uses the simplified internal implementation
    get_stack_var = providers.Callable(
        _get_stack_var_implementation,
        current_config=config,
        base_stack_ref=base_stack,  # Pass the single base_stack provider result
        exports=exports,
        propagate=providers.Object(False),
        propagate_as=None,
    )
