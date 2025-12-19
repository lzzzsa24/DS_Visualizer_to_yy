from PyQt6.QtCore import Qt, QObject,QTimer,QUrl
from src.game.game_model import GameModel
from src.game.game_view import GameView
from src.model.exceptions import StructureFullError,StructureEmptyError
from PyQt6.QtMultimedia import QSoundEffect
import os

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
        self.move_timer.setInterval(200)  # 每200毫秒处理一次移动
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
        
        for key_code in list(self.pressed_keys):
            self.handle_input(key_code)
        
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

    def handle_input(self, key_code):
        """处理玩家输入的移动指令"""
        if self.model.is_game_over:
            return

        dx, dy = 0, 0
        if key_code == Qt.Key.Key_W: dy = -1
        elif key_code == Qt.Key.Key_S: dy = 1
        elif key_code == Qt.Key.Key_A: dx = -1
        elif key_code == Qt.Key.Key_D: dx = 1
        
        if dx == 0 and dy == 0: return

        top_item = None 
        try:
            top_item = self.model.backpack.peek()
        except StructureEmptyError:
            top_item = None # 如果栈空了，就把栈顶当做 None

        # 下一步的位置
        target_x = self.model.player_x + dx
        target_y = self.model.player_y + dy

        # 1. 越界检查
        if not (0 <= target_x < self.model.grid_width and 0 <= target_y < self.model.grid_height):
            return 

        # 获取前方是什么
        target_val = self.model.grid[target_y][target_x]
        
        # 获取背包物品列表 (方便查找)
        backpack_items = self.model.backpack.get_items()

        # === 核心游戏逻辑 ===

        # Case 1:  墙 (1)
        if target_val == 1:
            self.model.message = " 墙壁太硬了，撞不开！"
            self.error_sound.play()

        # Case 2:  门 (8) -> 通关判定
        elif target_val == 8:
            if top_item == 5:  # 需要 Key (5)
                self.model.message = " 门打开了！下一层..."
                self.model.backpack.pop()
                self.pop_sound.play()
                if not self.model.next_level():
                    self.model.message = " 恭喜通关！所有关卡完成！"
            else:
                self.model.message = " 门锁着，你需要钥匙！"
                self.error_sound.play()
        # Case 3:  怪物 (7) -> 战斗判定
        elif target_val == 7:
            if top_item == 4:  # 需要 Sword (4)
                self.model.message = " 你挥舞宝剑，击败了怪物！"
                self.model.grid[target_y][target_x] = 0 # 怪物消失
                self.model.move_player(dx, dy)
                self.model.backpack.pop() 
                self.pop_sound.play()
            else:
                self.trigger_death(" 你被怪物吃掉了！")
                self.error_sound.play()

        # Case 4:  火焰 (6) -> 消耗品判定
        elif target_val == 6:
            # 栈的特性：我们要找水，而且通常要消耗水
            if top_item == 3:  # 需要 Water (3)
                self.model.message = " 你用水浇灭了火焰！"
                self.model.grid[target_y][target_x] = 0 # 火消失
                self.model.move_player(dx, dy)
                self.model.backpack.pop() 
                self.pop_sound.play()
            else:
                self.trigger_death(" 你被烧焦了！")
                self.error_sound.play()

        # Case 5:  道具 (3水, 4剑, 5匙) -> 拾取逻辑
        elif target_val in [3, 4, 5]:
            item_names = {3:"水", 4:"剑", 5:"钥匙"}
            try:
                # 尝试入栈
                self.model.backpack.push(target_val)
                # 成功后
                self.model.message = f"你获得了 {item_names[target_val]}"
                self.model.grid[target_y][target_x] = 0 # 地面变空
                self.model.move_player(dx, dy)
                self.push_sound.play()
            except StructureFullError:
                # 失败后 (捕获异常)
                self.model.message = " 背包满了！装不下！"
                self.error_sound.play()

        # Case 6: 空地 (0) -> 直接移动
        else:
            self.model.move_player(dx, dy)
            self.model.message = "栈，移动！"
            self.step_sound.play()

        # 刷新界面
        self.refresh_view()

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