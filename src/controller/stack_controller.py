from PyQt6.QtWidgets import QLineEdit, QLabel
from src.model.stack import Stack
from src.view.stack_canvas import StackCanvas
from src.model.exceptions import StructureFullError, StructureEmptyError




class StackController:
    def __init__(self, stack: Stack, canvas: StackCanvas,
                 input_field: QLineEdit, status_message: QLabel):
        self.stack = stack
        self.canvas = canvas
        self.stack_input_field = input_field
        self.stack_status_message = status_message
        # 初始化画布显示
        self.stack_refresh_view()


    def on_push_click(self):
        """处理入栈逻辑"""
        value = self.stack_input_field.text().strip()
        if not value:
            #QMessageBox.warning(self, "提示", "请输入内容！")
            # 提示用户输入为空
            self.stack_status_message.setText("请先输入数据！")
            self.stack_status_message.setStyleSheet("color: orange;")
            self.stack_input_field.setFocus()
            return
        
        try:
            # 1. 修改后端数据
            self.stack.push(value)
            # 2. 刷新前端显示
            self.stack_refresh_view()
            # 3. 清空输入框
            self.stack_input_field.clear()
            self.stack_input_field.setFocus()

            self.stack_status_message.setText(f"成功入栈元素: {value}")
            self.stack_status_message.setStyleSheet("color: green;")
        except StructureFullError:
            self.stack_status_message.setText("栈满溢出 (Stack Overflow)！")
            self.stack_status_message.setStyleSheet("color: red;")
            self.stack_input_field.clear()
            self.stack_input_field.setFocus()

    def on_pop_click(self):
        """处理出栈逻辑"""
        try:
            # 1. 修改后端数据
            popped_val = self.stack.pop()
            # 2. 刷新前端显示
            self.stack_refresh_view()
            self.stack_status_message.setText(f"成功出栈元素: {popped_val}")
            self.stack_status_message.setStyleSheet("color: green;")
            self.stack_input_field.setFocus()
        except StructureEmptyError:
            self.stack_status_message.setText("栈空下溢 (Stack Underflow)！")
            self.stack_status_message.setStyleSheet("color: red;")
            self.stack_input_field.setFocus()

    def stack_refresh_view(self):
        """刷新栈画布显示"""
        current_items = self.stack.get_items()
        self.canvas.update_data(current_items)