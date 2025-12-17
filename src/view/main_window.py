from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QPushButton, QLineEdit, QMessageBox, QLabel, QGroupBox)
from PyQt6.QtCore import Qt
from src.view.stack_canvas import StackCanvas

from src.model.stack import Stack
from src.model.exceptions import StructureFullError, StructureEmptyError

from src.model.queue import Queue             
from src.view.queue_canvas import QueueCanvas 

from src.controller.stack_controller import StackController
from src.controller.queue_controller import QueueController

from src.game.game_view import GameView       
from src.game.game_controller import GameController 


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
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 0;
            }
        """)
        self.setCentralWidget(self.tabs)

        #创建stack标签页
        self.stack_widget = self.create_stack_page()
        self.tabs.addTab(self.stack_widget, "栈 (Stack)")
        #创建queue标签页
        self.queue_widget = self.create_queue_page()
        self.tabs.addTab(self.queue_widget, "队列 (Queue)")
        #创建game标签页
        self.game_widget = self.create_game_page()
        self.tabs.addTab(self.game_widget, "栈之传说 (Legends of Stack)")
        self.game_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # 允许接收键盘焦点
        
        
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

        # 容量调整输入框和按钮
        self.stack_capacity_input = QLineEdit()
        self.stack_capacity_input.setPlaceholderText("请输入新的容量...")
        control_layout.addWidget(QLabel("调整容量:"))
        control_layout.addWidget(self.stack_capacity_input)
        self.btn_set_capacity = QPushButton("设置容量")
        control_layout.addWidget(self.btn_set_capacity)
        #容量加减号按钮
        self.btn_increase_capacity = QPushButton("+")
        self.btn_decrease_capacity = QPushButton("-")
        control_capacity_addandsubtract_layout = QHBoxLayout()
        control_capacity_addandsubtract_layout.addWidget(self.btn_increase_capacity)
        control_capacity_addandsubtract_layout.addWidget(self.btn_decrease_capacity)
        control_layout.addLayout(control_capacity_addandsubtract_layout)
        #设置容量按钮颜色
        self.btn_set_capacity.setStyleSheet("background-color: #008CBA; color: white; padding: 8px;")
        self.btn_increase_capacity.setStyleSheet("background-color: #10B981; color: white; padding: 3px;font-weight: bold;font-size: 20px;")
        self.btn_decrease_capacity.setStyleSheet("background-color: #EF4444; color: white; padding: 3px;font-weight: bold;font-size: 20px;")

        # 状态显示标签
        self.stack_status_message = QLabel("准备就绪")
        # 设置样式：居中，稍微留点上下边距
        self.stack_status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack_status_message.setStyleSheet("color: gray; font-size: 14px; margin-top: 10px;")
        control_layout.addWidget(self.stack_status_message)
    

        control_layout.addStretch() # 弹簧，把控件顶上去

        # === 信号连接 ===
        self.stack_controller = StackController(self.stack, self.canvas,
                                                self.stack_input_field, self.stack_status_message, self.stack_capacity_input)
        self.btn_push.clicked.connect(self.stack_controller.on_push_click)
        self.btn_pop.clicked.connect(self.stack_controller.on_pop_click)
        self.btn_set_capacity.clicked.connect(self.stack_controller.on_set_capacity_click)
        self.btn_increase_capacity.clicked.connect(self.stack_controller.on_increase_capacity_click)
        self.btn_decrease_capacity.clicked.connect(self.stack_controller.on_decrease_capacity_click)

        return page

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

        # 容量调整输入框和按钮
        self.queue_capacity_input = QLineEdit()
        self.queue_capacity_input.setPlaceholderText("请输入新的容量...")
        control_layout.addWidget(QLabel("调整容量:"))
        control_layout.addWidget(self.queue_capacity_input)
        self.btn_set_capacity = QPushButton("设置容量")
        control_layout.addWidget(self.btn_set_capacity)
        #容量加减号按钮
        self.btn_increase_capacity = QPushButton("+")
        self.btn_decrease_capacity = QPushButton("-")
        control_capacity_addandsubtract_layout = QHBoxLayout()
        control_capacity_addandsubtract_layout.addWidget(self.btn_increase_capacity)
        control_capacity_addandsubtract_layout.addWidget(self.btn_decrease_capacity)
        control_layout.addLayout(control_capacity_addandsubtract_layout)
        # 设置容量按钮颜色
        self.btn_set_capacity.setStyleSheet("background-color: #008CBA; color: white; padding: 8px;")
        self.btn_increase_capacity.setStyleSheet("background-color: #10B981; color: white; padding: 3px;font-weight: bold;font-size: 20px;")
        self.btn_decrease_capacity.setStyleSheet("background-color: #EF4444; color: white; padding: 3px;font-weight: bold;font-size: 20px;")

        # 状态显示标签
        self.queue_status_message = QLabel("准备就绪")
        # 设置样式：居中，稍微留点上下边距
        self.queue_status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.queue_status_message.setStyleSheet("color: gray; font-size: 14px; margin-top: 10px;")
        control_layout.addWidget(self.queue_status_message)

        control_layout.addStretch() # 弹簧，把控件顶上去

        # === 信号连接 ===
        self.queue_controller = QueueController(self.queue, self.queue_canvas,self.queue_input_field, 
                                                self.queue_status_message, self.queue_capacity_input)
        self.btn_enqueue.clicked.connect(self.queue_controller.on_enqueue_click)
        self.btn_dequeue.clicked.connect(self.queue_controller.on_dequeue_click)
        self.btn_set_capacity.clicked.connect(self.queue_controller.on_set_capacity_click)
        self.btn_increase_capacity.clicked.connect(self.queue_controller.on_increase_capacity_click)
        self.btn_decrease_capacity.clicked.connect(self.queue_controller.on_decrease_capacity_click)


        return page
    
    def create_game_page(self):
        """创建游戏页面"""
       
        # 创建游戏视图
        view = GameView()
        # 创建游戏控制器
        self.game_controller = GameController(view)

        return view
    