import open3d as o3d
import numpy as np
import imgui
from imgui.integrations.glfw import GlfwRenderer
import OpenGL.GL as gl
import OpenGL.GLU as glu
import glfw
import tkinter as tk
from tkinter import filedialog
from mouse_controller import MouseController  # 导入 MouseController 类
from point_cloud_thinning import get_lod_point_cloud  # 导入点云稀疏算法

# 全局变量，用于存储用户选择的文件路径和点云数据
custom_ply_path = None
original_points = None
original_colors = None

# 读取 PLY 点云数据
def read_ply(file_path):
    pcd = o3d.io.read_point_cloud(file_path)
    return np.asarray(pcd.points), np.asarray(pcd.colors)

# 保存 PLY 点云数据
def save_ply(file_path, points, colors):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    o3d.io.write_point_cloud(file_path, pcd)

# 绘制XYZ轴
def draw_axes(length=0.5, line_width=2.0):
    gl.glLineWidth(line_width)  # 设置线宽
    gl.glBegin(gl.GL_LINES)
    
    # X轴 - 红色
    gl.glColor3f(1.0, 0.0, 0.0)
    gl.glVertex3f(0.0, 0.0, 0.0)
    gl.glVertex3f(length, 0.0, 0.0)
    
    # Y轴 - 绿色
    gl.glColor3f(0.0, 1.0, 0.0)
    gl.glVertex3f(0.0, 0.0, 0.0)
    gl.glVertex3f(0.0, length, 0.0)
    
    # Z轴 - 蓝色
    gl.glColor3f(0.0, 0.0, 1.0)
    gl.glVertex3f(0.0, 0.0, 0.0)
    gl.glVertex3f(0.0, 0.0, length)
    
    gl.glEnd()
    gl.glLineWidth(1.0)  # 恢复默认线宽

# 渲染点云
def render_point_cloud(points, colors):
    gl.glBegin(gl.GL_POINTS)
    for point, color in zip(points, colors):
        gl.glColor3f(*color)
        gl.glVertex3f(*point)
    gl.glEnd()
    
    # 绘制XYZ轴
    draw_axes()

# ImGui 界面
def imgui_interface(is_thinning_enabled, ds, dh, lod_level, simplify_callback, load_ply_callback):
    imgui.new_frame()
    imgui.begin("Point Cloud Controls")
    imgui.text("Adjust point cloud settings:")

    _, is_thinning_enabled = imgui.checkbox("Enable Thinning", is_thinning_enabled)
    
    changed_ds, ds = imgui.slider_float("Distance Threshold (ds)", ds, 0.1, 100.0)
    changed_dh, dh = imgui.slider_float("Height Threshold (dh)", dh, 0.1, 100.0)
    changed_lod, lod_level = imgui.slider_float("LOD Level", lod_level, 0.001, 1.0)
    
    if imgui.button("Load PLY File"):
        load_ply_callback()
    
    if imgui.button("Save Simplified Point Cloud"):
        if is_thinning_enabled:
            simplify_callback(lod_level)

    imgui.end()
    imgui.render()

    return is_thinning_enabled, changed_ds, ds, changed_dh, dh, changed_lod, lod_level

# 主程序
def main():
    global custom_ply_path, original_points, original_colors

    # 初始化 GLFW
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Point Cloud Fast Thinning (Based on Sample Point Spatial Neighborhood)", None, None)
    glfw.make_context_current(window)

    imgui.create_context()
    impl = GlfwRenderer(window)

    # 创建 MouseController 实例
    mouse_controller = MouseController()

    # 设置鼠标回调
    glfw.set_mouse_button_callback(window, mouse_controller.mouse_button_callback)
    glfw.set_cursor_pos_callback(window, mouse_controller.cursor_position_callback)
    glfw.set_scroll_callback(window, mouse_controller.scroll_callback)

    lod_level = 1.0  # 初始 LOD 级别
    ds = 10.0  # 初始距离阈值
    dh = 10.0  # 初始高度阈值
    is_thinning_enabled = False  # 初始稀疏算法状态
    points, colors = np.array([]), np.array([])  # 初始化为空数组

    def simplify_callback(lod_level):
        nonlocal points, colors
        if original_points is not None and original_colors is not None:
            points, colors = get_lod_point_cloud(ds, dh, lod_level, original_points, original_colors)
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(title="Save PLY File", defaultextension=".ply", filetypes=[("PLY files", "*.ply")])
            if file_path:
                save_ply(file_path, points, colors)

    def load_ply_callback():
        global custom_ply_path, original_points, original_colors
        nonlocal points, colors
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Open PLY File", filetypes=[("PLY files", "*.ply")])
        if file_path:
            custom_ply_path = file_path
            original_points, original_colors = read_ply(file_path)
            points, colors = original_points, original_colors

    # 主循环
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        # 获取窗口尺寸
        width, height = glfw.get_framebuffer_size(window)
        gl.glViewport(0, 0, width, height)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 设置 ImGui 显示尺寸
        io = imgui.get_io()
        io.display_size = (width, height)

        # 设置视图变换
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, width / float(height), 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        glu.gluLookAt(mouse_controller.translation[0], mouse_controller.translation[1], 5 / mouse_controller.zoom, 
                      mouse_controller.translation[0], mouse_controller.translation[1], 0, 
                      0, 1, 0)
        gl.glRotatef(mouse_controller.rotation[0], 1, 0, 0)
        gl.glRotatef(mouse_controller.rotation[1], 0, 1, 0)

        # 更新 LOD
        if is_thinning_enabled and original_points is not None and original_colors is not None:
            points, colors = get_lod_point_cloud(ds, dh, lod_level, original_points, original_colors)
        elif not is_thinning_enabled and original_points is not None and original_colors is not None:
            points, colors = original_points, original_colors

        # OpenGL 渲染
        if points.size > 0 and colors.size > 0:
            render_point_cloud(points, colors)
        else:
            # 绘制XYZ轴
            draw_axes()

        # ImGui 渲染
        is_thinning_enabled, changed_ds, ds, changed_dh, dh, changed_lod, lod_level = imgui_interface(is_thinning_enabled, ds, dh, lod_level, simplify_callback, load_ply_callback)
        impl.render(imgui.get_draw_data())

        # 更新鼠标控制状态
        mouse_controller.update(not imgui.is_any_item_hovered())

        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()