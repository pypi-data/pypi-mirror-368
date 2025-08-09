import os
from amzsc.utils.file_worker import write_to_json


def test_write_to_json() -> None:
    """Test the write_to_json function."""
    data = {"key": "value"}
    file_path = "test_output.jsonl"

    try:
        write_to_json(file_path, data)
        with open(file_path, "r") as f:
            content = f.read().strip()
            assert_msg = "JSON content does not match expected output"
            assert content == '{"key": "value"}', assert_msg
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
