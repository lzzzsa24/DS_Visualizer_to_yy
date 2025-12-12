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
