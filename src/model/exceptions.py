class DSVisualizerError(Exception):
    """项目的基础异常类"""
    pass

class StructureEmptyError(DSVisualizerError):
    """当尝试从空的数据结构中取数据时抛出"""
    pass

class StructureFullError(DSVisualizerError):
    """当数据结构已满时抛出（如果有容量限制）"""
    pass

class StructureValueError(DSVisualizerError):
    """当传入的数据不符合要求时抛出"""
    pass



class GameError(Exception):
    """游戏所有自定义异常的基类"""
    pass

class MapLoadError(GameError):
    """当读取地图文件失败，或地图格式解析错误时抛出"""
    pass

class InventoryFullError(GameError):
    """当背包满时抛出"""
    pass
