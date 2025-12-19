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
        
        # 指针动画状态
        self.pointer_animation_active = False  # 是否正在播放指针动画
        self.temp_node_pos = None  # 临时节点位置 (x, y, value)
        self.old_pointer_from = -1  # 旧指针的起始节点
        self.old_pointer_to = -1  # 旧指针的目标节点
        self.new_pointer_from = -1  # 新指针的起始节点
        self.new_pointer_to = -1  # 新指针的目标节点
        self.pointer_alpha = 0  # 指针动画透明度
        self.animation_phase = 0  # 动画阶段
        
        # 滑动插入动画状态
        self.slide_active = False
        self.slide_index = -1
        self.slide_progress = 0.0  # 0.0 -> 1.0
        self.shift_distance = 110  # 与 node_width + spacing 保持一致默认值，运行时根据计算更新
        self.new_node_start_offset_y = 60  # 新节点从上方滑入的距离

        # 删除滑动动画状态
        self.slide_delete_active = False
        self.delete_slide_index = -1
        self.delete_slide_progress = 1.0  # 1.0 -> 0.0，向左合拢

    def update_data(self, items: list):
        self.data_items = items
        self.update()
    
    def highlight_node(self, index: int):
        """高亮指定节点"""
        self.highlight_index = index
        self.update()
        # 500ms后取消高亮
        QTimer.singleShot(500, lambda: self._clear_highlight())
    
    def animate_insert_slide(self, index: int):
        """滑动插入动画：右侧节点滑动让位 + 新节点自上方滑入 + 指针淡入"""
        self.new_node_index = index
        self.slide_active = True
        self.slide_index = index
        self.slide_progress = 0.0
        self.animation_step = 0
        self.animation_phase = 0  # 0:右侧滑动让位, 1:新节点下滑, 2:指针连接淡入

        # 指针目标（基于插入后的 data_items）
        if index >= 0 and index < len(self.data_items) - 1:
            self.new_pointer_from = index
            self.new_pointer_to = index + 1
        elif index == len(self.data_items) - 1 and len(self.data_items) > 1:
            # 尾插只显示前驱 -> 新节点指针（已由普通箭头绘制），无需额外新指针
            self.new_pointer_from = -1
            self.new_pointer_to = -1

        self.pointer_animation_active = True
        self.pointer_alpha = 0
        self.animation_timer.start(30)
    
    def animate_delete(self, index: int):
        """删除节点动画（带指针变化）"""
        self.delete_node_index = index
        self.pointer_animation_active = True
        self.animation_alpha = 255
        self.animation_step = 0
        self.animation_phase = 0  # 0:高亮节点, 1:指针跳过, 2:节点淡出
        
        # 设置指针跳过动画（注意：此方法适用于删除前的可视状态）
        if index > 0 and index < len(self.data_items) - 1:
            self.old_pointer_from = index - 1
            self.old_pointer_to = index
            self.new_pointer_from = index - 1
            self.new_pointer_to = index + 1
        elif index == 0 and len(self.data_items) > 1:
            self.old_pointer_to = 0
            self.new_pointer_to = 1
        
        self.animation_timer.start(30)

    def animate_delete_slide(self, index: int):
        """删除后向左合拢动画：右侧节点向左滑动填补空位"""
        self.delete_slide_index = index
        self.delete_slide_progress = 1.0
        self.slide_delete_active = True
        # 单独启动计时器（可能与其他动画共用）
        self.animation_timer.start(30)
    
    def _animate(self):
        """动画帧更新"""
        self.animation_step += 1
        
        if self.slide_active and self.new_node_index >= 0:
            # 滑动插入三阶段动画
            if self.animation_phase == 0:
                # 阶段0：右侧节点向右滑动让位
                self.slide_progress = min(1.0, self.slide_progress + 0.08)
                if self.slide_progress >= 1.0:
                    self.animation_phase = 1
                    self.animation_step = 0
            elif self.animation_phase == 1:
                # 阶段1：新节点由上向下滑入
                self.animation_alpha = min(255, 100 + self.animation_step * 20)
                if self.animation_step >= 12:  # 约 360ms
                    self.animation_phase = 2
                    self.animation_step = 0
            elif self.animation_phase == 2:
                # 阶段2：指针淡入连接
                self.pointer_alpha = min(255, self.pointer_alpha + 25)
                if self.pointer_alpha >= 255:
                    # 结束动画
                    self.animation_timer.stop()
                    self.slide_active = False
                    self._reset_animation_state()

        # 删除后的向左合拢动画（独立于上面的阶段）
        if self.slide_delete_active:
            self.delete_slide_progress = max(0.0, self.delete_slide_progress - 0.08)
            if self.delete_slide_progress <= 0.0:
                self.slide_delete_active = False
                # 不停止 timer，可能还有其他动画；若无其他动画，停止
                if not (self.slide_active or self.pointer_animation_active or self.delete_node_index >= 0):
                    self.animation_timer.stop()
            self.update()
        
        elif self.delete_node_index >= 0:
            # 删除动画
            if self.animation_phase == 0:
                # 阶段1：高亮需要删除的节点
                if self.animation_step >= 15:  # 保持高亮450ms
                    self.animation_phase = 1
                    self.animation_step = 0
            elif self.animation_phase == 1:
                # 阶段2：显示指针跳过
                self.pointer_alpha = min(255, self.animation_step * 25)
                if self.pointer_alpha >= 255:
                    self.animation_phase = 2
                    self.animation_step = 0
            elif self.animation_phase == 2:
                # 阶段3：节点渐隐
                self.animation_alpha = max(0, 255 - self.animation_step * 25)
                if self.animation_alpha <= 0:
                    self.animation_timer.stop()
                    self._reset_animation_state()
        
        self.update()
    
    def _reset_animation_state(self):
        """重置动画状态"""
        self.new_node_index = -1
        self.delete_node_index = -1
        self.pointer_animation_active = False
        self.old_pointer_from = -1
        self.old_pointer_to = -1
        self.new_pointer_from = -1
        self.new_pointer_to = -1
        self.pointer_alpha = 0
        self.animation_phase = 0
    
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

        # 根据当前参数更新 shift 距离
        self.shift_distance = node_width + spacing

        # 空链表显示特殊文字
        if not self.data_items:
            painter.setFont(QFont("Arial", 14))
            painter.setPen(Qt.GlobalColor.gray)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Head -> None")
            return

        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # 先绘制所有箭头和节点（考虑滑动偏移）
        for i, item in enumerate(self.data_items):
            x = start_x + i * (node_width + spacing)
            y = start_y
            
            # 插入阶段0：不渲染新节点本体（避免先出现在目标位置）
            skip_new_node_draw = (self.slide_active and i == self.slide_index and self.animation_phase == 0)
            
            # 滑动插入时：插入位置右侧的节点先向右偏移，随后回位
            if self.slide_active and i > self.slide_index:
                # 从旧位置（左侧）缓慢滑到新位置（右侧）
                # 新位置为 x，旧位置为 x - shift_distance
                # 因此应用负偏移使初始显示在旧位置，随后滑到 x
                offset = int(self.shift_distance * (1.0 - self.slide_progress))
                x -= offset
            
            # 新节点从上方滑入（仅插入位置，阶段1下滑一次；阶段2保持到位）
            if self.slide_active and i == self.slide_index and self.animation_phase == 1:
                y = start_y - int(self.new_node_start_offset_y * (1.0 - min(1.0, self.animation_step / 12.0)))

            # 删除后向左合拢：删除位置右侧的节点从右侧回位
            if self.slide_delete_active and i >= self.delete_slide_index:
                offset_left = int(self.shift_distance * (self.delete_slide_progress))
                x += offset_left
            
            # 1. 绘制节点连线 (箭头)
            arrow_start_x = x + node_width
            arrow_end_x = arrow_start_x + spacing
            center_y = start_y + node_height // 2
            
            # 决定是否绘制这个箭头
            should_draw_arrow = True
            arrow_color = Qt.GlobalColor.gray
            arrow_width = 2
            arrow_alpha = 255
            
            # 处理指针/插入阶段箭头动画
            if self.pointer_animation_active:
                # 删除动画中，显示旧指针淡出
                if self.animation_phase >= 1 and i == self.old_pointer_from and self.old_pointer_to == i + 1:
                    arrow_alpha = max(0, 255 - self.pointer_alpha)
                # 删除动画中，显示新指针出现（跳过删除节点）
                elif self.animation_phase >= 1 and i == self.new_pointer_from and self.new_pointer_to > i + 1:
                    # 绘制跳过的曲线箭头
                    if self.pointer_alpha > 0:
                        self._draw_curved_arrow(painter, x + node_width, start_y + node_height // 2,
                                              start_x + self.new_pointer_to * (node_width + spacing), 
                                              start_y + node_height // 2,
                                              QColor(0, 200, 0, self.pointer_alpha), 3)
                    should_draw_arrow = False
            
            # 插入阶段0：前驱 -> 新节点的箭头暂不绘制（新节点尚未出现）
            if self.slide_active and self.animation_phase == 0 and i == self.slide_index - 1:
                should_draw_arrow = False
            
            # 绘制普通箭头
            if should_draw_arrow:
                painter.setPen(QPen(QColor(128, 128, 128, arrow_alpha), arrow_width))
                
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
            
            # 跳过新节点的绘制（插入阶段0），只在阶段1开始下滑时出现
            if not skip_new_node_draw:
                painter.drawRect(x, y, node_width, node_height)
            
            # 3. 绘制节点文字
            if not skip_new_node_draw:
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(x, y, node_width, node_height, 
                               Qt.AlignmentFlag.AlignCenter, str(item))

        # 插入动画时，新指针淡入（index -> index+1）
        if self.slide_active and self.animation_phase == 2 and self.new_pointer_from >= 0:
            from_x = start_x + self.new_pointer_from * (node_width + spacing) + node_width
            to_x = start_x + self.new_pointer_to * (node_width + spacing)
            y = start_y + node_height // 2
            painter.setPen(QPen(QColor(0, 200, 0, self.pointer_alpha), 3))
            painter.drawLine(from_x, y, to_x, y)
            painter.drawLine(to_x - 10, y - 5, to_x, y)
            painter.drawLine(to_x - 10, y + 5, to_x, y)
    
    def _draw_curved_arrow(self, painter, x1, y1, x2, y2, color, width):
        """绘制弧形箭头（用于显示指针跳过）"""
        painter.setPen(QPen(color, width))
        
        # 计算控制点，使线条弯曲
        mid_x = (x1 + x2) / 2
        control_y = y1 - 30  # 向上弯曲
        
        # 绘制二次贝塞尔曲线（简化为直线近似）
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(x1, y1)
        path.quadTo(mid_x, control_y, x2, y2)
        painter.drawPath(path)
        
        # 绘制箭头
        painter.drawLine(x2 - 10, y2 - 5, x2, y2)
        painter.drawLine(x2 - 10, y2 + 5, x2, y2)