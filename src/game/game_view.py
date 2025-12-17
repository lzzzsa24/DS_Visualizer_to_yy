from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QLabel,QGraphicsTextItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QKeyEvent, QFont

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
        self.layout.addWidget(self.view)

        
        self.cell_size = 40 # 像素大小

        #HUD:左上角背包显示
        self.backpack_label = QLabel(self.view)
        self.backpack_label.move(10, 10)  # 设置位置在左上角
        self.backpack_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 160);
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-family: "SimHei";
                font-size: 14px;
                border: 1px solid #444;
            }
        """)
        self.backpack_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.backpack_label.hide()

        #HUD:右下角提示栏
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
        
    def update_backpack(self, items):
        """更新左上角背包 HUD"""
        if not items:
            self.backpack_label.setText("🎒 背包 (空)")
            self.backpack_label.adjustSize()
            self.backpack_label.show()
            return

        item_style = {
            3: ("药", "#2ecc71"), 
            4: ("剑", "#3498db"), 
            5: ("匙", "#f1c40f") 
        }

        html = "<div>🎒 <b>我的背包</b></div><hr style='background-color:#555; height:1px; border:none;'>"
        for item_id in reversed(items):
            if item_id in item_style:
                name, color = item_style[item_id]
                html += f"<div style='color:{color}; margin-top:2px;'>█ {name}</div>"
            else:
                html += "<div>? 未知</div>"
        
        self.backpack_label.setText(html)
        self.backpack_label.adjustSize()
        self.backpack_label.show()

            
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
            3: ("药", "#2ecc71"),  # 药水 - 绿色
            4: ("剑", "#3498db"),  # 宝剑 - 蓝色
            5: ("匙", "#f1c40f"),  # 钥匙 - 金色
            6: ("火", "#e67e22"),  # 火焰 - 橙色
            7: ("怪", "#9b59b6"),  # 怪物 - 紫色
            8: ("门", "#ecf0f1")   # 大门 - 白色
        }

        # 3. 设置字体 (使用黑体 SimHei 或 微软雅黑，加粗)
        # 字体大小设为格子大小的 80% 左右
        font = QFont("SimHei", int(self.cell_size * 0.6))
        font.setBold(True)

        # 4. 遍历地图并绘制
        for y, row in enumerate(grid):
            for x, val in enumerate(row):
                
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

    def keyPressEvent(self, event: QKeyEvent):
        """捕获键盘，直接转发给 Controller"""
        self.key_pressed_signal.emit(event.key())