import open3d as o3d
from plyfile import PlyData
import numpy as np

def read_ply(file_path):
    """
    读取 PLY 文件并返回点和颜色数据。

    :param file_path: PLY 文件路径。
    :return: 点和颜色数据。
    """
    plydata = PlyData.read(file_path)
    points = np.vstack([plydata['vertex']['x'], 
                        plydata['vertex']['y'], 
                        plydata['vertex']['z']]).T
    colors = np.vstack([plydata['vertex']['red'], 
                        plydata['vertex']['green'], 
                        plydata['vertex']['blue']]).T / 255.0
    return points, colors

def save_ply(file_path, points, colors):
    """
    保存点云数据到 PLY 文件。

    :param file_path: 文件路径。
    :param points: 点云的点数据。
    :param colors: 点云的颜色数据。
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    o3d.io.write_point_cloud(file_path, pcd)