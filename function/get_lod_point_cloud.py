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

    # 使用固定的随机种子
    np.random.seed(42)  # 固定种子以确保一致性

    # 计算采样率，假设 lod_level 越高，采样率越低
    sample_rate = max(0.1, 1.0 - lod_level * 0.1)
    num_points = int(len(original_points) * sample_rate)

    # 随机选择点
    indices = np.random.choice(len(original_points), num_points, replace=False)
    sampled_points = original_points[indices]
    sampled_colors = original_colors[indices]

    return sampled_points, sampled_colors


def auto_lod_level(camera_position, points, max_lod_level, block_size=10):
    """
    根据相机位置和视角内点云位置计算自动LOD级别。

    :param camera_position: 相机的位置 (x, y, z)。
    :param points: 点云的点数据。
    :param max_lod_level: 最大LOD级别。
    :param block_size: 分块大小。
    :return: 每个块的LOD级别列表。
    """
    # 计算每个点到相机的距离
    distances = np.linalg.norm(points - np.array(camera_position), axis=1)

    # 初始化每个块的LOD级别
    lod_levels = np.zeros(len(points), dtype=int)

    # 分块处理
    for i in range(0, len(points), block_size):
        block_points = points[i:i + block_size]
        block_distances = distances[i:i + block_size]

        # 计算块内点的平均距离
        average_distance = np.mean(block_distances)

        # 反转距离与LOD级别的映射，距离越近，LOD级别越低
        lod_level = max_lod_level - int((average_distance / 100.0) * max_lod_level)
        lod_level = min(max(lod_level, 0), max_lod_level)

        # 为该块内的所有点设置相同的LOD级别
        lod_levels[i:i + block_size] = lod_level

    return lod_levels