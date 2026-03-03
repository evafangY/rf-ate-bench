from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class TestResult:
    test_id: str
    label: str
    value: Union[float, str]
    unit: str
    min_spec: Optional[float]
    max_spec: Optional[float]
    status: str  # "PASS", "FAIL", "INFO"
