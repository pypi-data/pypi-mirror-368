from .LoopedLinkedList import LoopedLinkedList
from .DoubleLinkedList import DoubleLinkedList
from .LinkedList import _Node_T, BEFORE, AFTER
from typing import Any


class DoubleLoopedLinkedList(DoubleLinkedList, LoopedLinkedList):
    class DoubleLoopedNode(DoubleLinkedList.DoubleNode, LoopedLinkedList.LoopedNode):
        def __init__(self, data):
            super().__init__(data)
            self.next: DoubleLoopedLinkedList.DoubleLoopedNode = None
            self.before: DoubleLoopedLinkedList.DoubleLoopedNode = None

    head: DoubleLoopedNode

    def append(self, data: Any | _Node_T):
        new_node = DoubleLoopedLinkedList.DoubleLoopedNode(data) if not type(data) == DoubleLoopedLinkedList.DoubleLoopedNode else data
        if not self.head:
            self.head = new_node
            new_node.before = self.head
            new_node.next = self.head
            return
        last = self.head
        while last.next != self.head:
            last = last.next
        last.next = new_node
        new_node.before = last
        new_node.next = self.head
        self.head.before = new_node


    def remove(self, data: Any | _Node_T):
        self.find(data)
        for _ in range(len(self.findall(data))):
            if self.head.data == data:
                last = self.head
                while last.next != self.head:
                    last = last.next
                last.next = self.head.next
                self.head = self.head.next
                self.head.before = last
                continue
            last = self.head
            while last.next:
                if last.next.data == data:
                    break
                last = last.next
            last.next = last.next.next
            last.next.next.before = last


    def insert(self, data: Any | _Node_T, where: bool, value: Any | _Node_T):
        '''
        where = True: insert before
        where = False: insert after
        '''
        new_node = DoubleLoopedLinkedList.DoubleLoopedNode(data) if not type(data) == DoubleLoopedLinkedList.DoubleLoopedNode else data

        if where:
            if self.head == value:
                last = self.head
                while last.next != self.head:
                    last = last.next
                new_node.next = self.head
                new_node.before = last
                last.next = new_node
                self.head = new_node
                new_node.next.before = new_node
                return
            last = self.head
            while last.next:
                if last.next == value:
                    break
                last = last.next
            new_node.next = last.next
            new_node.before = last
            last.next.before = new_node
            last.next = new_node
        else:
            last = self.head
            while last.next:
                if last == value:
                    break
                last = last.next
            last.next.before = new_node
            new_node.next = last.next
            new_node.before = last
            last.next = new_node


    def find(self, value: Any | _Node_T) -> _Node_T:
        return super().find(value)
    

    def findall(self, value: Any | _Node_T) -> list[_Node_T]:
        return super().findall(value)
    

    def __repr__(self):
        r = 'DoubleLoopedLinkedList{\n'
        node = self.head
        if node is None: return r + '    empty\n}'
        r += f'     (head) data: {node.data}, next: {node.next.data}, before: (tail) {node.before.data}\n' if not node.next == self.head else f'    (tail) (head) data: {node.data}'
        node = node.next
        if node == self.head:
            r += '\n}'
            return r
        r += f'     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}, before: {node.before.data if not node.before == self.head else '(head) ' + node.before.data}\n' if not node.next == self.head else f'     (tail) data: {node.data}, next: (head) {node.next.data}, before: {node.before.data if not node.before == self.head else '(head) ' + node.before.data}'
        while node != self.head:
            node = node.next
            if node == self.head or node is None:
                break
            r += f'     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}, before: {node.before.data}\n' if not node.next == self.head else f'     (tail) data: {node.data}, next: (head) {node.next.data}, before: {node.before.data}'
        r += '\n}'
        return r
