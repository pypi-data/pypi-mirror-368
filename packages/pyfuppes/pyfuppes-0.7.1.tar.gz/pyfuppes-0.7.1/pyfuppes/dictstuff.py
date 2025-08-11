# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Dictionary tools."""

import tomllib
from pathlib import Path
from typing import Any, Self

# --------------------------------------------------------------------------------------------------


class DotDict(dict):
    """Wrapper class around dict for dot-notation access to dictionary keys."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize DotDict and recursively convert nested dictionaries."""
        super().__init__(*args, **kwargs)
        self._convert_nested()

    def _convert_nested(self, path: str = "") -> None:
        """Convert nested dictionaries to DotDict instances and validate keys."""
        for key, value in list(self.items()):
            # Validate keys
            if not isinstance(key, str):
                continue

            # Check for invalid attribute names
            if not key.isidentifier():
                print(
                    f"Warning: '{path}{key}' is not a valid Python identifier and cannot be accessed with dot notation"
                )

            # Check for reserved dictionary method names
            if key in dir(dict) and key not in ("__class__", "__dict__"):
                print(f"Warning: '{path}{key}' overrides a built-in dictionary method")

            # Recursively convert nested dictionaries
            if isinstance(value, dict) and not isinstance(value, DotDict):
                self[key] = DotDict(value)
                self[key]._convert_nested(f"{path}{key}.")
            elif isinstance(value, list):
                # Handle lists and recursively process any dictionaries within them
                self[key] = self._process_list_items(value, f"{path}{key}")

    def _process_list_items(self, items: list[Any], path: str) -> list[Any]:
        """Recursively process items in a list, converting any dicts to DotDict."""
        processed_items = []
        for i, item in enumerate(items):
            if isinstance(item, dict) and not isinstance(item, DotDict):
                dot_dict_item = DotDict(item)
                dot_dict_item._convert_nested(f"{path}[{i}].")
                processed_items.append(dot_dict_item)
            elif isinstance(item, list):
                # Handle nested lists recursively
                processed_items.append(
                    self._process_list_items(item, f"{path}[{i}]")  # type:ignore
                )  # type:ignore
            else:
                processed_items.append(item)
        return processed_items

    @classmethod
    def from_toml_data(cls, toml_data: dict[str, Any]) -> Self:
        """Create a DotDict instance from TOML data."""
        return cls(toml_data)

    @classmethod
    def from_toml_file(cls, file_path: str | Path) -> Self:
        """Load a TOML file into a DotDict instance."""
        with open(file_path, "rb") as f:
            config_data = tomllib.load(f)
        return cls(config_data)

    def __getattr__(self, key: str) -> Any:
        """Enable dot notation access for dictionary keys."""
        if key in self:
            return self[key]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any) -> None:
        """Enable dot notation assignment for dictionary keys."""
        # Convert dictionaries to DotDict when setting attributes
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        elif isinstance(value, list):
            # Process lists when setting them as attributes
            value = self._process_list_items(value, key)
        self[key] = value

    def __delattr__(self, key: str) -> None:
        """Enable dot notation deletion for dictionary keys."""
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")


# --------------------------------------------------------------------------------------------------


def compare_dictionaries(
    reference: dict[str, Any], candidate: dict[str, Any]
) -> tuple[list[str], list[str], bool]:
    """
    Compares two dictionaries based on their keys, including nested keys.

    Args:
        reference: The reference dictionary.
        candidate: The dictionary to compare against the reference.

    Returns:
        A tuple containing:
            - A list of keys missing in the candidate.
            - A list of keys present in the candidate but not in the reference.
            - A boolean indicating whether the comparison failed (missing keys > 0).

    Generated with Gemini Flash 2.0, edited.
    """

    missing_keys: list[str] = []
    extra_keys: list[str] = []

    def _traverse_and_compare(
        ref_dict: dict[str, Any], cand_dict: dict[str, Any], prefix: str = ""
    ) -> None:
        for key in ref_dict:
            full_key = prefix + str(key) if prefix else str(key)  # Handle nested keys
            if key not in cand_dict:
                missing_keys.append(full_key)
            elif isinstance(ref_dict[key], dict) and isinstance(cand_dict[key], dict):
                _traverse_and_compare(
                    ref_dict[key], cand_dict[key], full_key + "."
                )  # Recurse for nested dictionaries

        for key in cand_dict:
            full_key = prefix + str(key) if prefix else str(key)
            if key not in ref_dict:
                is_nested_extra = False
                for existing_key in reference:
                    if (
                        isinstance(reference[existing_key], dict)
                        and isinstance(cand_dict[key], dict)
                        and str(key).startswith(str(existing_key) + ".")
                    ):
                        is_nested_extra = True
                if not is_nested_extra:
                    extra_keys.append(full_key)

    _traverse_and_compare(reference, candidate)

    return missing_keys, extra_keys, len(missing_keys) > 0
