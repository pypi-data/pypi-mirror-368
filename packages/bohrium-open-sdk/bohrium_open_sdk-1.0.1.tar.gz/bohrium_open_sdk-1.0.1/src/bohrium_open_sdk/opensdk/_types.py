from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Union, Optional

JobInputType = Union[int, str, float, bool, List, Dict, None]


@dataclass
class UploadInputItem:
    input_field: Optional[str]
    """_summary_
    InputItem remote planned path
    this value will auto be filled by the SDK
    """
    input_path: Optional[str]
    src: Union[str, Path]

    def __init__(self, *, src: Union[str, Path], input_field: Optional[str]=None):
        self.input_field = input_field
        self.src = src
