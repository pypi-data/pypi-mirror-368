import json

from actionstreamer.WebService.API import PatchOperation


def add_patch_operation(operations: list, field_name: str, value: str | int) -> list:
    operations.append(PatchOperation(field_name, value))


def generate_patch_json(operations: list) -> str:
    # Convert all values to strings
    operations_str = [{k: str(v) for k, v in vars(op).items()} for op in operations]
    json_data = json.dumps(operations_str)
    return json_data