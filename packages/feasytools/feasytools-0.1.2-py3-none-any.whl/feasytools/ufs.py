from typing import Generic, TypeVar, Hashable, Iterable, Optional, Dict


TItem = TypeVar('TItem', bound=Hashable)


class UnionFindSet(Generic[TItem]):
    """A Union-Find (Disjoint Set) data structure implementation. Only path compression is used for optimization."""
    def __init__(self, items: Iterable[TItem]):
        self._mp:Dict[TItem, int] = {item: i for i, item in enumerate(items)}
        self._par = list(range(len(self._mp)))

    def __find(self, i:int) -> int:
        """Find the root of the set containing element i with path compression."""
        if self._par[i] != i:
            self._par[i] = self.__find(self._par[i])
        return self._par[i]

    def get_set_id(self, item:TItem) -> Optional[int]:
        """Get the index of representative (root) of the set containing the item. Returns None if item not found."""
        if item not in self._mp:
            return None
        root = self.__find(self._mp[item])
        return root
    
    def in_same_set(self, item1:TItem, item2:TItem) -> bool:
        """Check if two items are in the same set."""
        if item1 not in self._mp or item2 not in self._mp:
            return False
        root1 = self.__find(self._mp[item1])
        root2 = self.__find(self._mp[item2])
        return root1 == root2
    
    def union(self, item1:TItem, item2:TItem):
        """Merge the sets containing item1 and item2."""
        if item1 not in self._mp or item2 not in self._mp:
            raise ValueError("Both items must be in the set.")
        root1 = self.__find(self._mp[item1])
        root2 = self.__find(self._mp[item2])
        if root1 != root2:
            self._par[root1] = root2


__all__ = ["UnionFindSet"]