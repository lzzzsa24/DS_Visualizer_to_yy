from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer

class LinkedListCanvas(QWidget):
    """单向链表专用画布"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_items = []
        # 设置背景为浅蓝色，与Stack/Queue相同
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(240, 248, 255)) 
        self.setPalette(p)
        
        # 动画相关属性
        self.highlight_index = -1  # 高亮的节点索引
        self.new_node_index = -1   # 新插入节点的索引
        self.delete_node_index = -1  # 删除节点的索引
        self.animation_alpha = 255  # 动画透明度 (0-255)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_step = 0

    def update_data(self, items: list):
        self.data_items = items
        self.update()
    
    def highlight_node(self, index: int):
        """高亮指定节点"""
        self.highlight_index = index
        self.update()
        # 500ms后取消高亮
        QTimer.singleShot(500, lambda: self._clear_highlight())
    
    def animate_insert(self, index: int):
        """插入节点动画"""
        self.new_node_index = index
        self.animation_alpha = 100  # 从半透明开始
        self.animation_step = 0
        self.animation_timer.start(30)  # 30ms每帧
    
    def animate_delete(self, index: int):
        """删除节点动画"""
        self.delete_node_index = index
        self.animation_alpha = 255  # 从完全不透明开始
        self.animation_step = 0
        self.animation_timer.start(30)  # 30ms每帧
    
    def _animate(self):
        """动画帧更新"""
        self.animation_step += 1
        
        if self.new_node_index >= 0:
            # 插入动画：透明度逐渐增加
            self.animation_alpha = min(255, 100 + self.animation_step * 15)
            if self.animation_alpha >= 255:
                self.animation_timer.stop()
                self.new_node_index = -1
        elif self.delete_node_index >= 0:
            # 删除动画：透明度逐渐减少
            self.animation_alpha = max(0, 255 - self.animation_step * 25)
            if self.animation_alpha <= 0:
                self.animation_timer.stop()
                self.delete_node_index = -1
        
        self.update()
    
    def _clear_highlight(self):
        """清除高亮"""
        self.highlight_index = -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制参数
        node_width = 60
        node_height = 40
        spacing = 50   # 箭头长度
        start_x = 40   # 起始 X 坐标
        start_y = (self.height() - node_height) // 2 # 垂直居中

        # 空链表显示特殊文字
        if not self.data_items:
            painter.setFont(QFont("Arial", 14))
            painter.setPen(Qt.GlobalColor.gray)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Head -> None")
            return

        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        for i, item in enumerate(self.data_items):
            x = start_x + i * (node_width + spacing)
            
            # 1. 绘制节点连线 (箭头)
            # 箭头的起点是当前节点右侧，终点是下一个节点左侧
            arrow_start_x = x + node_width
            arrow_end_x = arrow_start_x + spacing
            center_y = start_y + node_height // 2
            
            painter.setPen(QPen(Qt.GlobalColor.gray, 2))
            
            if i < len(self.data_items) - 1:
                # 指向下一个节点
                painter.drawLine(arrow_start_x, center_y, arrow_end_x, center_y)
                # 箭头头部 ( > 形状)
                painter.drawLine(arrow_end_x - 10, center_y - 5, arrow_end_x, center_y)
                painter.drawLine(arrow_end_x - 10, center_y + 5, arrow_end_x, center_y)
            else:
                # 最后一个节点指向 None
                painter.drawLine(arrow_start_x, center_y, arrow_end_x, center_y)
                # 画 None 文字
                painter.setFont(QFont("Arial", 10))
                painter.setPen(Qt.GlobalColor.gray)
                painter.drawText(arrow_end_x + 5, center_y + 5, "None")
                # 箭头头部
                painter.drawLine(arrow_end_x - 10, center_y - 5, arrow_end_x, center_y)
                painter.drawLine(arrow_end_x - 10, center_y + 5, arrow_end_x, center_y)
                # 恢复字体以供下一次循环绘制节点
                painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            # 2. 绘制节点方块
            # 根据状态选择颜色
            if i == self.highlight_index:
                # 高亮节点：黄色
                painter.setBrush(QBrush(QColor(255, 215, 0)))
                painter.setPen(QPen(QColor(218, 165, 32), 3))
            elif i == self.new_node_index:
                # 新插入节点：渐变绿色
                color = QColor(0, 255, 0, self.animation_alpha)
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(QColor(34, 139, 34), 2))
            elif i == self.delete_node_index:
                # 删除节点：渐变红色
                color = QColor(255, 0, 0, self.animation_alpha)
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(QColor(139, 0, 0), 2))
            else:
                # 普通节点：浅蓝色
                painter.setBrush(QBrush(QColor(173, 216, 230)))
                painter.setPen(QPen(QColor(152, 180, 212), 2))
            
            painter.drawRect(x, start_y, node_width, node_height)
            
            # 3. 绘制节点文字
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(x, start_y, node_width, node_height, 
                           Qt.AlignmentFlag.AlignCenter, str(item))