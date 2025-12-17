from PyQt6.QtCore import Qt, QObject
from src.game.game_model import GameModel
from src.game.game_view import GameView

class GameController(QObject):
    def __init__(self, view: GameView):
        super().__init__()
        self.view = view
        self.model = GameModel() 

        # 连接信号
        self.view.key_pressed_signal.connect(self.handle_input)
        
        # 初始刷新
        self.refresh_view()

    def handle_input(self, key_code):
        """处理按键逻辑"""
        dx, dy = 0, 0
        if key_code == Qt.Key.Key_W: dy = -1
        elif key_code == Qt.Key.Key_S: dy = 1
        elif key_code == Qt.Key.Key_A: dx = -1
        elif key_code == Qt.Key.Key_D: dx = 1
        
        if dx != 0 or dy != 0:
            # 改数据
            self.model.move_player(dx, dy)
            # 刷新界面
            self.refresh_view()

    def refresh_view(self):
        """把 Model 的数据解包，喂给 View"""
        self.view.render(
            grid=self.model.grid,
            player_pos=(self.model.player_x, self.model.player_y),
            msg=self.model.message
        )