#!/usr/bin/env python3
# this_file: external/int_folders/d361/src/d361/api/generate_models.py
"""
OpenAPI Model Generation Script

This script automatically generates Pydantic models from the Document360 
OpenAPI specification using datamodel-code-generator. It provides both 
programmatic and CLI interfaces for model generation.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field

from .openapi_integration import OpenApiIntegration, OpenApiConfig


class ModelGenerationConfig(BaseModel):
    """Configuration for model generation."""
    
    # Input configuration
    openapi_config: OpenApiConfig = Field(
        default_factory=OpenApiConfig,
        description="OpenAPI integration configuration"
    )
    
    # Output configuration
    output_dir: Path = Field(
        default_factory=lambda: Path("generated") / "models",
        description="Directory for generated models"
    )
    
    output_filename: str = Field(
        default="document360_models.py",
        description="Output filename for generated models"
    )
    
    # Generation options
    class_name_prefix: str = Field(
        default="",
        description="Prefix for generated class names"
    )
    
    class_name_suffix: str = Field(
        default="",
        description="Suffix for generated class names"
    )
    
    use_enum_field: bool = Field(
        default=True,
        description="Use Enum for string fields with constraints"
    )
    
    use_union_operator: bool = Field(
        default=True,
        description="Use union operator (|) for Union types"
    )
    
    target_python_version: str = Field(
        default="3.12",
        description="Target Python version"
    )
    
    use_double_quotes: bool = Field(
        default=True,
        description="Use double quotes for strings"
    )
    
    use_schema_description: bool = Field(
        default=True,
        description="Include schema descriptions as docstrings"
    )
    
    use_field_description: bool = Field(
        default=True,
        description="Include field descriptions"
    )
    
    snake_case_field: bool = Field(
        default=True,
        description="Convert camelCase to snake_case for field names"
    )
    
    strict_nullable: bool = Field(
        default=True,
        description="Use strict nullable types"
    )
    
    # Additional options
    enable_faux_immutability: bool = Field(
        default=False,
        description="Enable faux immutability (frozen models)"
    )
    
    use_annotated: bool = Field(
        default=True,
        description="Use Annotated types"
    )
    
    use_standard_collections: bool = Field(
        default=True,
        description="Use standard collections (list, dict) instead of typing"
    )


class GenerationResult(BaseModel):
    """Result of model generation."""
    
    success: bool = Field(..., description="Whether generation succeeded")
    output_file: Path = Field(..., description="Path to generated models file")
    model_count: int = Field(default=0, description="Number of models generated")
    spec_version: str = Field(..., description="OpenAPI spec version used")
    spec_hash: str = Field(..., description="Hash of OpenAPI spec")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")


class ModelGenerator:
    """
    Generator for Pydantic models from OpenAPI specifications.
    
    Uses datamodel-code-generator to create type-safe Pydantic models
    from Document360's OpenAPI specification.
    """
    
    def __init__(self, config: Optional[ModelGenerationConfig] = None):
        """
        Initialize the model generator.
        
        Args:
            config: Model generation configuration
        """
        self.config = config or ModelGenerationConfig()
        self.openapi_integration = OpenApiIntegration(self.config.openapi_config)
        
        logger.info(
            f"ModelGenerator initialized",
            output_dir=str(self.config.output_dir),
            target_python=self.config.target_python_version
        )
    
    async def generate_models(self, force_refresh: bool = False) -> GenerationResult:
        """
        Generate Pydantic models from OpenAPI specification.
        
        Args:
            force_refresh: Force refresh of OpenAPI spec from remote
            
        Returns:
            Generation result with details and status
            
        Raises:
            Exception: If generation fails
        """
        logger.info("Starting model generation")
        
        try:
            # Fetch OpenAPI specification
            spec = await self.openapi_integration.get_spec(force_refresh=force_refresh)
            logger.info(
                f"Using OpenAPI spec",
                title=spec.title,
                version=spec.api_version,
                schemas=len(spec.schemas)
            )
            
            # Ensure output directory exists
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate models using datamodel-code-generator
            output_file = self.config.output_dir / self.config.output_filename
            result = await self._generate_with_datamodel_codegen(spec, output_file)
            
            # Add header comment to generated file
            await self._add_file_header(output_file, spec)
            
            logger.info(
                f"Model generation completed successfully",
                output_file=str(output_file),
                models=result.model_count
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            return GenerationResult(
                success=False,
                output_file=self.config.output_dir / self.config.output_filename,
                spec_version="unknown",
                spec_hash="unknown",
                errors=[str(e)]
            )
    
    async def _generate_with_datamodel_codegen(
        self, 
        spec: Any,
        output_file: Path
    ) -> GenerationResult:
        """Generate models using datamodel-code-generator."""
        
        # Create temporary file with OpenAPI spec
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(spec.spec, tmp_file, indent=2)
            tmp_spec_path = Path(tmp_file.name)
        
        try:
            # Build command arguments
            cmd = [
                "datamodel-codegen",
                "--input", str(tmp_spec_path),
                "--output", str(output_file),
                "--input-file-type", "openapi",
                "--target-python-version", self.config.target_python_version,
            ]
            
            # Add optional arguments based on configuration
            if self.config.use_double_quotes:
                cmd.append("--use-double-quotes")
            
            if self.config.use_schema_description:
                cmd.append("--use-schema-description")
            
            if self.config.use_field_description:
                cmd.append("--use-field-description")
            
            if self.config.use_union_operator:
                cmd.append("--use-union-operator")
            
            if self.config.use_standard_collections:
                cmd.append("--use-standard-collections")
            
            if self.config.snake_case_field:
                cmd.append("--snake-case-field")
            
            if self.config.strict_nullable:
                cmd.append("--strict-nullable")
            
            if self.config.enable_faux_immutability:
                cmd.append("--enable-faux-immutability")
            
            if self.config.use_annotated:
                cmd.append("--use-annotated")
            
            if self.config.use_enum_field:
                cmd.append("--use-enum-field")
            
            if self.config.class_name_prefix:
                cmd.extend(["--class-name", f"{self.config.class_name_prefix}{{name}}{self.config.class_name_suffix}"])
            
            # Execute the command
            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = f"datamodel-codegen failed: {result.stderr}"
                logger.error(error_msg)
                return GenerationResult(
                    success=False,
                    output_file=output_file,
                    spec_version=spec.api_version,
                    spec_hash=spec.content_hash,
                    errors=[error_msg]
                )
            
            # Count generated models by counting class definitions
            model_count = 0
            if output_file.exists():
                content = output_file.read_text()
                model_count = content.count("class ")
            
            warnings = []
            if result.stderr:
                warnings = [line.strip() for line in result.stderr.split('\n') if line.strip()]
            
            return GenerationResult(
                success=True,
                output_file=output_file,
                model_count=model_count,
                spec_version=spec.api_version,
                spec_hash=spec.content_hash,
                warnings=warnings
            )
            
        finally:
            # Clean up temporary file
            tmp_spec_path.unlink()
    
    async def _add_file_header(self, output_file: Path, spec: Any) -> None:
        """Add header comment to generated models file."""
        if not output_file.exists():
            return
        
        # Read existing content
        existing_content = output_file.read_text()
        
        # Create header
        header = f'''# this_file: {output_file.as_posix()}
"""
Auto-generated Pydantic models from Document360 OpenAPI specification.

