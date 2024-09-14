import numpy as np
import pandas as pd

# 点云稀疏算法
def point_cloud_thinning(points, colors, ds, dh):
    # 将点云数据转换为 DataFrame
    df = pd.DataFrame(points, columns=['x', 'y', 'z'])
    df['color_r'] = colors[:, 0]
    df['color_g'] = colors[:, 1]
    df['color_b'] = colors[:, 2]
    
    # 计算点到原点的距离
    df['distance'] = np.linalg.norm(points, axis=1)
    
    # 筛选满足距离和高度阈值的点
    thinned_df = df[(df['distance'] < ds) & (df['z'] < dh)]
    
    # 提取稀疏后的点和颜色
    thinned_points = thinned_df[['x', 'y', 'z']].to_numpy()
    thinned_colors = thinned_df[['color_r', 'color_g', 'color_b']].to_numpy()
    
    return thinned_points, thinned_colors

# 根据 LOD 级别选择点云数据
def get_tinning_point_cloud(ds, dh, lod_level, points, colors):
     # ds设置距离阈值
     # dh设置高度阈值
    return point_cloud_thinning(points, colors, lod_level * ds, lod_level * dh)