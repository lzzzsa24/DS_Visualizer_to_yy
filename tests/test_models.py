import pytest
from src.model.stack import Stack
from src.model.queue import Queue
from src.model.exceptions import StructureEmptyError, StructureFullError

# === 测试栈 (Stack) ===
def test_stack_push_pop():
    s = Stack(capacity=3)
    s.push(1)
    s.push(2)
    assert s.size() == 2
    assert s.peek() == 2
    assert s.pop() == 2
    assert s.pop() == 1
    assert s.is_empty()

def test_stack_overflow():
    s = Stack(capacity=1)
    s.push(1)
    with pytest.raises(StructureFullError):
        s.push(2)

def test_stack_underflow():
    s = Stack()
    with pytest.raises(StructureEmptyError):
        s.pop()

# === 测试队列 (Queue) ===
def test_queue_order():
    q = Queue()
    q.enqueue("A")
    q.enqueue("B")
    assert q.dequeue() == "A"  # 先进先出
    assert q.dequeue() == "B"

def test_queue_empty():
    q = Queue()
    with pytest.raises(StructureEmptyError):
        q.dequeue()