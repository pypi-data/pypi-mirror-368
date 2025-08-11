from dataclasses import dataclass
from typing import List

@dataclass
class ArrayLiteralNode:
    elements: List

@dataclass
class IndexAccessNode:
    object: any
    index: any
