from dataclasses import dataclass

@dataclass
class ArrayAssignmentNode:
    array: any
    index: any
    value: any
