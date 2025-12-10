from PyQt6.QtWidgets import QLineEdit, QLabel
from src.model.queue import Queue
from src.view.queue_canvas import QueueCanvas
from src.model.exceptions import StructureFullError, StructureEmptyError

class QueueController:
    def __init__(self, queue: Queue, canvas: QueueCanvas,
                 input_field: QLineEdit, status_message: QLabel):
        self.queue = queue
        self.canvas = canvas
        self.input_field = input_field
        self.status_message = status_message
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

    def queue_refresh_view(self):
        """刷新队列画布显示"""
        current_items = self.queue.get_items()
        self.canvas.update_data(current_items)