from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt

class DSCanvas(QWidget):
    """数据结构专用画布：负责把数据画成方块"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_items = []  # 存放要画的数据
        
        # 设置白色背景
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(p)

    def update_data(self, items: list):
        """更新数据并触发重绘"""
        self.data_items = items
        self.update()  # 这一步会触发 paintEvent

    def paintEvent(self, event):
        """Qt 绘图核心函数，系统会自动调用"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # 抗锯齿

        # 定义方块参数
        box_width = 80
        box_height = 40
        start_x = 100
        # 从窗口底部往上画（模拟栈的物理堆叠）
        base_y = self.height() - 50 

        # 遍历数据画图
        for i, item in enumerate(self.data_items):
            # 计算坐标：栈底在下，新元素往上摞
            x = start_x
            y = base_y - (i * (box_height + 5)) # 5是间距

            # 1. 画方块背景
            painter.setBrush(QBrush(QColor(100, 149, 237)))  # 漂亮的矢车菊蓝
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawRect(x, y, box_width, box_height)

            # 2. 画文字
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(x, y, box_width, box_height, 
                           Qt.AlignmentFlag.AlignCenter, str(item))
            
        # 3. 画一个底座（容器的感觉）
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(Qt.GlobalColor.gray, 3))
        # 画个 U 型开口
        container_width = box_width + 20
        container_height = (len(self.data_items) + 1) * (box_height + 5)
        # 左竖线
        painter.drawLine(start_x - 10, base_y + box_height, 
                        start_x - 10, base_y - container_height)
        # 右竖线
        painter.drawLine(start_x + box_width + 10, base_y + box_height, 
                        start_x + box_width + 10, base_y - container_height)
        # 底横线
        painter.drawLine(start_x - 10, base_y + box_height, 
                        start_x + box_width + 10, base_y + box_height)