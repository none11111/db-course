from app.services.point_service import PointService

def level_name(level):
    """获取等级名称的自定义过滤器"""
    return PointService.get_level_name(level)
