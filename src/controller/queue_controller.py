from PyQt6.QtWidgets import QLineEdit, QLabel
from src.model.queue import Queue
from src.view.queue_canvas import QueueCanvas
from src.model.exceptions import StructureFullError, StructureEmptyError, StructureValueError

class QueueController:
    def __init__(self, queue: Queue, canvas: QueueCanvas,
                 input_field: QLineEdit, status_message: QLabel, capacity_input: QLineEdit):
        self.queue = queue
        self.canvas = canvas
        self.input_field = input_field
        self.status_message = status_message
        self.queue_capacity_input = capacity_input
        # 初始化画布显示
        self.queue_refresh_view()


    def on_enqueue_click(self):
        """处理入队逻辑"""
        value = self.input_field.text().strip()
        if not value:
            # 提示用户输入为空
            self.status_message.setText("请先输入数据！")
            self.status_message.setStyleSheet("color: orange;")
            self.input_field.setFocus()
            return
        
        try:
            # 1. 修改后端数据
            self.queue.enqueue(value)
            # 2. 刷新前端显示
            self.queue_refresh_view()
            # 3. 清空输入框
            self.input_field.clear()
            self.input_field.setFocus()

            self.status_message.setText(f"成功入队元素: {value}")
            self.status_message.setStyleSheet("color: green;")
        except StructureFullError:
            self.status_message.setText("队列满溢 (Queue Overflow)！")
            self.status_message.setStyleSheet("color: red;")
            self.input_field.clear()
            self.input_field.setFocus()

    def on_dequeue_click(self):
        """处理出队逻辑"""
        try:
            # 1. 修改后端数据
            dequeued_val = self.queue.dequeue()
            # 2. 刷新前端显示
            self.queue_refresh_view()
            self.status_message.setText(f"成功出队元素: {dequeued_val}")
            self.status_message.setStyleSheet("color: green;")
            self.input_field.setFocus()
        except StructureEmptyError:
            self.status_message.setText("队列空下溢 (Queue Underflow)！")
            self.status_message.setStyleSheet("color: red;")

    def on_set_capacity_click(self):
        """处理修改队列容量逻辑"""
        new_capacity_str = self.queue_capacity_input.text().strip()
        if not new_capacity_str.isdigit():
            self.status_message.setText("请输入有效的容量数字！")
            self.status_message.setStyleSheet("color: orange;")
            self.queue_capacity_input.clear()
            self.queue_capacity_input.setFocus()
            return
        
        new_capacity = int(new_capacity_str)
        try:
            self.queue.set_capacity(new_capacity)
            self.canvas.set_capacity(new_capacity)
            self.queue_refresh_view()
            self.status_message.setText(f"队列容量已设置为: {new_capacity}")
            self.status_message.setStyleSheet("color: green;")
            self.queue_capacity_input.clear()
            self.queue_capacity_input.setFocus()
        except StructureValueError as e:
            self.status_message.setText(str(e))
            self.status_message.setStyleSheet("color: red;")
            self.queue_capacity_input.clear()
            self.queue_capacity_input.setFocus()
            

    def on_increase_capacity_click(self):
        """处理增加队列容量逻辑"""
        current_capacity = self.queue.capacity()
        new_capacity = current_capacity + 1
        self.queue.set_capacity(new_capacity)
        self.canvas.set_capacity(new_capacity)
        self.queue_refresh_view()
        self.status_message.setText(f"队列容量已增加到: {new_capacity}")
        self.status_message.setStyleSheet("color: green;")



    def on_decrease_capacity_click(self):
        """处理减少队列容量逻辑"""
        current_capacity = self.queue.capacity()
        if current_capacity <= 1:
            self.status_message.setText("队列容量不能小于 1！")
            self.status_message.setStyleSheet("color: red;")
            self.input_field.setFocus()
            return
        
        new_capacity = current_capacity - 1
        try:
            self.queue.set_capacity(new_capacity)
            self.canvas.set_capacity(new_capacity)
            self.queue_refresh_view()
            self.status_message.setText(f"队列容量已减少到: {new_capacity}")
            self.status_message.setStyleSheet("color: green;")
            self.input_field.setFocus()
        except StructureValueError as e:
            self.status_message.setText(str(e))
            self.status_message.setStyleSheet("color: red;")
            self.input_field.setFocus()

    def queue_refresh_view(self):
        """刷新队列画布显示"""
        current_items = self.queue.get_items()
        self.canvas.update_data(current_items)