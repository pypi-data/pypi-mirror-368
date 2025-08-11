from dataclasses import dataclass
from typing import Optional
from parser import ASTNode

@dataclass
class ForStatementNode(ASTNode):
    init: Optional[ASTNode]
    condition: Optional[ASTNode]
    increment: Optional[ASTNode]
    body: ASTNode
