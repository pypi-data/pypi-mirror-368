from typing import Any, Self, NoReturn

BEFORE = True
AFTER = False


class ItemNotFoundError(Exception):
    """
    Item does not appear in the LinkedList.
    """
    pass


class LinkedListType:
    class NodeType:
        def __init__(self):
            self.data = None
            self.next: LinkedListType.NodeType | None = None
            self.before: LinkedListType.NodeType | None = None

        def __eq__(self, other):
            if isinstance(other, LinkedListType.NodeType):
                return self.data == other.data
            else:
                return self.data == other
    
        def __str__(self):
            return str(self.data)

    head: NodeType | None = None
    def find(self, item: Any | NodeType) -> NodeType: return LinkedListType.NodeType()
    def findall(self, item: Any | NodeType) -> list[NodeType]: return [LinkedListType.NodeType()]
    def append(self, item: Any | NodeType): pass
    def remove(self, item: Any | NodeType): pass
    def insert(self, data: Any | NodeType, where: bool, value: Any | NodeType): pass

    def __iter__(self) -> Self:
        return self
    def __next__(self) -> Any | NoReturn:
        raise TypeError(f"{self} is not subscriptable")
    def __len__(self) -> int:
        return -1
    def __getitem__(self, n) -> NodeType | NoReturn:
        raise TypeError(f"{self} is not subscriptable")
    def __eq__(self, other) -> bool:
        return False
    def __repr__(self) -> str:
        return f"<{__name__}.LinkedListType object at {id(self)}>"

class LinkedList(LinkedListType):
    class Node(LinkedListType.NodeType):
        def __init__(self, data):
            self.data = data
            self.next: LinkedList.Node | None = None

    head: Node

    def __init__(self, *args):
        self.head: LinkedList.Node | None = None
        self._iter_node = None
        if len(args) == 1:
            for item in iter(args[0]):
                self.append(item)
        else:
            for item in args:
                self.append(item)

    def append(self, data: Any | Node):
        new_node = LinkedList.Node(data) if not type(data) is LinkedList.Node else data
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node


    def insert(self, data: Any | Node, where: bool, value: Any | Node):
        '''
        where = True: insert before
        where = False: insert after
        '''
        try:
            self.find(value)
            assert self.head is not None
        except (ItemNotFoundError, AssertionError):
            raise ItemNotFoundError(f"Cannot insert {'before' if where else 'after'} '{str(value)}': '{str(value)}' is not a member of the LinkedList.")
        new_node = LinkedList.Node(data) if not type(data) == LinkedList.Node else data

        if where:
            if self.head == value:
                new_node.next = self.head
                self.head = new_node
                return
            last = self.head
            while last.next is not None:
                if last.next == value or last.next.next is None:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node
            return
        else:
            last = self.head
            while last.next is not None:
                if last == value or last.next is None:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node
            return


    def remove(self, data: Any | Node):
        for _ in range(len(self.findall(data))):
            try:
                self.find(data)
                assert self.head is not None
            except (ItemNotFoundError, AssertionError):
                raise ItemNotFoundError("The item was not found in the LinkedList.")
            if data == self.head:
                self.head = self.head.next
                continue
            last = self.head
            while last.next is not None:
                if data == last.next or last.next is None:
                    break
                last = last.next
            if last.next is not None:
                last.next = last.next.next
        return


    def __iter__(self):
        self._iter_node = self.head
        self._iter_started = False
        return self

    def __next__(self):
        if self._iter_node == None or (self._iter_node == self.head and self._iter_started):
            self._iter_node = self.head
            self._iter_started = False
            raise StopIteration
        data = self._iter_node.data
        self._iter_node = self._iter_node.next
        self._iter_started = True
        return data
    

    def __len__(self):
        count = 0
        for _ in self:
            count += 1
        return count
    

    def __getitem__(self, n):
        if n < 0:
            n = len(self) + n
        node = self.head
        idx = 0
        while node:
            if idx == n:
                return node
            node = node.next
            idx += 1
            if node == self.head or node is None:
                break
        raise IndexError("LinkedList index out of range")
    

    def find(self, value: Any | Node) -> Node:
        node = self.head
        while node:
            if node == value:
                return node
            node = node.next
            if node is self.head or node is None:
                break
        raise ItemNotFoundError("The item was not found in the LinkedList.")
    

    def findall(self, value: Any | Node) -> list[Node]:
        self.find(value)
        nodes = []
        node = self.head
        while node is not None:
            if node == value:
                nodes.append(node)
            node = node.next
            if node is self.head or node is None:
                break
        return nodes
    

    def __eq__(self, other):
        if not isinstance(other, LinkedListType):
            return False
        
        if len(self) != len(other):
            return False
        
        return all([self[i] == other[i] for i in range(len(self))])

    
    def __repr__(self):
        r = 'LinkedList{\n'
        node = self.head
        if node is None: return r + '    empty\n}'
        r += f'     (head) data: {node.data}, next: {node.next.data if not node.next.next == None else '(tail) ' + node.next.data}\n' if not node.next == None else f'    (tail) (head) data: {node.data}'
        while node:
            node = node.next
            if node == self.head or node is None:
                break
            r += f'     data: {node.data}, next: {node.next.data if not node.next.next == None else '(tail) ' + node.next.data}\n' if not node.next == None else f'     (tail) data: {node.data}'
        r += '\n}'
        return r
   