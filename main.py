import open3d as o3d
from plyfile import PlyData
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
    plydata = PlyData.read(file_path)
    points = np.vstack([plydata['vertex']['x'], plydata['vertex']['y'], plydata['vertex']['z']]).T
    colors = np.vstack([plydata['vertex']['red'], plydata['vertex']['green'], plydata['vertex']['blue']]).T / 255.0
    return points, colors

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

# 渲染深度场景
def render_depth_scene(points, depth_range, depth_axis):
    gl.glBegin(gl.GL_POINTS)
    for point in points:
        depth = 1.0 - min(point[depth_axis] / depth_range, 1.0)  # 使用选定轴作为深度值，并根据深度范围进行归一化，限制最大值为1.0，深度值越大颜色越亮
        gl.glColor3f(depth, depth, depth)  # 将深度值映射为灰度颜色
        gl.glVertex3f(*point)
    gl.glEnd()
    
    # 绘制XYZ轴
    draw_axes()

# ImGui 界面
def imgui_interface(mouse_controller, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, is_thinning_enabled, ds, dh, lod_level, point_size, simplify_callback, load_ply_callback, show_depth_scene, depth_range, depth_axis):
    imgui.new_frame()

    # 初始化变量
    changed_ds = changed_dh = changed_lod = changed_point_size = changed_depth_range = changed_depth_axis = False
    is_hovered = False  # 新增变量，指示鼠标是否悬停在 ImGui 窗口上
    
    # 菜单栏
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("Window", True):
            clicked, show_point_clouds_tinning_control = imgui.menu_item("Show Point Cloud Tinning Controls", None, show_point_clouds_tinning_control, True)
            clicked, show_camera_control = imgui.menu_item("Show Camera Controls", None, show_camera_control, True)
            clicked, show_point_size_control = imgui.menu_item("Show Point Clouds Control", None, show_point_size_control, True)
            imgui.end_menu()
        imgui.end_main_menu_bar()

    if show_point_clouds_tinning_control:
        opened, show_point_clouds_tinning_control = imgui.begin("Point Cloud Tinning Controls", True)
        if opened:
            imgui.text("Adjust point cloud settings:")

            _, is_thinning_enabled = imgui.checkbox("Enable Thinning", is_thinning_enabled)
            
            imgui.push_item_width(150)  # 固定滑动条宽度为150像素
            
            changed_ds, ds = imgui.slider_float("Distance Threshold (ds)", ds, 0.1, 100.0)
            changed_dh, dh = imgui.slider_float("Height Threshold (dh)", dh, 0.1, 100.0)
            changed_lod, lod_level = imgui.slider_float("LOD Level", lod_level, 0.001, 1.0)
            
            imgui.pop_item_width()  # 恢复默认宽度

            if imgui.button("Load PLY File"):
                load_ply_callback()
            
            if imgui.button("Save Simplified Point Cloud"):
                if is_thinning_enabled:
                    simplify_callback(lod_level)

        is_hovered = is_hovered or imgui.is_window_hovered()  # 更新悬停状态
        imgui.end()

    if show_camera_control:
        # 添加相机控制窗口
        if imgui.begin("Camera Control", True):
            if imgui.button(label='rot 180'):
                mouse_controller.rotation[0] += 180
            
            imgui.same_line()
            # 添加恢复初始位置按钮
            if imgui.button(label="Reset Position"):
                mouse_controller.reset_position()

            imgui.push_item_width(150)  # 固定滑动条宽度为150像素

            changed, mouse_controller.zoom = imgui.slider_float(
                    "Zoom", mouse_controller.zoom, 0.1, 5.0, "zoom = %.3f"
                )
            if changed:
                mouse_controller.update_zoom()

            changed, mouse_controller.rotation_sensitivity = imgui.slider_float(
                    "Rotate Sensitivity", mouse_controller.rotation_sensitivity, 0.1, 5.0, "rotate speed = %.3f"
                )
            imgui.same_line()
            if imgui.button(label="Reset Rotate Sensitivity"):
                mouse_controller.rotation_sensitivity = 0.5

            changed, mouse_controller.translation_sensitivity = imgui.slider_float(
                    "Move Sensitivity", mouse_controller.translation_sensitivity, 0.001, 1.0, "move speed = %.3f"
                )
            imgui.same_line()
            if imgui.button(label="Reset Move Sensitivity"):
                mouse_controller.translation_sensitivity = 0.01

            imgui.pop_item_width()  # 恢复默认宽度

        is_hovered = is_hovered or imgui.is_window_hovered()  # 更新悬停状态
        imgui.end()

    if show_point_size_control:
        # 添加点云大小控制窗口
        if imgui.begin("Point Clouds Control", True):
            imgui.push_item_width(150)  # 固定滑动条宽度为150像素
            changed_point_size, point_size = imgui.slider_float("Point Size", point_size, 1.0, 10.0, "size = %.1f")
            imgui.pop_item_width()  # 恢复默认宽度

            # 添加深度场景切换按钮
            _, show_depth_scene = imgui.checkbox("Show Depth Scene", show_depth_scene)
            
            # 添加深度轴选择下拉列表
            depth_axis_labels = ["X-Axis", "Y-Axis", "Z-Axis"]
            changed_depth_axis, depth_axis = imgui.combo("Depth Axis", depth_axis, depth_axis_labels)
            
            # 添加深度范围滑动条
            changed_depth_range, depth_range = imgui.slider_float("Depth Range", depth_range, 0.1, 100.0, "range = %.1f")

        is_hovered = is_hovered or imgui.is_window_hovered()  # 更新悬停状态
        imgui.end()

    imgui.render()

    return is_thinning_enabled, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, changed_ds, ds, changed_dh, dh, changed_lod, lod_level, changed_point_size, point_size, is_hovered, show_depth_scene, depth_range, depth_axis

# 主程序
def main():
    global custom_ply_path, original_points, original_colors

    # 初始化 GLFW
    if not glfw.init():
        return

    window = glfw.create_window(900, 600, "Point Cloud Fast Thinning (Based on Sample Point Spatial Neighborhood)", None, None)
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
    point_size = 1.0  # 初始点大小
    is_thinning_enabled = False  # 初始稀疏算法状态
    points, colors = np.array([]), np.array([])  # 初始化为空数组
    show_point_clouds_tinning_control = True  # 点云滤波控制窗口显示状态
    show_camera_control = True  # 相机控制窗口显示状态
    show_point_size_control = True  # 点云大小控制窗口显示状态
    show_depth_scene = False  # 初始深度场景显示状态
    depth_range = 10.0  # 初始深度范围
    depth_axis = 2  # 初始深度轴（Z轴）

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
        if width == 0 or height == 0:  # 防止宽度或高度为零
            continue
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
        if points.size > 0:
            gl.glPointSize(point_size)  # 设置点大小
            if show_depth_scene:
                render_depth_scene(points, depth_range, depth_axis)
            else:
                render_point_cloud(points, colors)
        else:
            # 绘制XYZ轴
            draw_axes()

        # ImGui 渲染
        is_thinning_enabled, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, changed_ds, ds, changed_dh, dh, changed_lod, lod_level, changed_point_size, point_size, is_hovered, show_depth_scene, depth_range, depth_axis = imgui_interface(mouse_controller, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, is_thinning_enabled, ds, dh, lod_level, point_size, simplify_callback, load_ply_callback, show_depth_scene, depth_range, depth_axis)
        impl.render(imgui.get_draw_data())

        # 更新鼠标控制状态
        mouse_controller.update(not is_hovered)

        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()