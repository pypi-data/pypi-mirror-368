"""
Debug utilities for troubleshooting Pulumi issues.
"""
import pulumi
from typing import Any
from airspot_dev.pulumi_ import StackVar, is_stack_var
from airspot_dev import container


def debug_stack_var(var_name: str, var_value: Any):
    """
    Debug a StackVar value to understand its content and behavior.
    """
    pulumi.log.info(f"==== DEBUG StackVar: {var_name} ====")
    pulumi.log.info(f"  Value: {var_value}")
    pulumi.log.info(f"  Type: {type(var_value)}")
    pulumi.log.info(f"  is_stack_var: {is_stack_var(var_value)}")
    
    if is_stack_var(var_value):
        pulumi.log.info(f"  StackVar repr: {repr(var_value)}")
        pulumi.log.info(f"  StackVar str: {str(var_value)}")
        pulumi.log.info(f"  StackVar dir: {dir(var_value)}")
        
        # Try to extract the original variable name
        try:
            var_key = str(var_value)
            pulumi.log.info(f"  Extracted key: {var_key}")
            
            # Try to resolve the value
            resolved_value = container.get_stack_var(var_key)
            pulumi.log.info(f"  Resolved value: {resolved_value}")
            pulumi.log.info(f"  Resolved type: {type(resolved_value)}")
        except Exception as e:
            pulumi.log.error(f"  Error extracting/resolving: {str(e)}")
    
    pulumi.log.info("==== END DEBUG ====")
    return var_value


def debug_container_get_stack_var(key: str):
    """
    Debug the container.get_stack_var function.
    """
    pulumi.log.info(f"==== DEBUG container.get_stack_var({key}) ====")
    
    try:
        value = container.get_stack_var(key)
        pulumi.log.info(f"  Returned value: {value}")
        pulumi.log.info(f"  Returned type: {type(value)}")
    except Exception as e:
        pulumi.log.error(f"  Error in get_stack_var: {str(e)}")
    
    pulumi.log.info("==== END DEBUG ====")
    return value


def debug_direct_vs_stackvar(key: str):
    """
    Compare direct call vs. StackVar usage.
    """
    pulumi.log.info(f"==== DEBUG Direct vs StackVar: {key} ====")
    
    # Direct call
    try:
        direct_value = container.get_stack_var(key)
        pulumi.log.info(f"  Direct call value: {direct_value}")
        pulumi.log.info(f"  Direct call type: {type(direct_value)}")
    except Exception as e:
        pulumi.log.error(f"  Error in direct call: {str(e)}")
    
    # StackVar usage
    try:
        stack_var = StackVar(key)
        pulumi.log.info(f"  Created StackVar: {stack_var}")
        pulumi.log.info(f"  StackVar type: {type(stack_var)}")
        
        # Try to resolve using container.get_stack_var(stack_var)
        stack_var_direct = container.get_stack_var(stack_var)
        pulumi.log.info(f"  stack_var_direct value: {stack_var_direct}")
        pulumi.log.info(f"  stack_var_direct type: {type(stack_var_direct)}")
        
        # Try to resolve using container.get_stack_var(str(stack_var))
        stack_var_str = container.get_stack_var(str(stack_var))
        pulumi.log.info(f"  stack_var_str value: {stack_var_str}")
        pulumi.log.info(f"  stack_var_str type: {type(stack_var_str)}")
    except Exception as e:
        pulumi.log.error(f"  Error in StackVar usage: {str(e)}")
    
    pulumi.log.info("==== END DEBUG ====")


def debug_stackvar_creation(key: str):
    """Debug the creation and properties of a StackVar."""
    from airspot_dev.pulumi_ import StackVar
    pulumi.log.info(f"==== DEBUG StackVar Creation for {key} ====")
    
    # Create a StackVar
    sv = StackVar(key)
    
    # Basic information
    pulumi.log.info(f"  StackVar object: {sv}")
    pulumi.log.info(f"  Type: {type(sv)}")
    pulumi.log.info(f"  StackVar dir: {dir(sv)}")
    
    # Class information
    if hasattr(sv, '__class__'):
        pulumi.log.info(f"  __class__: {sv.__class__}")
        pulumi.log.info(f"  __class__.__name__: {sv.__class__.__name__}")
    
    # Try to access as string
    pulumi.log.info(f"  str(sv): {str(sv)}")
    pulumi.log.info(f"  repr(sv): {repr(sv)}")
    
    # Test equality
    pulumi.log.info(f"  sv == key: {sv == key}")
    pulumi.log.info(f"  sv is key: {sv is key}")
    
    # Test function behavior
    from airspot_dev.pulumi_ import is_stack_var
    pulumi.log.info(f"  is_stack_var(sv): {is_stack_var(sv)}")
    pulumi.log.info(f"  is_stack_var(key): {is_stack_var(key)}")
    
    # Try serialization if possible
    try:
        import json
        json_sv = json.dumps(sv)
        pulumi.log.info(f"  JSON serialized: {json_sv}")
    except Exception as e:
        pulumi.log.info(f"  JSON serialization failed: {e}")
    
    pulumi.log.info("==== END DEBUG ====")
    return sv
