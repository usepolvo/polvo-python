import os

import toml


def update_pyproject(dependencies):
    pyproject_path = "src/pyproject.toml"
    if not os.path.exists(pyproject_path):
        print(f"{pyproject_path} not found.")
        return

    with open(pyproject_path, "r") as file:
        pyproject = toml.load(file)

    pyproject["project"]["dependencies"] = dependencies

    with open(pyproject_path, "w") as file:
        toml.dump(pyproject, file)

    print("Updated pyproject.toml with frozen dependencies.")


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
