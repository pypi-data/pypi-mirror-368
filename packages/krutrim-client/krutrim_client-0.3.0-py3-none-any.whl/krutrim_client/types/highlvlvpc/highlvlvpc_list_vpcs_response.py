

from typing import List
from typing_extensions import TypeAlias

from .vpc_detail import VpcDetail

__all__ = ["HighlvlvpcListVpcsResponse"]

HighlvlvpcListVpcsResponse: TypeAlias = List[VpcDetail]
