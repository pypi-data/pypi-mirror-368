import toml
from pathlib import Path
from venv import logger


class SystemToolError(Exception):
    pass


def get_version() -> str:
    try:
        with Path("pyproject.toml").open("r") as f:
            toml_dict = toml.load(f)
            print(toml_dict)
            return toml_dict.get("project", {}).get("version", "0.0.0")
    except (FileNotFoundError, toml.TomlDecodeError, KeyError) as e:
        raise SystemToolError(f"Failed to get version: {e}")
    except Exception as e:
        raise SystemToolError(f"Unknown error to get version: {e}")


def set_version(current_version: str) -> None:
    try:
        with Path("pyproject.toml").open("r") as current_file:
            toml_dict = toml.load(current_file)
            toml_dict["project"]["version"] = current_version
            toml_dict.update({"project": toml_dict["project"]})

            with open("pyproject.toml", "w") as update_file:
                toml.dump(toml_dict, update_file)
    except (toml.TomlDecodeError, KeyError) as e:
        raise SystemToolError(
            f"Failed to update version {current_file} with error: {e}"
        )
    except FileNotFoundError:
        raise SystemToolError("Failed to update version: pyproject.toml not found")
    except PermissionError:
        raise SystemToolError("Failed to update version: Permission denied")
    except Exception as e:
        raise SystemToolError(
            f"Unknow error to update version {current_file} with error: {e}"
        )


def update_version():
    current_version = get_version()
    logger.info(f"Current version {current_version}")
    major, minor, patch = current_version.split(".")
    new_version = f"{major}.{minor}.{int(patch) + 1}"
    set_version(new_version)
    logger.info(f"New version is {new_version}")
