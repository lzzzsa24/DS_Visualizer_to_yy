from PyQt6.QtWidgets import QLineEdit, QLabel
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect
from src.model.linked_list import LinkedList
from src.view.linked_list_canvas import LinkedListCanvas
from src.model.exceptions import StructureEmptyError, StructureValueError
from src.utils import get_base_path

import os

class LinkedListController:
    def __init__(self, linked_list: LinkedList, canvas: LinkedListCanvas,
                 input_field: QLineEdit, status_message: QLabel, position_input: QLineEdit = None):
        self.linked_list = linked_list
        self.canvas = canvas
        self.input_field = input_field
        self.status_message = status_message
        self.position_input = position_input

        # 初始化音效 (复用 Stack/Queue 的音效文件)
        self.add_sound = QSoundEffect()
        self.remove_sound = QSoundEffect()
        self.error_sound = QSoundEffect()
        self.done_sound = QSoundEffect()

        project_root = get_base_path()
        sounds_dir = os.path.join(project_root, 'resources', 'sounds')

        self.add_sound.setSource(QUrl.fromLocalFile(os.path.join(sounds_dir, 'add_element_successfully.wav')))
        self.remove_sound.setSource(QUrl.fromLocalFile(os.path.join(sounds_dir, 'remove_element_successfully.wav')))
        self.error_sound.setSource(QUrl.fromLocalFile(os.path.join(sounds_dir, 'error.wav')))
        self.done_sound.setSource(QUrl.fromLocalFile(os.path.join(sounds_dir, 'done.wav')))
        
        # 音量设置
        self.add_sound.setVolume(0.5)
        self.remove_sound.setVolume(4.0)
        self.error_sound.setVolume(0.3)
        self.done_sound.setVolume(0.5)

        self.refresh_view()

    def on_append_click(self):
        """尾插"""
        value = self.input_field.text().strip()
        if not value:
            self._show_error("请先输入数据！")
            return
        
        old_size = self.linked_list.size()
        self.linked_list.append(value)
        self.refresh_view()
        # 触发尾部插入滑动动画
        self.canvas.animate_insert_slide(old_size)
        self._on_success(f"尾部添加: {value}", self.add_sound)

    def on_prepend_click(self):
        """头插"""
        value = self.input_field.text().strip()
        if not value:
            self._show_error("请先输入数据！")
            return
        
        self.linked_list.prepend(value)
        self.refresh_view()
        # 触发头部插入滑动动画
        self.canvas.animate_insert_slide(0)
        self._on_success(f"头部添加: {value}", self.add_sound)

    def on_delete_click(self):
        """按值删除"""
        value = self.input_field.text().strip()
        if not value:
            self._show_error("请输入要删除的值！")
            return

        try:
            items = self.linked_list.get_items()
            delete_index = -1
            for i, item in enumerate(items):
                if str(item) == str(value):
                    delete_index = i
                    break

            if delete_index >= 0:
                self._execute_delete(value, delete_index)
            else:
                self.status_message.setText(f"未找到元素: {value}")
                self.status_message.setStyleSheet("color: orange;")
                self.error_sound.play()
                self.input_field.setFocus()
        except StructureEmptyError:
            self._show_error("链表为空！")
    
    def _execute_delete(self, value, index):
        """执行删除操作"""
        success = self.linked_list.delete(value)
        if success:
            self.refresh_view()
            # 删除几何动画
            self.canvas.animate_delete(index, value)
            self._on_success(f"成功删除: {value}", self.remove_sound)

    def on_insert_at_click(self):
        """在指定位置插入"""
        value = self.input_field.text().strip()
        if not value:
            self._show_error("请输入要插入的值！")
            return
        
        if not self.position_input:
            self._show_error("位置输入框未初始化！")
            return
        
        position_text = self.position_input.text().strip()
        if not position_text:
            self._show_error("请输入插入位置！")
            return
        
        try:
            position = int(position_text)
            self.linked_list.insert_at(position, value)
            self.refresh_view()
            # 触发插入滑动动画
            self.canvas.animate_insert_slide(position)
            self._on_success(f"在位置 {position} 插入: {value}", self.add_sound)
            if self.position_input:
                self.position_input.clear()
        except ValueError:
            self._show_error("位置必须是数字！")
        except StructureValueError as e:
            self._show_error(str(e))

    def on_delete_head_click(self):
        """头部删除"""
        try:
            deleted_value = self.linked_list.delete_head()
            self.refresh_view()
            # 头部删除几何动画
            self.canvas.animate_delete(0, deleted_value)
            self._on_success(f"头部删除: {deleted_value}", self.remove_sound)
        except StructureEmptyError:
            self._show_error("链表为空！")

    def on_delete_tail_click(self):
        """尾部删除"""
        try:
            tail_index = max(0, self.linked_list.size() - 1)
            deleted_value = self.linked_list.delete_tail()
            self.refresh_view()
            # 尾部删除几何动画
            self.canvas.animate_delete(tail_index, deleted_value)
            self._on_success(f"尾部删除: {deleted_value}", self.remove_sound)
        except StructureEmptyError:
            self._show_error("链表为空！")

    def on_delete_at_click(self):
        """指定位置删除"""
        if not self.position_input:
            self._show_error("位置输入框未初始化！")
            return
        
        position_text = self.position_input.text().strip()
        if not position_text:
            self._show_error("请输入要删除的位置！")
            return
        
        try:
            position = int(position_text)
            self._execute_delete_at(position)
            if self.position_input:
                self.position_input.clear()
        except ValueError:
            self._show_error("位置必须是数字！")
    
    def _execute_delete_at(self, position):
        """执行指定位置删除"""
        try:
            deleted_value = self.linked_list.delete_at(position)
            self.refresh_view()
            # 指定位置删除几何动画
            self.canvas.animate_delete(position, deleted_value)
            self.status_message.setText(f"位置 {position} 删除: {deleted_value}")
            self.status_message.setStyleSheet("color: green;")
            self.remove_sound.play()
            self.position_input.setFocus()
        except (StructureValueError, StructureEmptyError) as e:
            self._show_error(str(e))

    def refresh_view(self):
        self.canvas.update_data(self.linked_list.get_items())

    # 辅助方法：减少重复代码
    def _show_error(self, msg):
        self.status_message.setText(msg)
        self.status_message.setStyleSheet("color: red;")
        self.error_sound.play()
        self.input_field.setFocus()

    def _on_success(self, msg, sound):
        self.refresh_view()
        self.input_field.clear()
        self.input_field.setFocus()
        self.status_message.setText(msg)
        self.status_message.setStyleSheet("color: green;")
        sound.play()