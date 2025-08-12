import json

from .constants import ACTION_VERSION
from .types import ActionType


def get_raw_action(action_type: ActionType, action: bytes | str) -> bytes:
    header = bytes([ACTION_VERSION])

    action_id = action_type.value
    header += action_id.to_bytes(3, "big")

    if isinstance(action, str):
        action = bytes.fromhex(action.lstrip("0x"))

    return header + action


def load_abi(name: str):
    with open(f"abis/{name}.json", "r") as f:
        return json.load(f)
