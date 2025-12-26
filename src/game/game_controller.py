from PyQt6.QtCore import Qt, QObject,QTimer,QUrl
from src.game.game_model import GameModel
from src.game.game_view import GameView
from src.model.exceptions import StructureFullError,StructureEmptyError
from PyQt6.QtMultimedia import QSoundEffect
import os,math

class GameController(QObject):
    def __init__(self, view: GameView):
        super().__init__()

        #初始化音效
        self.push_sound = QSoundEffect()
        self.pop_sound = QSoundEffect()
        self.error_sound = QSoundEffect()
        self.step_sound = QSoundEffect()
        current_dir = os.path.dirname(os.path.abspath(__file__)) # 获取当前文件所在目录
        project_root = os.path.dirname(os.path.dirname(current_dir)) # 往上跳两级：src -> 根目录
        sounds_dir = os.path.join(project_root, 'resources', 'sounds')

        push_sound_path = os.path.join(sounds_dir, 'add_element_successfully.wav')
        pop_sound_path = os.path.join(sounds_dir, 'remove_element_successfully.wav')
        error_sound_path = os.path.join(sounds_dir, 'error.wav')
        step_sound_path = os.path.join(sounds_dir, 'step.wav')
        self.push_sound.setSource(QUrl.fromLocalFile(push_sound_path))
        self.pop_sound.setSource(QUrl.fromLocalFile(pop_sound_path))
        self.error_sound.setSource(QUrl.fromLocalFile(error_sound_path))
        self.step_sound.setSource(QUrl.fromLocalFile(step_sound_path))
        self.push_sound.setVolume(0.5)  # 设置音量
        self.pop_sound.setVolume(4.0)
        self.error_sound.setVolume(0.3)
        self.step_sound.setVolume(0.8)

        # 初始化 MVC 组件
        self.view = view
        self.model = GameModel() 

        # 连接键盘信号
        self.view.key_pressed_signal.connect(self.on_key_pressed)
        self.view.key_released_signal.connect(self.on_key_released)

        # 连接复活信号
        self.view.game_over_overlay.retry_signal.connect(self.reset_game)
        self.view.game_over_overlay.quit_signal.connect(self.quit_game)

        # 移动循环
        self.pressed_keys = set()
        self.move_timer = QTimer()
        self.move_timer.setInterval(30)  # 每200毫秒处理一次移动
        self.move_timer.timeout.connect(self.process_movement)

        # 初始刷新
        self.refresh_view()

    def on_key_pressed(self, key_code):
        """处理按键按下事件"""
        if self.model.is_game_over:
            return

        self.pressed_keys.add(key_code)
        if not self.move_timer.isActive():
            self.process_movement()  # 立即处理一次移动
            self.move_timer.start()

    def on_key_released(self, key_code):
        """处理按键释放事件"""
        if key_code in self.pressed_keys:
            self.pressed_keys.remove(key_code)
        if not self.pressed_keys:
            self.move_timer.stop()

    def process_movement(self):
        """根据当前按下的键处理移动"""
        if self.model.is_game_over:
            self.move_timer.stop()
            return
        
        # 1. 计算合力方向
        dx, dy = 0.0, 0.0
        if Qt.Key.Key_W in self.pressed_keys: dy -= 1
        if Qt.Key.Key_S in self.pressed_keys: dy += 1
        if Qt.Key.Key_A in self.pressed_keys: dx -= 1
        if Qt.Key.Key_D in self.pressed_keys: dx += 1

        # 归一化 (防止斜走加速)
        if dx != 0 or dy != 0:
            length = math.sqrt(dx**2 + dy**2)
            dx /= length
            dy /= length

        # 应用速度
        step_x = dx * self.model.move_speed
        step_y = dy * self.model.move_speed

        # 2. 分轴移动 (实现贴墙滑行)
        # 尝试 X 轴移动
        if step_x != 0:
            if self.try_move(self.model.player_x + step_x, self.model.player_y):
                self.model.player_x += step_x
        
        # 尝试 Y 轴移动
        if step_y != 0:
            if self.try_move(self.model.player_x, self.model.player_y + step_y):
                self.model.player_y += step_y

        # 3. 播放脚步
        if (step_x != 0 or step_y != 0) and not self.step_sound.isPlaying():
            self.step_sound.play()

        self.refresh_view()

    def try_move(self, new_x, new_y):
        """
        尝试移动到新位置。
        返回 True 表示允许移动（可能是空地，也可能是踩到了道具）。
        返回 False 表示被阻挡（撞墙，或撞到没钥匙的门）。
        副作用：如果碰到了道具/怪物，会直接触发交互逻辑。
        """
        # 1. 获取玩家在新位置的碰撞箱覆盖的所有格子
        overlapped_tiles = self.get_overlapped_tiles(new_x, new_y)
        
        can_move = True
        
        for tx, ty in overlapped_tiles:
            # 越界检查
            if not (0 <= tx < self.model.grid_width and 0 <= ty < self.model.grid_height):
                return False # 撞世界边界
            
            val = self.model.grid[ty][tx]
            
            # === 🧱 阻挡判定 (墙/门/虚空) ===
            if val == 1 or val == -1: # 墙或虚空
                return False # 只要角碰到墙，就不能动
            
            if val == 8: # 门
                # 特殊逻辑：如果是门，检查是否有钥匙
                top_item = self._get_stack_top()
                if top_item == 5: # 有钥匙
                    self.model.message = "门打开了！"
                    self.model.backpack.pop()
                    self.model.grid[ty][tx] = 0 # 门变成了空地
                    self.pop_sound.play()
                    # 检查是否通关
                    if not self.model.next_level():
                        self.model.message = "恭喜通关！"
                    return False 
                else:
                    self.model.message = "门锁着，需要钥匙！"
                    self.error_sound.play()
                    return False # 撞门

            # === 🎒 交互判定 (道具/怪物/火) ===
            # 这些东西也是“允许移动”的，但会触发副作用
            if val in [3, 4, 5, 6, 7]:
                self.handle_interaction(tx, ty, val)
                
        return True
    
    def handle_interaction(self, tx, ty, val):
        """处理与物体的交互 (拾取/战斗)"""
        top_item = self._get_stack_top()
        
        # 道具 (3水, 4剑, 5匙)
        if val in [3, 4, 5]:
            item_names = {3:"水", 4:"剑", 5:"钥匙"}
            try:
                self.model.backpack.push(val)
                self.model.message = f"获得 {item_names[val]}"
                self.model.grid[ty][tx] = 0 # 物品消失
                self.push_sound.play()
            except StructureFullError:
                self.model.message = "背包满了！"
                self.error_sound.play()
        
        # 怪物 (7)
        elif val == 7:
            if top_item == 4: # 剑
                self.model.message = "击杀怪物！"
                self.model.backpack.pop() # 消耗剑
                self.model.grid[ty][tx] = 0 # 怪物消失
                self.pop_sound.play()
            else:
                self.trigger_death("你被怪物吃掉了！")
        
        # 火焰 (6)
        elif val == 6:
            if top_item == 3: # 水
                self.model.message = "熄灭火焰！"
                self.model.backpack.pop()
                self.model.grid[ty][tx] = 0
                self.pop_sound.play()
            else:
                self.trigger_death("你被烧死了！")

    def _get_stack_top(self):
        """安全获取栈顶元素，如果栈为空则返回 None"""
        try:
            return self.model.backpack.peek()
        except StructureEmptyError:
            return None

    def get_overlapped_tiles(self, px, py):
        """根据玩家坐标和大小，计算出接触到的所有网格坐标"""
        size = self.model.player_size
        # 玩家中心在 px, py。我们需要计算左上角和右下角
        # 假设 px, py 是格子的逻辑坐标 (比如 1.5, 2.5 是格子中心)
        # 这里为了简单，假设 px, py 就是玩家的【中心点坐标】
        
        # 碰撞箱边界
        left = px + (1 - size) / 2
        right = left + size
        top = py + (1 - size) / 2
        bottom = top + size
        
        # 涉及到的网格索引范围
        min_x, max_x = int(left), int(right) # right如果是 1.9，int是1。如果是2.01，int是2
        min_y, max_y = int(top), int(bottom)
        
        tiles = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                tiles.append((x, y))
        return tiles

        
    def reset_game(self):
        """复活：重置当前关卡"""
        self.model.reset_current_level()
        # 隐藏复活覆盖层
        self.view.hide_game_over()
        self.refresh_view()

    def quit_game(self):
        """退出游戏"""
        import sys
        sys.exit(0)

    def trigger_death(self,death_message):
        """玩家死亡时调用"""
        self.model.is_game_over = True
        self.model.message = death_message
        self.refresh_view()
         # 显示复活覆盖层
        self.view.show_game_over()

    def refresh_view(self):
        """把 Model 的数据解包，喂给 View"""
        self.view.render(
            grid=self.model.grid,
            player_pos=(self.model.player_x, self.model.player_y),
            msg=self.model.message
        )
        #刷新背包
        backpack_items = self.model.backpack.get_items()
        backpack_capacity = self.model.backpack.capacity()
        self.view.update_backpack(backpack_items, backpack_capacity)