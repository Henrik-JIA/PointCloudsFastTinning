import numpy as np

def get_lod_point_cloud(lod_level, original_points, original_colors):
    """
    根据 LOD 级别返回简化的点云数据。
    
    :param lod_level: LOD 级别，0 表示完整点云，较高的值表示更少的点。
    :param original_points: 原始点云的点数据。
    :param original_colors: 原始点云的颜色数据。
    :return: 简化后的点和颜色数据。
    """
    if lod_level <= 0:
        return original_points, original_colors

    # 计算采样率，假设 lod_level 越高，采样率越低
    sample_rate = max(0.1, 1.0 - lod_level * 0.1)
    num_points = int(len(original_points) * sample_rate)

    # 随机选择点
    indices = np.random.choice(len(original_points), num_points, replace=False)
    sampled_points = original_points[indices]
    sampled_colors = original_colors[indices]

    return sampled_points, sampled_colors