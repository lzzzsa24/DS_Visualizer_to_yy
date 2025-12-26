import sys
import os

def get_base_path():
    """
    获取项目的根路径。
    兼容：
    1. 开发环境 (直接运行 main.py)
    2. PyInstaller 打包环境 (单文件 .exe 模式)
    """
    if hasattr(sys, '_MEIPASS'):
        # 打包后，PyInstaller 会把资源解压到这里
        return sys._MEIPASS
    else:
        # 开发环境：回退两级找到项目根目录
        # 假设此文件在 src/utils.py，回退两级就是 DS_Visualizer/
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))