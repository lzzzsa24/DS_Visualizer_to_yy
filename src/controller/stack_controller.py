from PyQt6.QtWidgets import QLineEdit, QLabel, QMessageBox
from src.model.stack import Stack
from src.view.stack_canvas import StackCanvas
from src.model.exceptions import StructureFullError, StructureEmptyError, StructureValueError
from src.utils import get_base_path

import os
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect




class StackController:
    def __init__(self, stack: Stack, canvas: StackCanvas,
                 input_field: QLineEdit, status_message: QLabel, capacity_input: QLineEdit):
        self.stack = stack
        self.canvas = canvas
        self.stack_input_field = input_field
        self.stack_status_message = status_message
        self.stack_capacity_input = capacity_input

        # 初始化音效
        self.push_sound = QSoundEffect()
        self.pop_sound = QSoundEffect()
        self.error_sound = QSoundEffect()
        self.done_sound = QSoundEffect()

        project_root = get_base_path() # 根目录
        sounds_dir = os.path.join(project_root, 'resources', 'sounds')

        push_sound_path = os.path.join(sounds_dir, 'add_element_successfully.wav')
        pop_sound_path = os.path.join(sounds_dir, 'remove_element_successfully.wav')
        error_sound_path = os.path.join(sounds_dir, 'error.wav')
        done_sound_path = os.path.join(sounds_dir, 'done.wav')
        self.push_sound.setSource(QUrl.fromLocalFile(push_sound_path))
        self.pop_sound.setSource(QUrl.fromLocalFile(pop_sound_path))
        self.error_sound.setSource(QUrl.fromLocalFile(error_sound_path))
        self.done_sound.setSource(QUrl.fromLocalFile(done_sound_path))
        self.push_sound.setVolume(0.5)  # 设置音量
        self.pop_sound.setVolume(4.0)
        self.error_sound.setVolume(0.3)
        self.done_sound.setVolume(0.5)


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
            self.error_sound.play()
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
            # 播放入栈成功音效
            self.push_sound.play()
        except StructureFullError:
            self.stack_status_message.setText("栈满溢出 (Stack Overflow)！")
            self.stack_status_message.setStyleSheet("color: red;")
            self.stack_input_field.clear()
            self.stack_input_field.setFocus()
            self.error_sound.play()

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
            # 播放出栈成功音效
            self.pop_sound.play()
        except StructureEmptyError:
            self.stack_status_message.setText("栈空下溢 (Stack Underflow)！")
            self.stack_status_message.setStyleSheet("color: red;")
            self.stack_input_field.setFocus()
            self.error_sound.play()

    def on_set_capacity_click(self):
        """处理修改栈容量逻辑"""
        new_capacity_str = self.stack_capacity_input.text().strip()
        if not new_capacity_str.isdigit():
            self.stack_status_message.setText("请输入有效的容量数字！")
            self.stack_capacity_input.clear()
            self.stack_status_message.setStyleSheet("color: orange;")
            self.stack_capacity_input.setFocus()
            self.error_sound.play()
            return
        
        new_capacity = int(new_capacity_str)
        try:
            self.stack.set_capacity(new_capacity)
            self.canvas.set_capacity(new_capacity)
            self.stack_refresh_view()
            self.stack_status_message.setText(f"栈容量已设置为: {new_capacity}")
            self.stack_status_message.setStyleSheet("color: green;")
            self.stack_capacity_input.clear()
            self.stack_capacity_input.setFocus()
            self.done_sound.play()
        except StructureValueError as e:
            self.stack_status_message.setText(str(e))
            self.stack_status_message.setStyleSheet("color: red;")
            self.stack_capacity_input.setFocus()
            self.error_sound.play()

    def on_increase_capacity_click(self):
        """处理增加栈容量逻辑"""
        current_capacity = self.stack.capacity()
        new_capacity = current_capacity + 1
        self.stack.set_capacity(new_capacity)
        self.canvas.set_capacity(new_capacity)
        self.stack_refresh_view()
        self.stack_status_message.setText(f"栈容量已增加到: {new_capacity}")
        self.stack_status_message.setStyleSheet("color: green;")
        self.done_sound.play()

    def on_decrease_capacity_click(self):
        """处理减少栈容量逻辑"""
        current_capacity = self.stack.capacity()
        if current_capacity <= 1:
            self.stack_status_message.setText("栈容量不能小于 1！")
            self.stack_status_message.setStyleSheet("color: red;")
            self.error_sound.play()
            return
        
        new_capacity = current_capacity - 1
        try:
            self.stack.set_capacity(new_capacity)
            self.canvas.set_capacity(new_capacity)
            self.stack_refresh_view()
            self.stack_status_message.setText(f"栈容量已减少到: {new_capacity}")
            self.stack_status_message.setStyleSheet("color: green;")
            self.done_sound.play()
        except StructureValueError as e:
            self.stack_status_message.setText(str(e))
            self.stack_status_message.setStyleSheet("color: red;")
            self.error_sound.play()

    def stack_refresh_view(self):
        """刷新栈画布显示"""
        current_items = self.stack.get_items()
        self.canvas.update_data(current_items)