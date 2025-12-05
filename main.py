import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DS Visualizer - 环境验证")
        self.setGeometry(100, 100, 800, 600)
        
        # 屏幕中央显示文字
        label = QLabel("Hello, Data Structure!", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 设置一点简单的样式（加大字体）
        label.setStyleSheet("font-size: 24px; color: blue;")
        self.setCentralWidget(label)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()