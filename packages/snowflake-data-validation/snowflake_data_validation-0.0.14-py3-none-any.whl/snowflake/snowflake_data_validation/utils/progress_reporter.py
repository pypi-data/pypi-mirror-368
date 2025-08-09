import json
import sys

from typing import Optional, TypedDict


class ProgressMetadata(TypedDict):

    """Interface for the metadata structure."""

    table: str
    columns: list[str]
    run_id: str
    run_start_time: str
    errorMessage: Optional[str]


def report_progress(metadata: ProgressMetadata) -> None:
    """Print a progress message to the standard output in the specified JSON structure.

    Args:
        metadata (dict): A dictionary containing metadata to include in the message.

    """
    message = {
        "channelName": "DataValidationMessage",
        "code": "TableDataValidationProgress",
        "metadata": metadata,
    }

    # Print the JSON message to standard output
    print(json.dumps(message), file=sys.stdout)
