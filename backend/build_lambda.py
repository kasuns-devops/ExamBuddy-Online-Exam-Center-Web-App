#!/usr/bin/env python
"""Build Lambda deployment package with all dependencies"""
import zipfile
import os
from pathlib import Path

backend_dir = Path(".")
venv_site_packages = backend_dir / ".venv" / "Lib" / "site-packages"
zip_file = backend_dir / "lambda_function.zip"

if not venv_site_packages.exists():
    print(f"Error: site-packages not found at {venv_site_packages}")
    exit(1)

# Remove old zip
if zip_file.exists():
    zip_file.unlink()

with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add source code
    for root, dirs, files in os.walk(backend_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', '.pytest_cache', 'node_modules'}]
        
        for file in files:
            if file in {'lambda_function.zip', 'configure_options.py', 'build_lambda.py', 'options_cors.json'} or file.endswith('.pyc') or file.startswith('.'):
                continue
            
            fpath = Path(root) / file
            arcname = fpath.relative_to(backend_dir)
            zf.write(fpath, arcname)
    
    # Add site-packages
    for root, dirs, files in os.walk(venv_site_packages):
        for file in files:
            if file.endswith('.pyc') or file.startswith('.'): 
                continue
            
            fpath = Path(root) / file
            arcname = fpath.relative_to(venv_site_packages.parent.parent)
            zf.write(fpath, arcname)

size_mb = zip_file.stat().st_size / (1024 * 1024)
print(f"✓ Lambda package built: {size_mb:.1f} MB")
