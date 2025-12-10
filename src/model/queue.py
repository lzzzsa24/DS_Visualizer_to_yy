from typing import Any, List
from src.model.exceptions import StructureEmptyError, StructureFullError

class Queue:
    """队列的实现类"""
    def __init__(self, capacity: int = 10):
        self._items: List[Any] = []
        self._capacity = capacity

    def enqueue(self, item: Any) -> None:
        """入队"""
        if self.is_full():
            raise StructureFullError("Queue is full")
        self._items.append(item)

    def dequeue(self) -> Any:
        """出队"""
        if self.is_empty():
            raise StructureEmptyError("Queue is empty")
        return self._items.pop(0)  # 移除列表第一个元素

    def peek(self) -> Any:
        """查看队头元素"""
        if self.is_empty():
            raise StructureEmptyError("Queue is empty")
        return self._items[0]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def is_full(self) -> bool:
        return len(self._items) >= self._capacity

    def size(self) -> int:
        return len(self._items)

    def get_items(self) -> List[Any]:
        return self._items.copy()
    
    def capacity(self) -> int:
        return self._capacity