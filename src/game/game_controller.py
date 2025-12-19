from PyQt6.QtCore import Qt, QObject
from src.game.game_model import GameModel
from src.game.game_view import GameView
from src.model.exceptions import StructureFullError,StructureEmptyError

class GameController(QObject):
    def __init__(self, view: GameView):
        super().__init__()
        self.view = view
        self.model = GameModel() 

        # 连接键盘信号
        self.view.key_pressed_signal.connect(self.handle_input)

        # 连接复活信号
        self.view.game_over_overlay.retry_signal.connect(self.reset_game)
        self.view.game_over_overlay.quit_signal.connect(self.quit_game)
        
        # 初始刷新
        self.refresh_view()
        
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

        # Case 2:  门 (8) -> 通关判定
        elif target_val == 8:
            if top_item == 5:  # 需要 Key (5)
                self.model.message = " 门打开了！下一层..."
                self.model.backpack.pop()
                if not self.model.next_level():
                    self.model.message = " 恭喜通关！所有关卡完成！"
            else:
                self.model.message = " 门锁着，你需要钥匙！"
        # Case 3:  怪物 (7) -> 战斗判定
        elif target_val == 7:
            if top_item == 4:  # 需要 Sword (4)
                self.model.message = " 你挥舞宝剑，击败了怪物！"
                self.model.grid[target_y][target_x] = 0 # 怪物消失
                self.model.move_player(dx, dy)
                self.model.backpack.pop() 
            else:
                self.trigger_death(" 你被怪物吃掉了！")

        # Case 4:  火焰 (6) -> 消耗品判定
        elif target_val == 6:
            # 栈的特性：我们要找水，而且通常要消耗水
            if top_item == 3:  # 需要 Water (3)
                self.model.message = " 你用水浇灭了火焰！"
                self.model.grid[target_y][target_x] = 0 # 火消失
                self.model.move_player(dx, dy)
                self.model.backpack.pop() 
            else:
                self.trigger_death(" 你被烧焦了！")

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
            except StructureFullError:
                # 失败后 (捕获异常)
                self.model.message = " 背包满了！装不下！"

        # Case 6: 空地 (0) -> 直接移动
        else:
            self.model.move_player(dx, dy)
            self.model.message = "栈，移动！"

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