Generated on: {datetime.now().isoformat()}
OpenAPI Version: {spec.version}
API Version: {spec.api_version} 
Source: {spec.source_url}
Content Hash: {spec.content_hash}

DO NOT EDIT THIS FILE MANUALLY
This file is automatically generated from the OpenAPI specification.
Use the ModelGenerator to regenerate when the API specification changes.

To regenerate:
    from d361.api.generate_models import ModelGenerator
    generator = ModelGenerator()
    result = await generator.generate_models()
"""

# Generated dependencies
from __future__ import annotations

'''
        
        # Write header + existing content
        output_file.write_text(header + existing_content)
    
    async def check_for_updates(self) -> bool:
        """
        Check if the OpenAPI spec has updates that would require model regeneration.
        
        Returns:
            True if updates are available
        """
        return await self.openapi_integration.check_for_updates()
    
    async def get_spec_summary(self) -> Dict[str, Any]:
        """Get summary of the current OpenAPI specification."""
        return await self.openapi_integration.get_api_summary()
    
    async def close(self) -> None:
        """Close the OpenAPI integration and cleanup resources."""
        await self.openapi_integration.close()


async def generate_models_cli(
    output_dir: str = "generated/models",
    force_refresh: bool = False,
    config_file: Optional[str] = None
) -> None:
    """
    CLI interface for model generation.
    
    Args:
        output_dir: Output directory for generated models
        force_refresh: Force refresh of OpenAPI spec
        config_file: Path to configuration file (JSON)
    """
    logger.info("Starting CLI model generation")
    
    # Load configuration
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            config_data = json.loads(config_path.read_text())
            config = ModelGenerationConfig(**config_data)
        else:
            logger.warning(f"Configuration file not found: {config_file}")
            config = ModelGenerationConfig()
    else:
        config = ModelGenerationConfig()
    
    # Override output directory if provided
    config.output_dir = Path(output_dir)
    
    generator = ModelGenerator(config)
    
    try:
        result = await generator.generate_models(force_refresh=force_refresh)
        
        if result.success:
            print(f"✅ Models generated successfully!")
            print(f"   Output: {result.output_file}")
            print(f"   Models: {result.model_count}")
            print(f"   Version: {result.spec_version}")
            
            if result.warnings:
                print("⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   {warning}")
        else:
            print("❌ Model generation failed!")
            for error in result.errors:
                print(f"   Error: {error}")
            
    finally:
        await generator.close()


if __name__ == "__main__":
    import fire
    fire.Fire(generate_models_cli)