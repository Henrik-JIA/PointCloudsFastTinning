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
from util.mouse_controller import MouseController
from function.point_cloud_thinning import get_tinning_point_cloud
from interface.camera_control_interface import camera_control_interface
from interface.point_clouds_tinning_control_interface import point_clouds_tinning_control_interface
from interface.point_clouds_control_interface import point_clouds_control_interface
from interface.wave_control_interface import wave_control_interface
import ctypes
import time

# 全局变量，用于存储用户选择的文件路径和点云数据
custom_ply_path = None
original_points = None
original_colors = None

# 读取 PLY 点云数据
def read_ply(file_path):
    plydata = PlyData.read(file_path)
    points = np.vstack([plydata['vertex']['x'], 
                        plydata['vertex']['y'], 
                        plydata['vertex']['z']]).T
    colors = np.vstack([plydata['vertex']['red'], 
                        plydata['vertex']['green'], 
                        plydata['vertex']['blue']]).T / 255.0
    return points, colors

# 保存 PLY 点云数据
def save_ply(file_path, points, colors):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    o3d.io.write_point_cloud(file_path, pcd)

# 绘制XYZ轴
def draw_axes(length=0.3, line_width=2.0):
    gl.glLineWidth(line_width)
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
    gl.glLineWidth(1.0)

# 渲染点云
def render_point_cloud_vbo(points, colors):
    # 创建VBO并绑定数据
    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    data = np.hstack((points, colors)).astype(np.float32)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)

    # 启用顶点属性
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    gl.glVertexPointer(3, gl.GL_FLOAT, 6 * data.itemsize, None)
    gl.glEnableClientState(gl.GL_COLOR_ARRAY)
    gl.glColorPointer(3, gl.GL_FLOAT, 6 * data.itemsize, ctypes.c_void_p(3 * data.itemsize))

    # 绘制点云
    gl.glDrawArrays(gl.GL_POINTS, 0, len(points))

    # 禁用顶点属性
    gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
    gl.glDisableClientState(gl.GL_COLOR_ARRAY)

    # 删除VBO
    gl.glDeleteBuffers(1, [vbo])

# 渲染深度场景
def render_depth_scene(points, depth_range, depth_axis):
    gl.glBegin(gl.GL_POINTS)
    for point in points:
        depth = 1.0 - min(point[depth_axis] / depth_range, 1.0)
        gl.glColor3f(depth, depth, depth)
        gl.glVertex3f(*point)
    gl.glEnd()
    
    # 绘制XYZ轴
    draw_axes()

# 新增函数：生成波动效果
def apply_wave_effect(points, amplitude, frequency, phase, axis):
    points = points.copy()
    points[:, axis] += amplitude * np.sin(frequency * points[:, (axis + 1) % 3] + phase)
    return points

# ImGui 界面
def imgui_interface(mouse_controller, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, show_wave_control, is_thinning_enabled, ds, dh, tinning_level, point_size, simplify_callback, load_ply_callback, show_depth_scene, depth_range, depth_axis, wave_amplitude, wave_frequency, wave_axis, is_wave_enabled, wave_speed, fps):
    imgui.new_frame()

    is_hovered = False

    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("Window", True):
            clicked, show_point_clouds_tinning_control = imgui.menu_item("Show Point Cloud Tinning Controls", None, show_point_clouds_tinning_control, True)
            clicked, show_camera_control = imgui.menu_item("Show Camera Controls", None, show_camera_control, True)
            clicked, show_point_size_control = imgui.menu_item("Show Point Clouds Control", None, show_point_size_control, True)
            clicked, show_wave_control = imgui.menu_item("Show Wave Controls", None, show_wave_control, True)
            imgui.end_menu()
        imgui.end_main_menu_bar()

    if show_point_clouds_tinning_control:
        is_thinning_enabled, ds, dh, tinning_level, hovered = point_clouds_tinning_control_interface(is_thinning_enabled, ds, dh, tinning_level, simplify_callback, load_ply_callback, fps)
        is_hovered = is_hovered or hovered

    if show_camera_control:
        hovered = camera_control_interface(mouse_controller)
        is_hovered = is_hovered or hovered

    if show_point_size_control:
        point_size, show_depth_scene, depth_range, depth_axis, hovered = point_clouds_control_interface(point_size, show_depth_scene, depth_range, depth_axis)
        is_hovered = is_hovered or hovered

    if show_wave_control:
        is_wave_enabled, wave_amplitude, wave_frequency, wave_speed, wave_axis, hovered = wave_control_interface(is_wave_enabled, wave_amplitude, wave_frequency, wave_speed, wave_axis)
        is_hovered = is_hovered or hovered

    imgui.render()

    return is_thinning_enabled, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, show_wave_control, ds, dh, tinning_level, point_size, is_hovered, show_depth_scene, depth_range, depth_axis, wave_amplitude, wave_frequency, wave_axis, is_wave_enabled, wave_speed

