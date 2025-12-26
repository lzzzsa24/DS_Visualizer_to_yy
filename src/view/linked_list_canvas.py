import math
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
        self.new_node_index = -1   # 新插入节点的索引
        self.delete_node_index = -1  # 删除节点的索引
        self.animation_alpha = 255  # 透明度（删除动画遗留，不再用于插入）
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
        self.pointer_alpha = 0  # 指针动画透明度（不再用于插入）
        self.animation_phase = 0  # 动画阶段
        # 插入几何动画进度
        self.new_arrow_progress = 0.0  # 新节点箭头从 None 指向下一个的进度 0->1
        self.prev_arrow_progress = 0.0 # 前驱节点箭头指向新节点的进度 0->1
        self.drop_progress = 0.0       # 新节点下落进度 0->1
        # 删除几何动画状态
        self.delete_active = False
        self.delete_arrow_progress = 0.0
        self.delete_lift_progress = 0.0
        self.delete_lift_height = 50
        self.delete_prev_index = -1
        self.delete_next_index = -1
        self.delete_ghost_value = None
        self.delete_fade_progress = 0.0
        
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
    
    def animate_insert_slide(self, index: int):
        """滑动插入动画：新节点出现与指针转向 → 前驱转向 → 节点右移 + 新节点下落"""
        self.new_node_index = index
        self.slide_active = True
        self.slide_index = index
        self.slide_progress = 0.0
        self.animation_step = 0
        # 重构阶段：0 新节点上方出现并指向 None（后继不动）
        # 1 新节点箭头从 None 转向下一个
        # 2 前驱箭头从原指向（后继）转向斜上方的新节点
        # 3 后续节点同时右移、新节点下落，箭头随动
        self.animation_phase = 0
        self.new_arrow_progress = 0.0
        self.prev_arrow_progress = 0.0
        self.drop_progress = 0.0

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
    
    def animate_delete(self, index: int, value=None):
        """删除节点动画：节点上提 + 右侧合拢 → 前驱箭头转向后继/None"""
        self.delete_node_index = index
        self.delete_ghost_value = value
        self.delete_prev_index = index - 1 if index > 0 else -1
        self.delete_next_index = index if index < len(self.data_items) else -1
        self.delete_active = True
        self.delete_arrow_progress = 0.0
        self.delete_lift_progress = 0.0
        self.delete_fade_progress = 0.0
        self.animation_phase = 0
        self.animation_step = 0
        # 右侧节点初始保持在旧位置，随后向左合拢
        self.slide_delete_active = True
        self.delete_slide_index = index
        self.delete_slide_progress = 1.0
        self.pointer_animation_active = False
        self.animation_timer.start(30)
    
    def _animate(self):
        """动画帧更新"""
        self.animation_step += 1
        
        if self.slide_active and self.new_node_index >= 0:
            # 新插入五步几何动画
            if self.animation_phase == 0:
                # 新节点上方出现，箭头指向 None
                if self.animation_step >= 10:
                    if self.new_pointer_to < 0:
                        # 无后继：直接转前驱阶段或下落
                        if self.slide_index > 0:
                            self.animation_phase = 2
                            self.animation_step = 0
                            self.prev_arrow_progress = 0.0
                        else:
                            self.animation_phase = 3
                            self.animation_step = 0
                    else:
                        self.animation_phase = 1
                        self.animation_step = 0
            elif self.animation_phase == 1:
                # 新节点箭头从 None 转向后继
                self.new_arrow_progress = min(1.0, self.new_arrow_progress + 0.08)
                if self.new_arrow_progress >= 1.0:
                    if self.slide_index > 0:
                        self.animation_phase = 2
                        self.animation_step = 0
                        self.prev_arrow_progress = 0.0
                    else:
                        self.animation_phase = 3
                        self.animation_step = 0
            elif self.animation_phase == 2:
                # 前驱箭头转向新节点（旧指向为后继）
                self.prev_arrow_progress = min(1.0, self.prev_arrow_progress + 0.08)
                if self.prev_arrow_progress >= 1.0:
                    self.animation_phase = 3
                    self.animation_step = 0
                    self.slide_progress = 0.0
                    self.drop_progress = 0.0
            elif self.animation_phase == 3:
                # 后续节点右移 + 新节点下落，箭头随动
                self.slide_progress = min(1.0, self.slide_progress + 0.08)
                self.drop_progress = self.slide_progress
                if self.slide_progress >= 1.0:
                    self.animation_timer.stop()
                    self.slide_active = False
                    self._reset_animation_state()

        # 删除动画阶段
        if self.delete_active and self.delete_node_index >= 0:
            if self.animation_phase == 0:
                # 节点上提淡出，同时右侧节点向左合拢，箭头随动
                self.delete_lift_progress = min(1.0, self.delete_lift_progress + 0.06)
                if self.slide_delete_active:
                    self.delete_slide_progress = max(0.0, self.delete_slide_progress - 0.05)
                    if self.delete_slide_progress <= 0.0:
                        self.slide_delete_active = False
                if self.delete_lift_progress >= 1.0 and not self.slide_delete_active:
                    if self.delete_prev_index >= 0:
                        self.animation_phase = 1
                        self.animation_step = 0
                        self.delete_arrow_progress = 0.0
                    else:
                        self.animation_timer.stop()
                        self._reset_animation_state()
            elif self.animation_phase == 1:
                # 前驱箭头缓缓转向后继/None
                self.delete_arrow_progress = min(1.0, self.delete_arrow_progress + 0.06)
                if self.delete_arrow_progress >= 1.0:
                    self.animation_phase = 2
                    self.animation_step = 0
                    self.delete_fade_progress = 0.0
            elif self.animation_phase == 2:
                # 指针到位后才开始淡出
                self.delete_fade_progress = min(1.0, self.delete_fade_progress + 0.08)
                if self.delete_fade_progress >= 1.0:
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
        self.slide_progress = 0.0
        self.drop_progress = 0.0
        self.new_arrow_progress = 0.0
        self.prev_arrow_progress = 0.0
        self.delete_active = False
        self.delete_arrow_progress = 0.0
        self.delete_lift_progress = 0.0
        self.delete_prev_index = -1
        self.delete_next_index = -1
        self.delete_ghost_value = None
        self.slide_delete_active = False
        self.delete_slide_index = -1
        self.delete_slide_progress = 1.0
        self.delete_fade_progress = 0.0
    
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
            
            # 新节点立即可见（在上方悬浮），不再跳过绘制
            skip_new_node_draw = False
            
            # 插入时：后侧节点保持旧位置，最终回位
            if self.slide_active and i > self.slide_index:
                offset = int(self.shift_distance * (1.0 - self.slide_progress))
                x -= offset
            
            # 新节点上方悬浮与下落
            if self.slide_active and i == self.slide_index:
                if self.animation_phase <= 2:
                    y = start_y - self.new_node_start_offset_y
                elif self.animation_phase == 3:
                    y = start_y - int(self.new_node_start_offset_y * (1.0 - self.drop_progress))

            # 删除后向左合拢：删除位置右侧的节点从右侧回位
            if self.slide_delete_active and i >= self.delete_slide_index:
                offset_left = int(self.shift_distance * (self.delete_slide_progress))
                x += offset_left
            
            # 1. 绘制节点连线 (箭头)
            arrow_start_x = x + node_width
            arrow_end_x = arrow_start_x + spacing
            center_y = y + node_height // 2
            
            # 决定是否绘制这个箭头
            should_draw_arrow = True
            arrow_color = Qt.GlobalColor.gray
            arrow_width = 2
            arrow_alpha = 255
            
            # 处理指针/插入阶段箭头动画
            if self.pointer_animation_active:
                # 删除动画中，显示旧指针淡出
                if self.animation_phase >= 1 and i == self.old_pointer_from and self.old_pointer_to == i + 1:
                    # 移除颜色/透明度动画，始终使用固定颜色
                    arrow_alpha = 255
                # 删除动画中，显示新指针出现（跳过删除节点）
                elif self.animation_phase >= 1 and i == self.new_pointer_from and self.new_pointer_to > i + 1:
                    # 绘制跳过的曲线箭头
                    if self.pointer_alpha >= 0:
                        self._draw_curved_arrow(painter, x + node_width, start_y + node_height // 2,
                                              start_x + self.new_pointer_to * (node_width + spacing), 
                                              start_y + node_height // 2,
                                              QColor(128, 128, 128, 255), 3)
                    should_draw_arrow = False
            
            # 插入动画定制箭头
            next_exists = (self.new_pointer_to >= 0 and self.new_pointer_to < len(self.data_items))
            next_x = start_x + self.new_pointer_to * (node_width + spacing) if next_exists else None
            if self.slide_active and next_exists and self.new_pointer_to > self.slide_index:
                next_x -= int(self.shift_distance * (1.0 - self.slide_progress))
            next_y = start_y + node_height // 2 if next_exists else None

            # 新节点箭头
            if self.slide_active and i == self.slide_index:
                should_draw_arrow = False
                sx = x + node_width
                sy = center_y
                if self.animation_phase == 0:
                    ex = sx + spacing
                    ey = sy
                    self._draw_arrow_line(painter, sx, sy, ex, ey, QColor(128, 128, 128, 255), 2)
                    painter.setFont(QFont("Arial", 10))
                    painter.setPen(Qt.GlobalColor.gray)
                    painter.drawText(ex + 5, ey + 5, "None")
                    painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                elif self.animation_phase == 1 and next_exists:
                    ex0, ey0 = sx + spacing, sy
                    ex1, ey1 = next_x, next_y
                    ex = int(ex0 + (ex1 - ex0) * self.new_arrow_progress)
                    ey = int(ey0 + (ey1 - ey0) * self.new_arrow_progress)
                    self._draw_arrow_line(painter, sx, sy, ex, ey, QColor(128, 128, 128, 255), 2)
                elif self.animation_phase in (2, 3) and next_exists:
                    self._draw_arrow_line(painter, sx, sy, next_x, next_y, QColor(128, 128, 128, 255), 2)
                else:
                    ex = sx + spacing
                    ey = sy
                    self._draw_arrow_line(painter, sx, sy, ex, ey, QColor(128, 128, 128, 255), 2)
                    painter.setFont(QFont("Arial", 10))
                    painter.setPen(Qt.GlobalColor.gray)
                    painter.drawText(ex + 5, ey + 5, "None")
                    painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            # 前驱箭头
            prev_idx = self.slide_index - 1
            if self.slide_active and prev_idx >= 0 and i == prev_idx:
                should_draw_arrow = False
                psx = x + node_width
                psy = center_y
                # 旧指向（后继或 None）
                if next_exists:
                    old_ex, old_ey = next_x, next_y
                else:
                    old_ex, old_ey = psx + spacing, psy
                # 新指向（新节点左侧，中间高度）
                new_node_x = start_x + self.slide_index * (node_width + spacing)
                # 新节点当前位置 y（与上方悬浮/下落保持一致）
                if self.animation_phase <= 2:
                    new_node_y = start_y - self.new_node_start_offset_y
                else:
                    new_node_y = start_y - int(self.new_node_start_offset_y * (1.0 - self.drop_progress))
                new_ex = new_node_x
                new_ey = new_node_y + node_height // 2

                if self.animation_phase == 2:
                    ex = int(old_ex + (new_ex - old_ex) * self.prev_arrow_progress)
                    ey = int(old_ey + (new_ey - old_ey) * self.prev_arrow_progress)
                    self._draw_arrow_line(painter, psx, psy, ex, ey, QColor(128, 128, 128, 255), 2)
                elif self.animation_phase == 3:
                    self._draw_arrow_line(painter, psx, psy, new_ex, new_ey, QColor(128, 128, 128, 255), 2)
                else:
                    self._draw_arrow_line(painter, psx, psy, old_ex, old_ey, QColor(128, 128, 128, 255), 2)
            
            # 删除动画定制箭头（前驱 -> 删除节点/后继）
            if self.delete_active and i == self.delete_prev_index:
                should_draw_arrow = False
                psx = x + node_width
                psy = center_y
                ghost_x = start_x + self.delete_node_index * (node_width + spacing)
                ghost_y = start_y - int(self.delete_lift_height * self.delete_lift_progress)
                ghost_ey = ghost_y + node_height // 2
                # 新指向：后继节点现位置或 None（随合拢变化）
                if self.delete_next_index >= 0 and self.delete_next_index < len(self.data_items):
                    new_ex = start_x + self.delete_next_index * (node_width + spacing)
                    if self.slide_delete_active and self.delete_next_index >= self.delete_slide_index:
                        new_ex += int(self.shift_distance * self.delete_slide_progress)
                    new_ey = start_y + node_height // 2
                else:
                    new_ex = psx + spacing
                    new_ey = psy

                if self.animation_phase == 0:
                    self._draw_arrow_line(painter, psx, psy, ghost_x, ghost_ey, QColor(128, 128, 128, 255), 2)
                elif self.animation_phase == 1:
                    ex = int(ghost_x + (new_ex - ghost_x) * self.delete_arrow_progress)
                    ey = int(ghost_ey + (new_ey - ghost_ey) * self.delete_arrow_progress)
                    self._draw_arrow_line(painter, psx, psy, ex, ey, QColor(128, 128, 128, 255), 2)
                else:
                    self._draw_arrow_line(painter, psx, psy, new_ex, new_ey, QColor(128, 128, 128, 255), 2)

            # 绘制普通箭头
            if should_draw_arrow:
                if i < len(self.data_items) - 1:
                    # 指向下一个节点
                    self._draw_arrow_line(painter, arrow_start_x, center_y, arrow_end_x, center_y,
                                          QColor(128, 128, 128, arrow_alpha), arrow_width)
                else:
                    # 最后一个节点指向 None（统一箭头规格）
                    self._draw_arrow_line(painter, arrow_start_x, center_y, arrow_end_x, center_y,
                                          QColor(128, 128, 128, arrow_alpha), arrow_width)
                    painter.setFont(QFont("Arial", 10))
                    painter.setPen(Qt.GlobalColor.gray)
                    painter.drawText(arrow_end_x + 5, center_y + 5, "None")
                    painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            # 2. 绘制节点方块
            # 固定颜色：浅蓝色节点，不再使用颜色变化
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

        # 删除动画中的“幽灵”节点：箭头与节点同步淡出
        if self.delete_active and self.delete_node_index >= 0:
            ghost_x = start_x + self.delete_node_index * (node_width + spacing)
            ghost_y = start_y - int(self.delete_lift_height * self.delete_lift_progress)
            if self.animation_phase in (0, 1):
                alpha = 255  # 指针未完全指向后继前保持不透明
            elif self.animation_phase == 2:
                alpha = max(0, 255 - int(255 * self.delete_fade_progress))
            else:
                alpha = 0

            if alpha > 0:
                arrow_sx = ghost_x + node_width
                arrow_sy = ghost_y + node_height // 2
                if self.delete_next_index >= 0 and self.delete_next_index < len(self.data_items):
                    target_x = start_x + self.delete_next_index * (node_width + spacing)
                    if self.slide_delete_active and self.delete_next_index >= self.delete_slide_index:
                        target_x += int(self.shift_distance * self.delete_slide_progress)
                    target_y = start_y + node_height // 2
                else:
                    target_x = arrow_sx + spacing
                    target_y = arrow_sy
                self._draw_arrow_line(painter, arrow_sx, arrow_sy, target_x, target_y, QColor(128, 128, 128, alpha), 2)

                painter.setBrush(QBrush(QColor(173, 216, 230, alpha)))
                painter.setPen(QPen(QColor(152, 180, 212, alpha), 2))
                painter.drawRect(ghost_x, ghost_y, node_width, node_height)
                painter.setPen(QColor(255, 255, 255, alpha))
                text_value = str(self.delete_ghost_value) if self.delete_ghost_value is not None else ""
                painter.drawText(ghost_x, ghost_y, node_width, node_height,
                                 Qt.AlignmentFlag.AlignCenter, text_value)

        # 已移除插入阶段的颜色淡入箭头，改为几何插值绘制（见上方阶段2与阶段3）
    
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

    def _draw_arrow_line(self, painter, x1, y1, x2, y2, color, width):
        """绘制带角度箭头的直线"""
        painter.setPen(QPen(color, width))
        painter.drawLine(x1, y1, x2, y2)
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 10
        ax1 = x2 - size * math.cos(angle - math.pi / 6)
        ay1 = y2 - size * math.sin(angle - math.pi / 6)
        ax2 = x2 - size * math.cos(angle + math.pi / 6)
        ay2 = y2 - size * math.sin(angle + math.pi / 6)
        painter.drawLine(x2, y2, int(ax1), int(ay1))
        painter.drawLine(x2, y2, int(ax2), int(ay2))