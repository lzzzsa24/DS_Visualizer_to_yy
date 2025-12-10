import sys
from PyQt6.QtWidgets import QApplication
from src.view.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 设置全局字体大小，防止在高分屏上字太小
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
        