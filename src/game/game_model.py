from src.model.stack import Stack
import os
from src.model.exceptions import MapLoadError,InventoryFullError
from src.utils import get_base_path

class GameModel:
    def __init__(self):
        #定位资源路径
        project_root = get_base_path()
        self.resources_path = os.path.join(project_root, 'resources')
        self.maps_path = os.path.join(self.resources_path, 'maps')
        self.sounds_path = os.path.join(self.resources_path, 'sounds')
        #关卡
        self.level_files=[
            "1.txt",
            "2.txt",
            "3.txt",
            "4.txt",
            "5.txt"

        ]
        self.current_level_index = 0
        # 玩家背包 
        self.backpack = Stack(capacity=3)
        # 游戏消息 (用于显示在界面上)
        self.message = "欢迎来到栈国杀 - 按 WASD 移动"
        #移动相关
        self.player_x=0.0
        self.player_y=0.0
        self.player_start_x = 0.0  # 关卡中标记的初始位置
        self.player_start_y = 0.0
        self.move_speed=0.1  # 每次刷新移动的格子数
        self.player_size=0.6  # 玩家碰撞箱大小（格子数）
        # 地图定义
        self.grid_width = 0
        self.grid_height = 0
        self.grid = []
        
        self.load_level(self.current_level_index)

        #游戏状态
        self.is_game_over = False

      
    def load_level(self, level_index):
        """从文件加载关卡"""
        self.is_game_over = False
        if level_index >= len(self.level_files):
            self.message = " 恭喜！你已通过所有关卡！"
            return MapLoadError 

        file_name = self.level_files[level_index]
        full_path = os.path.join(self.maps_path,file_name)

        if not os.path.exists(full_path):
            print(f"Error: Map file not found: {full_path}")
            return MapLoadError
        
        # 符号 -> 数字 ID 映射表
        # 0=空地, 1=墙, 2=玩家
        # 3=水, 4=剑, 5=钥匙 (道具-入栈)
        # 6=火, 7=怪, 8=门 (障碍-需出栈)
        char_map = {
            '#': 1, '.': 0, 'P': 0, # P也是空地，但记录坐标
            'K': 5, 'D': 8,'M': 7, 'F': 6,
            'S': 4, 'W': 3,' ': -1
        }

        new_grid = []
        player_found = False  # 标记是否在文件中找到玩家位置
        
        # 读取文件
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # 1. 预处理：去掉换行符
            lines = [line.rstrip('\n') for line in lines]
            
            # 2. 找最大宽度 (为了把矩阵补齐)
            max_width = 0
            if lines:
                max_width = max(len(line) for line in lines)
            
            # 3. 解析每一行
            for y, line in enumerate(lines):
                row_data = []
                
                # 4. 自动补全：如果这就行短，后面补空格
                padded_line = line.ljust(max_width, ' ')
                
                for x, char in enumerate(padded_line):
                    if char == 'P':
                        self.player_x = float(x)
                        self.player_y = float(y)
                        self.player_start_x = float(x)  # 记录初始位置
                        self.player_start_y = float(y)
                        player_found = True
                        val = 0
                    else:
                        # 如果遇到未知的字符，默认当做虚空(-1)
                        val = char_map.get(char, -1) 
                    row_data.append(val)
                new_grid.append(row_data)

        self.grid = new_grid
        self.grid_height = len(self.grid)
        self.grid_width = len(self.grid[0]) if self.grid_height > 0 else 0
        
        # 如果文件中没有找到玩家位置标记，使用记录的初始位置或默认位置
        if not player_found:
            self.player_x = self.player_start_x
            self.player_y = self.player_start_y
        
        # 每次进新关卡，背包清空
        self.backpack.clear()
        self.message = f"第 {level_index + 1} 关：开始冒险！"
        return True
    
    def next_level(self):
        """切换到下一关的接口"""
        self.current_level_index += 1
        return self.load_level(self.current_level_index)

    def move_player(self, dx, dy):#暂时保留
        """更新坐标"""
        self.player_x += dx
        self.player_y += dy

    def reset_current_level(self):
        """重新加载当前关卡（用于死亡重置）"""
        self.backpack.clear() # 死后背包清空
        self.load_level(self.current_level_index)