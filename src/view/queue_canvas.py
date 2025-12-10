from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt

class QueueCanvas(QWidget):
    def __init__(self, parent=None, capacity=10):
        super().__init__(parent)
        self.data_items = []
        self.capacity = capacity
        # 背景色
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(255, 250, 240)) # 浅米色背景
        self.setPalette(p)

    def update_data(self, items: list):
        self.data_items = items
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # === 1. 参数设置 ===
        box_width = 60  # 队列方块通常画小一点，防止太长
        box_height = 60
        spacing = 0
        
        # 计算整个队列通道的总长度
        total_width = self.capacity * (box_width + spacing)
        
        # 居中计算：起点的 X 坐标
        start_x = (self.width() - total_width) // 2
        # 垂直居中：Y 坐标固定
        base_y = (self.height() - box_height) // 2

        # === 2. 画上下两条轨道 (平行线) ===
        painter.setPen(QPen(Qt.GlobalColor.gray, 3))
        # 上轨道
        painter.drawLine(start_x -1, base_y - 2, 
                         start_x + total_width +1, base_y - 2)
        # 下轨道
        painter.drawLine(start_x -1, base_y + box_height + 2, 
                         start_x + total_width +1, base_y + box_height + 2)
        
        # 画“队头”和“队尾”的文字标记
        painter.setFont(QFont("Arial", 10))
        painter.drawText(start_x , base_y -20, "队头\n(Head)")
        painter.drawText(start_x + total_width - 40, base_y -20, "队尾\n(Tail)")

        # === 3. 画虚线空位 (占位符) ===
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(self.capacity):
            # 公式：x 随着 i 变大，向右移动
            slot_x = start_x + i * (box_width + spacing)
            painter.drawRect(slot_x, base_y, box_width, box_height)

        # === 4. 画真实数据 ===
        # 颜色换成绿色系，代表 Queue
        painter.setBrush(QBrush(QColor(144, 238, 144))) # 浅绿色
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        for i, item in enumerate(self.data_items):
            # 同样是从左往右画
            x = start_x + i * (box_width + spacing)
            
            painter.drawRect(x, base_y, box_width, box_height)
            painter.drawText(x, base_y, box_width, box_height, 
                           Qt.AlignmentFlag.AlignCenter, str(item))

        # === 紧挨队列下方居中显示容量 ===
        painter.setPen(QPen(Qt.GlobalColor.darkGray))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(self.width() // 2 - 50, base_y + box_height + 30, f"队列容量: {self.capacity} \n当前数量: {len(self.data_items)}")
        
        
        