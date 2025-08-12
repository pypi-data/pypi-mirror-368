from .LinkedList import *
from .DoubleLinkedList import *
from .LoopedLinkedList import *
from .DoubleLoopedLinkedList import *
from typing import Any


def jump(ll: DoubleLoopedLinkedList, start_value: Any | DoubleLoopedLinkedList.DoubleLoopedNode, jumps: int) -> DoubleLoopedLinkedList.DoubleLoopedNode:
    node = ll.find(start_value)
    if jumps >= 0:
        for _ in range(jumps):
            node = node.next
    else:
        for _ in range(-jumps):
            node = node.before
    return node


def has_duplicates(linkedlist: LinkedListType) -> bool:
    seen = set()
    for value in linkedlist:
        if value in seen:
            return True
        seen.add(value)
    return False


def reverse(linkedlist: LinkedListType) -> LinkedListType:
    new_ll = type(linkedlist)()
    node = linkedlist.head
    nodes = []
    while node:
        nodes.append(node.data)
        node = node.next
        if node == linkedlist.head or node is None:
            break
    for data in reversed(nodes):
        new_ll.append(data)
    return new_ll
