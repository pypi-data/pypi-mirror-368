import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field, model_validator

import pulumi
from pulumi_docker import Image, DockerBuildArgs

from airspot_dev import container


def _is_in_pulumi_directory() -> bool:
    """Check if current working directory is within a .pulumi directory"""
    current_path = Path.cwd()
    return any(part == ".pulumi" for part in current_path.parts)


def _get_project_root() -> Path:
    """Get project root directory (parent of .pulumi directory)"""
    current_path = Path.cwd()
    
    # Find the .pulumi directory in the path
    for i, part in enumerate(current_path.parts):
        if part == ".pulumi":
            # Return the parent directory of .pulumi
            pulumi_parent_parts = current_path.parts[:i]
            if pulumi_parent_parts:
                return Path(*pulumi_parent_parts)
            else:
                # .pulumi is at root, return root
                return Path("/")
    
    # If no .pulumi found, return current directory
    return current_path


def _resolve_path_if_needed(path: str) -> str:
    """
    Resolve path relative to project root if:
    - Path is relative AND
    - We are in a .pulumi directory
    """
    path_obj = Path(path)
    
    # If path is absolute, return as-is
    if path_obj.is_absolute():
        return path
    
    # If we're not in a .pulumi directory, return as-is
    if not _is_in_pulumi_directory():
        return path
    
    # Resolve relative to project root
    project_root = _get_project_root()
    resolved_path = project_root / path
    return str(resolved_path)


class ImageBuildConfig(BaseModel):
    """Configuration for building Docker images
    
    This class defines the configuration for building a Docker image using Pulumi.
    It includes options for specifying resources to copy to the build context,
    Dockerfile location, build context, platform, and registry URL.
    
    Path Resolution:
    - If running in a .pulumi directory (or subdirectory), relative paths are resolved 
      relative to the project root (parent of .pulumi)
    - Absolute paths are always used as-is
    - This allows simpler path specifications when using the typical .pulumi structure
    """
    name: str
    copy_resources: List[str]
    dockerfile: str = "Dockerfile"
    context: str = ".build"
    platform: str = "linux/amd64"
    registry_url: Optional[Any] | None = None
    image_name: Optional[str] = None
    tag: str = "latest"
    build_args: Dict[str, str] = Field(default_factory=dict)
    extra_options: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}
    
    @model_validator(mode='after')
    def resolve_all_paths(self):
        """Resolve all paths (including defaults) using intelligent path resolution"""
        # Resolve dockerfile and context paths
        self.dockerfile = _resolve_path_if_needed(self.dockerfile)
        self.context = _resolve_path_if_needed(self.context)
        
        # Resolve all copy_resources paths
        self.copy_resources = [_resolve_path_if_needed(path) for path in self.copy_resources]
        
        return self


def prepare_build_context(config: ImageBuildConfig) -> str:
    """
    Prepares the build context by copying resources to the context directory.
    
    Args:
        config: The image build configuration
        
    Returns:
        The path to the prepared build context
    """
    # Create the build context directory if it doesn't exist
    context_path = Path(config.context)
    if not context_path.exists():
        context_path.mkdir(parents=True)
    
    # Copy all specified resources to the build context
    for resource in config.copy_resources:
        resource_path = Path(resource)
        dest_path = context_path / resource_path.name
        
        # Handle directories and files differently
        if resource_path.is_dir():
            if dest_path.exists() and dest_path.is_dir():
                shutil.rmtree(dest_path)
            shutil.copytree(resource_path, dest_path)
        else:
            shutil.copy2(resource_path, dest_path)
            
    # Handle Dockerfile - it's always relative to the current directory (or absolute)
    # not relative to the build context
    dockerfile_path = Path(config.dockerfile)
    dest_dockerfile = context_path / dockerfile_path.name
    
    # Copy the Dockerfile to the context directory if it exists
    if dockerfile_path.exists() and not dest_dockerfile.exists():
        shutil.copy2(dockerfile_path, dest_dockerfile)
    else:
        # Check if it's a path that needs to be resolved from current directory
        resolved_path = Path.cwd() / config.dockerfile
        if resolved_path.exists() and not dest_dockerfile.exists():
            shutil.copy2(resolved_path, dest_dockerfile)
        
    return str(context_path.absolute())


def get_image(config: ImageBuildConfig, resource_name: Optional[str] = None, depends_on=None) -> Image:
    """
    Creates a Pulumi Docker Image resource based on the provided configuration.
    
    Args:
        config: The image build configuration
        resource_name: Optional resource name (defaults to {name}-image)
        depends_on: Optional resource dependencies
        
    Returns:
        A Pulumi Docker Image resource
        
    Notes:
        To get the full image reference with digest, use image.repo_digest
        Example: pulumi.export("image_digest", image.repo_digest)
    """
    if not resource_name:
        resource_name = f"{config.name}-image"

    if not config.registry_url:
        config.registry_url = container.get_stack_var("registry_url")
    
    # Prepare the build context by copying resources
    prepared_context = prepare_build_context(config)
    
    # Get just the Dockerfile name (not path) for Docker build
    dockerfile_name = Path(config.dockerfile).name
    
    # Add debug info
    pulumi.log.info(f"Docker build context: {prepared_context}")
    pulumi.log.info(f"Dockerfile name: {dockerfile_name}")
    
    # Verify the Dockerfile exists in the build context
    dockerfile_full_path = os.path.join(prepared_context, dockerfile_name)
    if not os.path.exists(dockerfile_full_path):
        pulumi.log.error(f"Dockerfile not found at {dockerfile_full_path}")
        # Try to copy it directly as a last resort
        src_dockerfile = config.dockerfile
        if os.path.exists(src_dockerfile):
            shutil.copy2(src_dockerfile, dockerfile_full_path)
            pulumi.log.info(f"Copied Dockerfile from {src_dockerfile} to {dockerfile_full_path}")
    
    # Determine the image name
    image_name = config.image_name if config.image_name else config.name
    image_tag = pulumi.Output.concat(config.registry_url, "/", image_name, ":", config.tag)
    
    # Create build arguments
    build_args = DockerBuildArgs(
        context=prepared_context,
        dockerfile=dockerfile_full_path,  # Use absolute path to Dockerfile
        platform=config.platform,
        args=config.build_args,
        **config.extra_options
    )
    
    # Handle dependencies
    options = {}
    if depends_on:
        if isinstance(depends_on, list):
            options["depends_on"] = depends_on
        else:
            options["depends_on"] = [depends_on]
    
    # Create the Image resource
    return Image(
        resource_name=resource_name,
        image_name=image_tag,
        build=build_args,
        opts=pulumi.ResourceOptions(**options) if options else None
    )
