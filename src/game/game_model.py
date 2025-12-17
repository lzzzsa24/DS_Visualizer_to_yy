from src.model.stack import Stack

class GameModel:
    def __init__(self):
        # --- 核心数据 ---
        # 1. 玩家背包 (复用你的 Stack 类)
        self.backpack = Stack(capacity=5)
        
        # 2. 游戏消息 (用于显示在界面上)
        self.message = "欢迎来到栈之传说 - 按 WASD 移动"
        
        # 3. 地图定义
        # 0=空地, 1=墙, 2=玩家
        # 3=水, 4=剑, 5=钥匙 (道具-入栈)
        # 6=火, 7=怪, 8=门 (障碍-需出栈)
        self.grid_width = 10
        self.grid_height = 10
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 0, 0, 1, 0, 0, 4, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 3, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 7, 1, 1, 1, 5, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 1, 0, 1],
            [1, 0, 1, 6, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 8, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        # 4. 初始化位置
        self.player_x, self.player_y = self._find_player()
        self.grid[self.player_y][self.player_x] = 0 # 清除地图上的玩家标记，避免重复

    def _find_player(self):
        """遍历网格找到 2 的位置"""
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                if val == 2: return x, y
        return 1, 1

    def move_player(self, dx, dy):
        """核心逻辑：尝试移动"""
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # A. 越界检查
        if not (0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height):
            return

        target_val = self.grid[new_y][new_x]

        # B. 交互逻辑
        if target_val == 1: # 墙
            self.message = "Ouch! It's a wall."
            return # 撞墙不动

        elif target_val == 0: # 空地
            self.player_x, self.player_y = new_x, new_y
            self.message = "Moved."

        elif target_val in [3, 4, 5]: # 捡东西 (入栈)
            item_name = {3:"Potion", 4:"Sword", 5:"Key"}[target_val]
            try:
                self.backpack.push(target_val) 
                self.grid[new_y][new_x] = 0    # 捡走后变空地
                self.player_x, self.player_y = new_x, new_y
                self.message = f"Picked up {item_name}!"
            except:
                self.message = "Backpack is Full!"

        elif target_val in [6, 7, 8]: # 障碍物 (需要出栈)
             self._try_interact(new_x, new_y, target_val)

    def _try_interact(self, tx, ty, target):
        """处理消除逻辑"""
        if self.backpack.is_empty():
            self.message = "I need a tool!"
            return

        tool = self.backpack.peek() 
        
        # 配对规则: 6(火)-3(药), 7(怪)-4(剑), 8(门)-5(匙)
        match_map = {6:3, 7:4, 8:5}
        
        if match_map.get(target) == tool:
            self.backpack.pop()  
            self.grid[ty][tx] = 0 # 消除障碍
            self.player_x, self.player_y = tx, ty # 移动进去
            self.message = "Obstacle cleared!"
        else:
            self.message = "Wrong tool! Check stack top."