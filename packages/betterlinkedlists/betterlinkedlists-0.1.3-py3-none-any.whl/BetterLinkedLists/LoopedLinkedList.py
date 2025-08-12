from .LinkedList import LinkedList, LinkedListType, BEFORE, AFTER
from typing import Any


class LoopedLinkedList(LinkedList):
    class LoopedNode(LinkedList.Node):
        def __init__(self, data):
            super().__init__(data)
            self.next: LoopedLinkedList.LoopedNode = None

    head: LoopedNode

    def append(self, data: Any | LoopedNode):
        new_node = LoopedLinkedList.LoopedNode(data) if not type(data) == LoopedLinkedList.LoopedNode else data
        if not self.head:
            self.head = new_node
            new_node.next = self.head
            return
        last = self.head
        while not last.next is self.head:
            last = last.next
        last.next = new_node
        new_node.next = self.head

    
    def remove(self, data: Any | LoopedNode):
        self.find(data)
        if isinstance(data, LinkedListType.NodeType):
            for _ in range(len(self.findall(data))):
                if self.head == data:
                    last = self.head
                    while last.next != self.head:
                        last = last.next
                    last.next = self.head.next
                    self.head = self.head.next
                    continue
                last = self.head
                while last.next:
                    if last.next == data:
                        break
                    last = last.next
                last.next = last.next.next
            return
        for _ in range(len(self.findall(data))):
            if self.head.data == data:
                last = self.head
                while last.next != self.head:
                    last = last.next
                last.next = self.head.next
                self.head = self.head.next
                continue
            last = self.head
            while last.next:
                if last.next.data == data:
                    break
                last = last.next
            last.next = last.next.next


    def insert(self, data: Any | LoopedNode, where: bool, value: Any | LoopedNode):
        '''
        where = True: insert before
        where = False: insert after
        '''
        new_node = LoopedLinkedList.LoopedNode(data) if not type(data) == LoopedLinkedList.LoopedNode else data

        if where:
            if self.head == value:
                last = self.head
                while last.next != self.head:
                    last = last.next
                new_node.next = self.head
                last.next = new_node
                self.head = new_node
                return
            last = self.head
            while last.next:
                if last.next == value:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node
        else:
            last = self.head
            while last.next:
                if last == value:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node


    def find(self, value: Any | LoopedNode) -> LoopedNode:
        return super().find(value)
    

    def findall(self, value: Any | LoopedNode) -> list[LoopedNode]:
        return super().findall(value)
    

    def __repr__(self):
        r = 'LoopedLinkedList{\n'
        node = self.head
        if node is None: return r + '    empty\n}'
        r += f'     (head) data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n' if not node.next == self.head else f'    (tail) (head) data: {node.data}'
        node = node.next
        if node.next == self.head:
            r += '\n}'
            return r
        r += f'     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n' if not node.next == self.head else f'     (tail) data: {node.data}, next: (head) {node.next.data}'
        while node != self.head:
            node = node.next
            if node == self.head or node is None:
                break
            r += f'     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n' if not node.next == self.head else f'     (tail) data: {node.data}, next: (head) {node.next.data}'
        r += '\n}'
        return r
