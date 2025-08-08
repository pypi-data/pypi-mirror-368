# #!/bin/bash

# # Get current version from pyproject.toml
# current_version=$(grep -oP '(?<=version = ")[^"]*' pyproject.toml)

# # Split version into parts
# IFS='.' read -ra version_parts <<< "$current_version"
# patch_version=$((version_parts[2] + 1))

# # Create new version
# new_version="${version_parts[0]}.${version_parts[1]}.$patch_version"

# # Update version in pyproject.toml
# sed -i "s/version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml

# Build and publish
UV_TOKEN=pypi-AgEIcHlwaS5vcmcCJGU0ZTMxZjg5LTI0MzktNDExZS1hMDExLWU1ZjEyY2NhYTE5NwACKlszLCJlOWJlNjNkZS0wMTgxLTQyNGItYTc4ZC02NTU2MmY2NDdmNjUiXQAABiCHj2A57TMp4DT2jVfYBvP0UsKymbnHccNonu08WXwInw

uv build
uv publish --token "$UV_TOKEN"
