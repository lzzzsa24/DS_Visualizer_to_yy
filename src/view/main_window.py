from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QPushButton, QLineEdit, QMessageBox, QLabel, QGroupBox)
from PyQt6.QtCore import Qt
from src.view.stack_canvas import StackCanvas
from src.model.stack import Stack
from src.model.exceptions import StructureFullError, StructureEmptyError

from src.model.queue import Queue             
from src.view.queue_canvas import QueueCanvas 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化 Stack 后端
        self.stack = Stack(capacity=8) # 容量设为8
        # 初始化 Queue 后端
        self.queue = Queue(capacity=10) # 容量设为10
        
        # 初始化界面
        self.setWindowTitle("数据结构可视化系统")
        self.resize(1000, 700)
        self.setup_ui()

    def setup_ui(self):
        # 主容器
        self.tabs=QTabWidget()
        self.setCentralWidget(self.tabs)

        #创建stack标签页
        self.stack_widget = self.create_stack_page()
        self.tabs.addTab(self.stack_widget, "栈 (Stack)")
        #创建queue标签页
        self.queue_widget = self.create_queue_page()
        self.tabs.addTab(self.queue_widget, "队列 (Queue)")

        
    def create_stack_page(self):
        """创建栈操作页面"""
        page = QWidget()
        main_layout = QHBoxLayout(page)
        
        # 左侧画布区域
        self.canvas = StackCanvas(capacity=self.stack.capacity())
        main_layout.addWidget(self.canvas, stretch=3) # 占 3/4 宽度

        # 右侧控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel, stretch=1) # 占 1/4 宽度
        # 输入框
        self.stack_input_field = QLineEdit()
        self.stack_input_field.setPlaceholderText("请输入数字或字符...")
        control_layout.addWidget(QLabel("元素值:"))
        control_layout.addWidget(self.stack_input_field)

        # 按钮组
        self.btn_push = QPushButton("入栈 (Push)")
        self.btn_pop = QPushButton("出栈 (Pop)")
        
        # 设置样式
        self.btn_push.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.btn_pop.setStyleSheet("background-color: #F44336; color: white; padding: 8px;")

        control_layout.addWidget(self.btn_push)
        control_layout.addWidget(self.btn_pop)

        # 状态显示标签
        self.stack_status_message = QLabel("准备就绪")
        # 设置样式：居中，稍微留点上下边距
        self.stack_status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack_status_message.setStyleSheet("color: gray; font-size: 14px; margin-top: 10px;")
        control_layout.addWidget(self.stack_status_message)
    

        control_layout.addStretch() # 弹簧，把控件顶上去

        # === 信号连接 ===
        # 当按钮被点击时，执行对应的函数
        self.btn_push.clicked.connect(self.on_push_click)
        self.btn_pop.clicked.connect(self.on_pop_click)

        return page

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

    def create_queue_page(self):
        """创建队列操作页面"""
        page = QWidget()
        main_layout = QHBoxLayout(page)
        # 左侧画布区域
        self.queue_canvas = QueueCanvas(capacity=self.queue.capacity())
        main_layout.addWidget(self.queue_canvas, stretch=3) # 占 3/4 宽度

        # 右侧控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel, stretch=1) # 占 1/4

        self.queue_input_field = QLineEdit()
        self.queue_input_field.setPlaceholderText("请输入数字或字符...")

        control_layout.addWidget(QLabel("元素值:"))
        control_layout.addWidget(self.queue_input_field)

        # 按钮组
        self.btn_enqueue = QPushButton("入队 (Enqueue)")
        self.btn_dequeue = QPushButton("出队 (Dequeue)")
        # 设置样式
        self.btn_enqueue.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.btn_dequeue.setStyleSheet("background-color: #F44336; color: white; padding: 8px;")

        control_layout.addWidget(self.btn_enqueue)
        control_layout.addWidget(self.btn_dequeue)

        # 状态显示标签
        self.queue_status_message = QLabel("准备就绪")
        # 设置样式：居中，稍微留点上下边距
        self.queue_status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.queue_status_message.setStyleSheet("color: gray; font-size: 14px; margin-top: 10px;")
        control_layout.addWidget(self.queue_status_message)

        control_layout.addStretch() # 弹簧，把控件顶上去

        # === 信号连接 ===
        self.btn_enqueue.clicked.connect(self.on_enqueue_click)
        self.btn_dequeue.clicked.connect(self.on_dequeue_click)


        return page
    
    def on_enqueue_click(self):
        """处理入队逻辑"""
        value = self.queue_input_field.text().strip()
        if not value:
            self.queue_status_message.setText("请先输入数据！")
            self.queue_status_message.setStyleSheet("color: orange;")
            self.queue_input_field.setFocus()
            return
        
        try:
            self.queue.enqueue(value)
            self.refresh_queue_view()
            self.queue_input_field.clear()
            self.queue_input_field.setFocus()

            self.queue_status_message.setText(f"成功入队元素: {value}")
            self.queue_status_message.setStyleSheet("color: green;")
        except StructureFullError:
            self.queue_status_message.setText("队列满溢 (Queue Overflow)！")
            self.queue_status_message.setStyleSheet("color: red;")
            self.queue_input_field.clear()
            self.queue_input_field.setFocus()
    
    def on_dequeue_click(self):
        """处理出队逻辑"""
        try:
            dequeued_val = self.queue.dequeue()
            self.refresh_queue_view()
            self.queue_status_message.setText(f"成功出队元素: {dequeued_val}")
            self.queue_status_message.setStyleSheet("color: green;")
            self.queue_input_field.setFocus()
        except StructureEmptyError:
            self.queue_status_message.setText("队列空下溢 (Queue Underflow)！")
            self.queue_status_message.setStyleSheet("color: red;")
            self.queue_input_field.setFocus()

    def stack_refresh_view(self):
        """同步栈数据"""
        # 从模型获取最新列表，交给画布去画
        items = self.stack.get_items()
        self.canvas.update_data(items)

    def refresh_queue_view(self):
        """同步队列数据"""
        items = self.queue.get_items()
        self.queue_canvas.update_data(items)