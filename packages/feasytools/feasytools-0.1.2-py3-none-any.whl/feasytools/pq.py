import heapq
from collections import deque
from typing import Dict, Generic, List, Tuple, TypeVar


QItem = TypeVar("QItem")


class Heap(Generic[QItem]):
    """Min heap"""

    def __init__(self):
        self._q = []

    def push(self, item: QItem):
        """Push, O(log n)"""
        heapq.heappush(self._q, item)

    def pop(self) -> QItem:
        """Pop, O(log n)"""
        return heapq.heappop(self._q)

    def remove(self, item: QItem) -> bool:
        """Remove element `item`, O(n)"""
        try:
            idx = self._q.index(item)
        except ValueError:
            return False
        self._q.pop(idx)
        heapq.heapify(self._q)
        return True

    @property
    def top(self) -> QItem:
        """Get the top element without popping it, O(1)"""
        return self._q[0]

    def __len__(self) -> int:
        return len(self._q)

    def __contains__(self, obj: QItem) -> bool:
        """Check if an element exists, O(n)"""
        return obj in self._q

    def empty(self) -> bool:
        """Check if the heap is empty, O(1)"""
        return len(self._q) == 0


class PQueue(Generic[QItem]):
    """Priority queue (Min heap)"""

    def __init__(self):
        self._q: "List[Tuple[int,QItem]]" = []

    def push(self, pri: int, item: QItem) -> None:
        """
        Push, O(log n)
            pri: Priority
            item: Element
        """
        heapq.heappush(self._q, (pri, item))

    def pop(self) -> "Tuple[int, QItem]":
        """Get the top element and pop it, O(log n)"""
        return heapq.heappop(self._q)

    def remove(self, item: QItem) -> bool:
        """Remove the first element of `item`, O(n). Return whether it's successful"""
        idx = -1
        for i, (_, data) in enumerate(self._q):
            if data == item:
                idx = i
                break
        if idx == -1:
            return False
        self._q.pop(idx)
        heapq.heapify(self._q)
        return True

    @property
    def top(self) -> "Tuple[int,QItem]":
        """Get the top value without popping it, O(1)"""
        return self._q[0]

    def __len__(self) -> int:
        return len(self._q)

    def __contains__(self, obj) -> bool:
        return obj in self._q

    def empty(self) -> bool:
        """Check if the queue is empty, O(1)"""
        return len(self._q) == 0

    def __str__(self) -> str:
        """Convert to string, O(n log n)"""
        q2 = self._q.copy()
        q2.sort()
        return str(q2)


class BufferedPQ(Generic[QItem]):
    """
    A priority queue (named q) with a buffer queue (named p).
    The priority queue size is fixed (n), and the buffer queue size is variable (m).
    Data enters the buffer queue, then enters the priority queue, and finally leaves the structure.
    """

    def __init__(self, p_size: int):
        self._sz = p_size
        self._P: "PQueue[QItem]" = PQueue()
        self._Q: "deque[Tuple[int,QItem]]" = deque()
        self._sP = set()
        self._sQ: "Dict[QItem, int]" = {}

    def __len__(self) -> int:
        return len(self._P) + len(self._Q)

    @property
    def p_size(self) -> int:
        """Get the size of the priority area, O(1)"""
        return self._sz

    @property
    def p_len(self) -> int:
        """Get the length of the priority area, O(1)"""
        return len(self._P)

    @property
    def q_len(self) -> int:
        """Get the length of the buffer area, O(1)"""
        return len(self._Q)

    def __contains__(self, obj: QItem) -> bool:
        """Check if an element exists, O(1)"""
        return obj in self._sP or obj in self._sQ

    def push(self, pri: int, obj: QItem) -> bool:
        """
        Push, O(log n)
            pri: Priority
            item: Element
        """
        if self.__contains__(obj):
            return False
        if len(self._P) < self._sz:
            self._P.push(pri, obj)
            self._sP.add(obj)
        else:
            self._Q.append((pri, obj))
            self._sQ[obj] = pri
        return True

    def top(self) -> "Tuple[int,QItem]":
        """Get the top element without popping it, O(1)"""
        return self._P.top

    def pop(self) -> "Tuple[int,QItem]":
        """Get the top element and pop it, O(log n)"""
        ret = self._P.pop()
        self._sP.remove(ret[1])
        if len(self._Q) > 0:
            pri, obj = self._Q.popleft()
            self._sQ.pop(obj)
            self._P.push(pri, obj)
            self._sP.add(obj)
        return ret

    def empty(self) -> bool:
        """Check if the queue is empty, O(1)"""
        return self._P.empty()

    def remove(self, obj: QItem) -> bool:
        """Remove the first element of `obj`, O(n+m). Return whether it's successful"""
        if self._P.remove(obj):
            self._sP.remove(obj)
            return True
        pri = self._sQ.pop(obj, None)
        if pri is None:
            return False
        self._Q.remove((pri, obj))
        return True

    def p_has(self, obj) -> bool:
        """Check if an element exists in the priority area, O(1)"""
        return obj in self._sP

    def q_has(self, obj) -> bool:
        """Check if an element exists in the buffer area, O(1)"""
        return obj in self._sQ

    def __str__(self) -> str:
        """Convert to string, O(nlogn+m)"""
        return f"BufferedPQ[P={self._P},Q={self._Q}]"


__all__ = ["Heap", "PQueue", "BufferedPQ"]