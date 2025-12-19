from typing import Any, List, Optional
from src.model.exceptions import StructureEmptyError, StructureValueError

class Node:
    """链表节点"""
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional['Node'] = None

class LinkedList:
    """单向链表实现"""
    def __init__(self):
        self.head: Optional[Node] = None
        self._size = 0

    def append(self, data: Any) -> None:
        """在尾部添加 (Append)"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1

    def prepend(self, data: Any) -> None:
        """在头部添加 (Prepend)"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def insert_at(self, position: int, data: Any) -> None:
        """在指定位置插入节点 (0-based index)"""
        if position < 0:
            raise StructureValueError("位置不能为负数")
        
        if position > self._size:
            raise StructureValueError(f"位置超出范围 (0-{self._size})")
        
        # 在头部插入
        if position == 0:
            self.prepend(data)
            return
        
        # 在中间或尾部插入
        new_node = Node(data)
        current = self.head
        for i in range(position - 1):
            current = current.next
        
        new_node.next = current.next
        current.next = new_node
        self._size += 1

    def delete(self, value: Any) -> bool:
        """删除指定值的第一个节点"""
        if not self.head:
            raise StructureEmptyError("List is empty")

        # Case 1: 如果头节点就是要删的
        if str(self.head.data) == str(value):
            self.head = self.head.next
            self._size -= 1
            return True

        # Case 2: 遍历查找后续节点
        current = self.head
        while current.next:
            if str(current.next.data) == str(value):
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
        return False

    def delete_head(self) -> Any:
        """删除头节点并返回其值"""
        if not self.head:
            raise StructureEmptyError("链表为空，无法删除")
        
        data = self.head.data
        self.head = self.head.next
        self._size -= 1
        return data

    def delete_tail(self) -> Any:
        """删除尾节点并返回其值"""
        if not self.head:
            raise StructureEmptyError("链表为空，无法删除")
        
        # 只有一个节点的情况
        if not self.head.next:
            data = self.head.data
            self.head = None
            self._size -= 1
            return data
        
        # 多个节点：找到倒数第二个节点
        current = self.head
        while current.next.next:
            current = current.next
        
        data = current.next.data
        current.next = None
        self._size -= 1
        return data

    def delete_at(self, position: int) -> Any:
        """删除指定位置的节点并返回其值 (0-based index)"""
        if position < 0:
            raise StructureValueError("位置不能为负数")
        
        if position >= self._size:
            raise StructureValueError(f"位置超出范围 (0-{self._size - 1})")
        
        # 删除头节点
        if position == 0:
            return self.delete_head()
        
        # 删除中间或尾部节点
        current = self.head
        for i in range(position - 1):
            current = current.next
        
        data = current.next.data
        current.next = current.next.next
        self._size -= 1
        return data

    def get_items(self) -> List[Any]:
        """获取所有数据用于绘图 (转换成列表)"""
        items = []
        current = self.head
        while current:
            items.append(current.data)
            current = current.next
        return items

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def clear(self) -> None:
        self.head = None
        self._size = 0