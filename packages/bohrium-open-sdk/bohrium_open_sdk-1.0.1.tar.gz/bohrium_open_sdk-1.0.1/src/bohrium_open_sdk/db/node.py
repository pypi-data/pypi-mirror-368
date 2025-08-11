# -*- coding: UTF-8 -*-

from enum import Enum
from typing import List

'''
{
    "type":1,
    "field": "1",
    "op": "eq",
    "value": 2,
    "condition":"and/or",
    "sub":[]
}
'''


class Op(Enum):
    EQ = "eq"
    NEQ = "neq"
    BETWEEN = "between"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    LIKE = "like"
    IN = "in"
    NIN = "nin"
    ELEMENTMATCHOFNUM = "elemMatchOfNum"


class Condition(Enum):
    AND = "and"
    OR = "or"


class NodeType(Enum):
    NORMAL = 1
    Operator = 2
    UNKNOWN = 3


class Node:
    def __init__(self, key: str, op: Op, value):
        self.key = key
        self.op = op
        self.value = value
        self.type = NodeType.UNKNOWN

    def Or(self, *args):
        pass

    def And(self, *args):
        pass

    def get_op(self) -> Op:
        return self.op

    def dict(self):
        pass


class OperatorNode(Node):
    def __init__(self, op: Op, condition: Condition):
        super().__init__("", op, None)
        self.type = NodeType.Operator
        self.condition = condition
        self.stack = []
        self.children = []
        self.has_or = False

    def Or(self, *args):
        if len(args) == 1:
            args[0].condition = Condition.OR
            self._add_or(args[0])
            return self
        elif len(args) == 3:
            node = Entity(args[0], args[1], args[2])
            self._add_or(node)
            return self
        else:
            raise ValueError("args count err")

    def _add_or(self, node):  # 弹栈、打包、压入
        self.has_or = True
        if len(self.stack) > 0:
            group_list = []
            for child in self.stack:
                group_list.append(child)
            self.stack = []
            if len(group_list) > 0:
                self.children.append(group_list)

        self.stack.append(node)

    def And(self, *args):
        if len(args) == 1:
            args[0].condition = Condition.AND
            self._add_and(args[0])
            return self
        elif len(args) == 3:
            node = Entity(args[0], args[1], args[2])
            self._add_and(node)
            return self
        else:
            raise ValueError("args count err")

    def _add_and(self, node):
        self.stack.append(node)

    def dict(self):
        if len(self.stack) > 0:
            group_list = []
            for child in self.stack:
                group_list.append(child)
            self.stack = []
            if len(group_list) > 0:
                self.children.append(group_list)

        res = {}
        if self.has_or:
            res["type"] = NodeType.Operator.value
            res["groupOperator"] = Condition.OR.value
        else:
            res["type"] = NodeType.NORMAL.value
            res["groupOperator"] = Condition.AND.value

        sub = []
        for child in self.children:
            if self.has_or:
                if len(child) == 0:
                    continue
                elif len(child) == 1:
                    for c in child:
                        if isinstance(c, (OperatorNode, Entity)):
                            sub.append(c.dict())
                        else:
                            raise ValueError("can not find this node")
                else:
                    and_group = {
                        "type": NodeType.Operator.value,
                        "groupOperator": Condition.AND.value,
                    }
                    child_sub = []
                    for c in child:
                        if isinstance(c, (OperatorNode, Entity)):
                            child_sub.append(c.dict())
                        else:
                            raise ValueError("can not find this node")
                    and_group["sub"] = child_sub
                    sub.append(and_group)

            else:
                if len(child) == 0:
                    continue
                else:
                    for c in child:
                        if isinstance(c, (OperatorNode, Entity)):
                            sub.append(c.dict())
                        else:
                            raise ValueError("can not find this node")

        if len(sub) == 0:
            return None

        res = {
            "type": self.type.value if self.type else None,
            "groupOperator": "or" if self.has_or else "and",
            "sub": sub,
        }

        res = {k: v for k, v in res.items() if v is not None}
        return res


class Entity(Node):
    def __init__(self, key: str, op: Op, value):
        super().__init__(key, op, value)
        self.type = NodeType.NORMAL

    def Or(self, key: str, op: Op, value, condition: Condition):
        raise ValueError("entity can not add or")

    def And(self, key: str, op: Op, value, conditin: Condition):
        raise ValueError("entity can not add and")

    def dict(self):
        res = {
            "type": self.type.value,
            "field": self.key,
            "operator": self.op.value if self.op else None,
            "value": self.value,
        }

        res = {k: v for k, v in res.items() if v is not None}
        return res
