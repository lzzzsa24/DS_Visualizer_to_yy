from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QMessageBox, QLabel, QGroupBox)
from src.view.canvas import DSCanvas
from src.model.stack import Stack
from src.model.exceptions import StructureFullError, StructureEmptyError

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. 初始化后端数据模型
        self.stack = Stack(capacity=8) # 容量设为8
        
        # 2. 初始化界面
        self.setWindowTitle("数据结构可视化系统 - Stack")
        self.resize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # === 左侧：画布区 ===
        self.canvas = DSCanvas(capacity=self.stack.capacity())
        layout.addWidget(self.canvas, stretch=3) # 占 3/4 宽度

        # === 右侧：控制面板 ===
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        layout.addWidget(control_panel, stretch=1) # 占 1/4 宽度

        # 输入框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请输入数字或字符...")
        control_layout.addWidget(QLabel("元素值:"))
        control_layout.addWidget(self.input_field)

        # 按钮组
        self.btn_push = QPushButton("入栈 (Push)")
        self.btn_pop = QPushButton("出栈 (Pop)")
        
        # 设置一点样式
        self.btn_push.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.btn_pop.setStyleSheet("background-color: #F44336; color: white; padding: 8px;")

        control_layout.addWidget(self.btn_push)
        control_layout.addWidget(self.btn_pop)
        control_layout.addStretch() # 弹簧，把控件顶上去

        # === 信号连接 ===
        # 当按钮被点击时，执行对应的函数
        self.btn_push.clicked.connect(self.on_push_click)
        self.btn_pop.clicked.connect(self.on_pop_click)

    def on_push_click(self):
        """处理入栈逻辑"""
        value = self.input_field.text().strip()
        if not value:
            QMessageBox.warning(self, "提示", "请输入内容！")
            return
        
        try:
            # 1. 修改后端数据
            self.stack.push(value)
            # 2. 刷新前端显示
            self.refresh_view()
            # 3. 清空输入框
            self.input_field.clear()
            self.input_field.setFocus()
        except StructureFullError:
            QMessageBox.critical(self, "错误", "栈满溢出 (Stack Overflow)！")

    def on_pop_click(self):
        """处理出栈逻辑"""
        try:
            # 1. 修改后端数据
            popped_val = self.stack.pop()
            # 2. 刷新前端显示
            self.refresh_view()
            QMessageBox.information(self, "成功", f"弹出了元素: {popped_val}")
        except StructureEmptyError:
            QMessageBox.critical(self, "错误", "栈空下溢 (Stack Underflow)！")

    def refresh_view(self):
        """同步数据"""
        # 从模型获取最新列表，交给画布去画
        items = self.stack.get_items()
        self.canvas.update_data(items)