"""Transform functions for `ties`."""

import yaml


def trivy_yaml(gitignore: str) -> str:
    """Transform for a `.gitignore` -> `trivy.toml` tie."""
    lines = [line.strip() for line in gitignore.split("\n")]
    lines = [line for line in lines if (not line.startswith("#")) and (len(line) > 0)]
    lines = [f"**/{line}" for line in lines]
    file_lines = [line for line in lines if not line.endswith("/")]
    dir_lines = [line for line in lines if line.endswith("/")]
    trivy_config = {
        "fs": {
            "skip-dirs": sorted(dir_lines),
            "skip-files": sorted(file_lines),
        }
    }
    return yaml.dump(trivy_config)
