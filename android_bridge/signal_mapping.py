import json
from dataclasses import dataclass


@dataclass
class SignalMapping:
    signal: str
    property_id: int
    area_id: int


def parse_signal_mappings(mapping_filename: str) -> dict[str, SignalMapping]:
    signal_mappings = {}

    try:
        with open(mapping_filename, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading mapping file: {e}")
        raise e

    required_fields = {"signal", "propertyId", "areaId"}
    for obj in data:
        if not isinstance(obj, dict) or not required_fields.issubset(obj):
            print(f"Warning: Skipping invalid mapping object: {obj}")
            continue
        try:
            mapping = SignalMapping(
                signal=obj["signal"],
                property_id=obj["propertyId"],
                area_id=obj["areaId"],
            )
            signal_mappings[mapping.signal] = mapping
        except Exception as e:
            print(f"Warning: Failed to parse mapping object {obj}: {e}")

    return signal_mappings
