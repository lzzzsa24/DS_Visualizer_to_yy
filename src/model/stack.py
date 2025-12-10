from typing import Any, List
from src.model.exceptions import StructureEmptyError, StructureFullError

class Stack:
    """栈的实现类"""
    def __init__(self, capacity: int = 10):
        # 使用列表作为底层存储，_items 表示这是一个私有属性（封装）
        self._items: List[Any] = []
        self._capacity = capacity

    def push(self, item: Any) -> None:
        """入栈"""
        if self.is_full():
            raise StructureFullError("Stack is full")
        self._items.append(item)

    def pop(self) -> Any:
        """出栈"""
        if self.is_empty():
            raise StructureEmptyError("Stack is empty")
        return self._items.pop()

    def peek(self) -> Any:
        """查看栈顶元素"""
        if self.is_empty():
            raise StructureEmptyError("Stack is empty")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def is_full(self) -> bool:
        return len(self._items) >= self._capacity

    def size(self) -> int:
        return len(self._items)

    def get_items(self) -> List[Any]:
        """获取所有元素（用于前端绘图）"""
        return self._items.copy()  # 返回副本，防止外部直接修改
    
    def capacity(self) -> int:
        return self._capacity