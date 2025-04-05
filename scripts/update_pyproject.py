import os
import re

import toml


def convert_to_version_range(dependency):
    """Convert an exact version dependency to a compatible version range."""
    # Extract package name and handle extras
    match = re.match(r"([a-zA-Z0-9_.-]+(?:\[[a-zA-Z0-9_,.-]+\])?)(==|>=|~=)?(.*)", dependency)
    if not match:
        return dependency

    package_full = match.group(1)  # Package name with optional extras
    version_op = match.group(2)
    version = match.group(3)

    # If it has an exact version, convert to a compatible version range
    if version_op == "==" and version:
        # Split version into components
        version_parts = version.split(".")
        if len(version_parts) >= 2:
            # Use compatible release range ~= for major.minor versions
            return f"{package_full}~={'.'.join(version_parts[:2])}"
        else:
            # Fallback for unusual version formats
            return f"{package_full}>={version}"

    # Return as is if it's already using a version range or has no version
    return dependency


def update_pyproject(dependencies):
    pyproject_path = "src/pyproject.toml"
    if not os.path.exists(pyproject_path):
        print(f"{pyproject_path} not found.")
        return

    with open(pyproject_path, "r") as file:
        pyproject = toml.load(file)

    # Get all optional dependencies to exclude them from main dependencies
    optional_deps = set()
    if "project" in pyproject and "optional-dependencies" in pyproject["project"]:
        for dep_group, deps in pyproject["project"]["optional-dependencies"].items():
            for i, dep in enumerate(deps):
                # Extract the package name without version
                package_name = (
                    dep.split("==")[0].split(">=")[0].split("~=")[0].split("[")[0].strip()
                )
                optional_deps.add(package_name)

                # Convert optional dependencies to use version ranges as well
                pyproject["project"]["optional-dependencies"][dep_group][i] = (
                    convert_to_version_range(dep)
                )

    # Filter out dependencies that are already in optional dependencies
    # and convert exact versions to version ranges for main dependencies
    filtered_dependencies = []
    for dep in dependencies:
        if not dep.strip():
            continue

        # Extract base package name for filtering
        base_package = dep.split("==")[0].split(">=")[0].split("~=")[0].split("[")[0].strip()

        # Skip if it's in optional dependencies
        if base_package in optional_deps:
            continue

        # Convert to version range
        filtered_dependencies.append(convert_to_version_range(dep))

    pyproject["project"]["dependencies"] = filtered_dependencies

    with open(pyproject_path, "w") as file:
        toml.dump(pyproject, file)

    print(
        "Updated pyproject.toml with dependency version ranges for both main and optional dependencies."
    )


def get_frozen_dependencies(requirements_file):
    if not os.path.exists(requirements_file):
        print(f"{requirements_file} not found.")
        return []

    with open(requirements_file, "r") as file:
        lines = file.readlines()

    dependencies = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    return dependencies


if __name__ == "__main__":
    requirements_file = "requirements.txt"
    dependencies = get_frozen_dependencies(requirements_file)
    if dependencies:
        update_pyproject(dependencies)
