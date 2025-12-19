from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
                             QLabel,QGraphicsTextItem, QPushButton, QHBoxLayout,QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QSize
from PyQt6.QtGui import QBrush, QColor, QKeyEvent, QFont, QPen

class GameView(QWidget):
    # 定义信号
    key_pressed_signal = pyqtSignal(int) 

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.setStyleSheet("background-color: #202020;")

        #  游戏画布
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background-color: #202020;border: none;")
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.view)

        # 复活覆盖层
        self.game_over_overlay = GameOverOverlay(self)

        
        self.cell_size = 40 # 像素大小

        #HUD:左上角背包显示
        self.backpack_capacity = 3
        self.backpack_scene = QGraphicsScene()
        self.backpack_view = QGraphicsView(self.backpack_scene, self.view)
        #背包位置和样式
        self.backpack_view.scale(0.8,0.8) #缩放比例
        self.backpack_view.move(0,0)
        self.backpack_view.setStyleSheet("background: transparent; border: none;")
        self.backpack_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.backpack_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.backpack_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        #初始化背包大小
        self.backpack_dimensions()

        #HUD:中间上方提示栏
        self.info_label = QLabel(self.view)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: rgba(44, 62, 80, 200); /* 深蓝色半透明背景 */
                color: #ecf0f1; /* 亮白色文字 */
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                padding: 5px 20px;
                font-family: "SimHei";
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #34495e;
                border-top: none;
            }
        """)
        self.info_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.info_label.setText("欢迎来到栈之传说 - 按 WASD 移动")
        self.info_label.adjustSize()
        # 初始居中
        self.info_label.move((self.view.width() - self.info_label.width()) // 2,0)

    def backpack_dimensions(self):
        """根据背包容量调整背包 HUD 的尺寸"""
        self.slot_width = 50
        self.slot_height=50
        self.backpack_height = self.backpack_capacity * 50 + 40 # 每个物品40px，高度加点边距
        self.backpack_width= self.slot_width + 40
        self.backpack_view.setFixedSize(self.backpack_width, self.backpack_height)
        
        
    def update_backpack(self, items,capacity=None):
        """绘制悬浮背包"""
        self.backpack_scene.clear()
        self.backpack_capacity = capacity if capacity is not None else self.backpack_capacity
        self.backpack_dimensions()
        
        capacity = self.backpack_capacity
        slot_w = self.slot_width
        slot_h = self.slot_height
        
        start_x = 10
        start_y = 60
        
        # 绘制标题
        title = QGraphicsTextItem("🎒背包")
        title.setFont(QFont("SimHei", 16, QFont.Weight.Bold))
        title.setDefaultTextColor(QColor("white"))
        # 居中标题
        t_rect = title.boundingRect()
        title.setPos(start_x + (slot_w - t_rect.width())/2, 10) # y=10
        self.backpack_scene.addItem(title)

        # 1. 绘制空槽位
        pen = QPen(QColor("#95a5a6"))
        pen.setWidth(3)
        brush = QBrush(QColor(0, 0, 0, 150)) 

        for i in range(capacity):
            y = start_y + i * slot_h
            self.backpack_scene.addRect(start_x, y, slot_w, slot_h, pen, brush)

        # 2. 绘制物品
        item_style = {
            3: ("水", "#2ecc71"), 
            4: ("剑", "#3498db"), 
            5: ("匙", "#f1c40f") 
        }
        font = QFont("SimHei", 24)
        font.setBold(True)

        for i, item_id in enumerate(items):
            if i >= capacity: break
            
            # 栈底在最下面 (row_index 最大)
            row_index = capacity - 1 - i
            current_y = start_y + row_index * slot_h
            
            if item_id in item_style:
                char, color = item_style[item_id]
                text_item = QGraphicsTextItem(char)
                text_item.setFont(font)
                text_item.setDefaultTextColor(QColor(color))
                self.backpack_scene.addItem(text_item)
                
                rect = text_item.boundingRect()
                text_x = start_x + (slot_w - rect.width()) / 2
                text_y = current_y + (slot_h - rect.height()) / 2
                text_item.setPos(text_x, text_y)

            
    def render(self, grid, player_pos, msg):
        """根据传入的数据渲染画面"""
        self.scene.clear()

        # 更新信息栏
        self.info_label.setText(msg)
        self.info_label.adjustSize()
        # 动态计算居中位置：(View总宽 - 文字标签宽) / 2
        center_x = (self.view.width() - self.info_label.width()) // 2
        self.info_label.move(center_x, 0) # y=0 紧贴顶部
        
        # 1. 设置背景色 
        self.scene.setBackgroundBrush(QBrush(QColor("#202020")))

        # 2. 定义【字典】：将数字 ID 映射为 (汉字, 颜色)
        skin_map = {
            0: ("·", "#404040"),  # 空地 (用点表示，更有网格感)
            1: ("墙", "#7f8c8d"),  # 墙壁 - 灰色
            2: ("我", "#e74c3c"),  # 玩家 - 红色
            3: ("水", "#2ecc71"),  # 水 - 绿色
            4: ("剑", "#3498db"),  # 宝剑 - 蓝色
            5: ("匙", "#f1c40f"),  # 钥匙 - 金色
            6: ("火", "#e67e22"),  # 火焰 - 橙色
            7: ("怪", "#9b59b6"),  # 怪物 - 紫色
            8: ("门", "#ecf0f1")   # 大门 - 白色
        }

        # 3. 设置字体 
        font = QFont("SimHei", int(self.cell_size * 0.6))
        font.setBold(True)

        # 4. 遍历地图并绘制
        for y, row in enumerate(grid):
            for x, val in enumerate(row):
                if val == -1:
                    continue  # 跳过虚空区域
                
                # 获取该位置的皮肤，如果没有定义就跳过
                if val in skin_map:
                    char, color_code = skin_map[val]
                    
                    # 创建文字项
                    text_item = QGraphicsTextItem(char)
                    text_item.setFont(font)
                    text_item.setDefaultTextColor(QColor(color_code))
                    
                    # 居中校准
                    # 计算偏移量让文字显示在格子正中间
                    # x_pos = 格子左边缘 + (格子宽 - 文字宽) / 2

                    # 先把 item 加进去才能获取宽度
                    self.scene.addItem(text_item) 
                    
                    # 获取文字的实际包围盒
                    rect = text_item.boundingRect()
                    text_width = rect.width()
                    text_height = rect.height()
                    
                    # 计算居中位置
                    center_x = (x * self.cell_size) + (self.cell_size - text_width) / 2
                    center_y = (y * self.cell_size) + (self.cell_size - text_height) / 2
                    
                    text_item.setPos(center_x, center_y)

        # 5. 单独绘制玩家 (覆盖在地图层之上)
        px, py = player_pos
        char, color_code = skin_map[2] # 获取“我”的皮肤
        
        player_item = QGraphicsTextItem(char)
        player_item.setFont(font)
        player_item.setDefaultTextColor(QColor(color_code))
        
        self.scene.addItem(player_item)
        
        # 同样的居中计算
        rect = player_item.boundingRect()
        player_item.setPos(
            (px * self.cell_size) + (self.cell_size - rect.width()) / 2,
            (py * self.cell_size) + (self.cell_size - rect.height()) / 2
        )

        #地图尺寸
        map_height_rows = len(grid)
        map_width_cols = len(grid[0]) if map_height_rows > 0 else 0
        map_pixel_width = map_width_cols * self.cell_size
        map_pixel_height = map_height_rows * self.cell_size
        #设定场景边界
        self.scene.setSceneRect(0, 0, map_pixel_width, map_pixel_height)
        #窗口尺寸
        view_w = self.view.viewport().width()
        view_h = self.view.viewport().height()

        if map_pixel_width > view_w or map_pixel_height > view_h:
            # 地图很大，开启跟随模式
            self.view.centerOn(player_item)
        else:
            # 地图较小，居中显示
            pass

    def keyPressEvent(self, event: QKeyEvent):
        """捕获键盘，直接转发给 Controller"""
        self.key_pressed_signal.emit(event.key())

    def show_game_over(self):
        """显示复活界面"""
        # 确保它覆盖整个视图区域
        self.game_over_overlay.resize(self.size())
        self.game_over_overlay.show()
        # 确保它在最上层
        self.game_over_overlay.raise_()

    def hide_game_over(self):
        """隐藏复活界面"""
        self.game_over_overlay.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        center_x = (self.view.width() - self.info_label.width()) // 2
        self.info_label.move(center_x, 0) 
        if hasattr(self, 'game_over_overlay'):
            self.game_over_overlay.resize(self.size())


            
#复活界面类
class GameOverOverlay(QFrame):
    # 定义两个信号，告诉 Controller 用户点了什么
    retry_signal = pyqtSignal()
    quit_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 半透明白色背景
        self.setStyleSheet("background-color: rgba(255,255,255, 120);")
        
        # 主布局（垂直居中）
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(80)

        # 1. 大标题 "YOU DIED"
        title_label = QLabel(" YOU DIED ")
        title_label.setStyleSheet("""
            background-color: transparent;
            color: #e74c3c;
            font-family: "SimHei";
            font-size: 128px;
            font-weight: bold;
            margin-bottom: 30px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 2. 按钮容器（水平布局）
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # 1. 复活按钮 (红色线框)
        retry_style = """
            QPushButton {
                background-color: #f8d7da;   /*浅红色背景*/
                color: #e74c3c;              /* 与标题同色 */
                font-family: "SimHei"; font-size: 20px; font-weight: 900;
                padding: 10px 30px; 
                border-radius: 20px;         /* 大圆角，胶囊型 */
                border: 3px solid #e74c3c;   /* 粗边框 */
            }
            QPushButton:hover { 
                background-color: #e74c3c;   /* 悬停填满红色 */
                color: white;                /* 文字变白 */
            }
        """

        # 2. 退出按钮 (灰色线框)
        quit_style = """
            QPushButton {
                background-color: #ecf0f1; /* 浅灰色背景 */
                color: #7f8c8d;
                font-family: "SimHei"; font-size: 20px; font-weight: 900;
                padding: 10px 30px; 
                border-radius: 20px;
                border: 3px solid #7f8c8d;
            }
            QPushButton:hover { 
                background-color: #7f8c8d;
                color: white;
            }
        """
        
        # 复活按钮
        self.btn_retry = QPushButton("复活 (Retry)")
        self.btn_retry.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_retry.setStyleSheet(retry_style)
        # 连接信号
        self.btn_retry.clicked.connect(self.retry_signal.emit)

        # 退出按钮
        self.btn_quit = QPushButton("退出 (Quit)")
        self.btn_quit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quit.setStyleSheet(quit_style)
        # 连接信号
        self.btn_quit.clicked.connect(self.quit_signal.emit)
        
        button_layout.addWidget(self.btn_retry)
        button_layout.addWidget(self.btn_quit)

        main_layout.addWidget(title_label)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        # 默认隐藏
        self.hide()