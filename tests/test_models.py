import pytest
import sys
import os

# 路径设置 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.stack import Stack
from src.model.queue import Queue
from src.model.exceptions import StructureFullError, StructureEmptyError, StructureValueError

# 栈 (Stack) 的测试 

@pytest.fixture
def empty_stack():
    """创建一个容量为 3 的空栈供测试使用"""
    return Stack(capacity=3)

def test_stack_initialization(empty_stack):
    """测试栈初始化是否正确"""
    assert empty_stack.size() == 0
    assert empty_stack.is_empty() is True
    assert empty_stack.capacity() == 3 

def test_stack_push(empty_stack):
    """测试入栈逻辑"""
    empty_stack.push(10)
    assert empty_stack.size() == 1
    assert empty_stack.peek() == 10
    assert empty_stack.is_empty() is False

def test_stack_pop(empty_stack):
    """测试出栈逻辑"""
    empty_stack.push(10)
    empty_stack.push(20)
    
    item = empty_stack.pop()
    assert item == 20
    assert empty_stack.size() == 1
    
    item = empty_stack.pop()
    assert item == 10
    assert empty_stack.size() == 0

def test_stack_overflow(empty_stack):
    """测试栈满溢出异常"""
    # 填满 (3个)
    empty_stack.push(1)
    empty_stack.push(2)
    empty_stack.push(3)
    
    assert empty_stack.is_full() is True
    
    # 再推一个，应该报错 StructureFullError
    with pytest.raises(StructureFullError):
        empty_stack.push(4)

def test_stack_underflow(empty_stack):
    """测试空栈弹出异常"""
    with pytest.raises(StructureEmptyError):
        empty_stack.pop()

def test_stack_resize_success():
    """测试：正常的修改容量（变大或不变）"""
    s = Stack(capacity=5)
    for i in range(5):
        s.push(i)
    
    # 1. 扩容到 10
    s.set_capacity(10)
    assert s.capacity() == 10
    assert s.size() == 5 # 数据还在
    
    # 2. 缩容到 5 (刚好等于当前数量，允许)
    s.set_capacity(5)
    assert s.capacity() == 5
    assert s.size() == 5

def test_stack_resize_fail():
    """测试：非法的修改容量（试图让容量小于当前数量）"""
    s = Stack(capacity=5)
    for i in range(5):
        s.push(i) # 栈里有 0,1,2,3,4 (共5个)
    
    # 试图把容量设为 3，根据你的代码，应该抛出 StructureValueError
    with pytest.raises(StructureValueError):
        s.set_capacity(3)
        
    # 确保操作失败后，原来的容量和数据没变
    assert s.capacity() == 5
    assert s.size() == 5

#  队列 (Queue) 的测试 

@pytest.fixture
def empty_queue():
    return Queue(capacity=3)

def test_queue_order(empty_queue):
    empty_queue.enqueue("A")
    empty_queue.enqueue("B")
    
    assert empty_queue.dequeue() == "A"
    assert empty_queue.dequeue() == "B"

def test_queue_full_error(empty_queue):
    empty_queue.enqueue(1)
    empty_queue.enqueue(2)
    empty_queue.enqueue(3)
    
    with pytest.raises(StructureFullError):
        empty_queue.enqueue(4)