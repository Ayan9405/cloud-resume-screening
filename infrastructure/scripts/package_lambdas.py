"""Helper script to package backend lambda code and dependencies into a zip artifact."""

import os
import shutil
import zipfile
import subprocess
import sys

def package_lambdas():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    backend_dir = os.path.join(project_root, "backend")
    dist_dir = os.path.join(project_root, "infrastructure", "dist")
    zip_path = os.path.join(dist_dir, "backend_lambda.zip")

    os.makedirs(dist_dir, exist_ok=True)
    print(f"[INFO] Packaging backend lambdas from {backend_dir} -> {zip_path}")

    # Create temporary build dir
    build_dir = os.path.join(dist_dir, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    # Copy backend handlers and services
    shutil.copytree(os.path.join(backend_dir, "handlers"), os.path.join(build_dir, "handlers"))
    shutil.copytree(os.path.join(backend_dir, "services"), os.path.join(build_dir, "services"))

    # Create zip archive
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith((".pyc", ".pyo")) or "__pycache__" in root:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, build_dir)
                zipf.write(file_path, arcname)

    # Clean up temp build dir
    shutil.rmtree(build_dir)
    print(f"[SUCCESS] Created Lambda package: {zip_path} ({os.path.getsize(zip_path)} bytes)")

if __name__ == "__main__":
    package_lambdas()