# 主程序
def main():
    global custom_ply_path, original_points, original_colors

    if not glfw.init():
        return

    window = glfw.create_window(900, 600, "Point Cloud Fast Thinning (Based on Sample Point Spatial Neighborhood)", None, None)
    glfw.make_context_current(window)

    imgui.create_context()
    impl = GlfwRenderer(window)

    mouse_controller = MouseController()

    glfw.set_mouse_button_callback(window, mouse_controller.mouse_button_callback)
    glfw.set_cursor_pos_callback(window, mouse_controller.cursor_position_callback)
    glfw.set_scroll_callback(window, mouse_controller.scroll_callback)

    tinning_level = 1.0
    ds = 10.0
    dh = 10.0
    point_size = 1.0
    is_thinning_enabled = False
    points, colors = np.array([]), np.array([])

    show_point_clouds_tinning_control = True
    show_camera_control = False
    show_point_size_control = False
    show_wave_control = False

    show_depth_scene = False
    depth_range = 10.0
    depth_axis = 2
    wave_amplitude = 0.6
    wave_frequency = 0.6
    wave_axis = 0
    is_wave_enabled = False
    wave_speed = 0.1
    wave_phase = 0.0

    def simplify_callback(tinning_level):
        nonlocal points, colors
        if original_points is not None and original_colors is not None:
            points, colors = get_tinning_point_cloud(ds, dh, tinning_level, original_points, original_colors)
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

    last_time = time.time()
    fps = 0

    while not glfw.window_should_close(window):
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        fps = 1.0 / delta_time if delta_time > 0 else 0

        glfw.poll_events()
        impl.process_inputs()

        width, height = glfw.get_framebuffer_size(window)
        if width == 0 or height == 0:
            continue
        gl.glViewport(0, 0, width, height)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        io = imgui.get_io()
        io.display_size = (width, height)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, width / float(height), 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        glu.gluLookAt(mouse_controller.translation[0], mouse_controller.translation[1], 5 / mouse_controller.zoom, 
                      mouse_controller.translation[0], mouse_controller.translation[1], 0, 
                      0, 1, 0)
        gl.glRotatef(mouse_controller.rotation[0], 1, 0, 0)
        gl.glRotatef(-mouse_controller.rotation[1], 0, 1, 0)

        if is_thinning_enabled and original_points is not None and original_colors is not None:
            points, colors = get_tinning_point_cloud(ds, dh, tinning_level, original_points, original_colors)
        elif not is_thinning_enabled and original_points is not None and original_colors is not None:
            points, colors = original_points, original_colors

        if is_wave_enabled and points.size > 0:
            wave_phase = (wave_phase + wave_speed) % (2 * np.pi)
            points = apply_wave_effect(points, wave_amplitude, wave_frequency, wave_phase, wave_axis)

        if points.size > 0:
            gl.glPointSize(point_size)
            if show_depth_scene:
                render_depth_scene(points, depth_range, depth_axis)
            else:
                render_point_cloud_vbo(points, colors)
        else:
            draw_axes()

        is_thinning_enabled, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, show_wave_control, ds, dh, tinning_level, point_size, is_hovered, show_depth_scene, depth_range, depth_axis, wave_amplitude, wave_frequency, wave_axis, is_wave_enabled, wave_speed = imgui_interface(
            mouse_controller, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, 
            show_wave_control, is_thinning_enabled, ds, dh, tinning_level, point_size, simplify_callback, 
            load_ply_callback, show_depth_scene, depth_range, depth_axis, wave_amplitude, wave_frequency, 
            wave_axis, is_wave_enabled, wave_speed, fps)  # 传递fps
        impl.render(imgui.get_draw_data())

        mouse_controller.update(not is_hovered)

        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()
