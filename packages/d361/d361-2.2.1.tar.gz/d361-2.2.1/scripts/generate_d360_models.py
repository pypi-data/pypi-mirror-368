#!/usr/bin/env python3
# this_file: external/int_folders/d361/scripts/generate_d360_models.py
"""
Standalone script to generate Pydantic models from Document360 OpenAPI specification.

This script provides a convenient CLI interface for generating type-safe
Pydantic models from the Document360 API specification.

Usage:
    python generate_d360_models.py [OPTIONS]

Examples:
    # Generate models to default location
    python generate_d360_models.py
    
    # Generate to specific directory with forced refresh
    python generate_d360_models.py --output_dir custom/models --force_refresh
    
    # Use custom configuration file
    python generate_d360_models.py --config_file my_config.json
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import d361
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

if __name__ == "__main__":
    import asyncio
    from d361.api.generate_models import generate_models_cli
    import fire
    
    # Use fire to provide CLI interface
    def main(**kwargs):
        """Generate Pydantic models from Document360 OpenAPI specification."""
        return asyncio.run(generate_models_cli(**kwargs))
    
    fire.Fire(main)