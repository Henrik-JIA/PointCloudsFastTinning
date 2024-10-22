import imgui
from interface.camera_control_interface import camera_control_interface
from interface.point_clouds_tinning_control_interface import point_clouds_tinning_control_interface
from interface.point_clouds_control_interface import point_clouds_control_interface
from interface.wave_control_interface import wave_control_interface
from interface.lod_control_interface import point_cloud_lod_control_interface

# ImGui 界面
def imgui_interface(mouse_controller, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, \
                    show_wave_control, show_lod_control, is_thinning_enabled, ds, dh, tinning_level, point_size, simplify_callback, \
                    load_ply_callback, show_depth_scene, depth_range, depth_axis, wave_amplitude, wave_frequency, wave_axis, \
                    is_wave_enabled, wave_speed, lod_level, max_lod_level, is_lod_enabled, is_export_lod_structure, export_lod_directory, update_lod_callback, fps, export_lod_callback):
    imgui.new_frame()

    is_hovered = False

    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("Window", True):
            clicked, show_point_clouds_tinning_control = imgui.menu_item("Show Point Cloud Tinning Controls", None, show_point_clouds_tinning_control, True)
            clicked, show_camera_control = imgui.menu_item("Show Camera Controls", None, show_camera_control, True)
            clicked, show_point_size_control = imgui.menu_item("Show Point Clouds Control", None, show_point_size_control, True)
            clicked, show_wave_control = imgui.menu_item("Show Wave Controls", None, show_wave_control, True)
            clicked, show_lod_control = imgui.menu_item("Show LOD Controls", None, show_lod_control, True)
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

    if show_lod_control:
        lod_level, is_lod_enabled, is_export_lod_structure, export_lod_directory, hovered = point_cloud_lod_control_interface(
            lod_level, max_lod_level, is_lod_enabled, is_export_lod_structure, export_lod_directory, update_lod_callback, export_lod_callback
        )
        is_hovered = is_hovered or hovered

    imgui.render()

    return is_thinning_enabled, show_point_clouds_tinning_control, show_camera_control, show_point_size_control, show_wave_control, show_lod_control, ds, dh, tinning_level, point_size, is_hovered, show_depth_scene, depth_range, depth_axis, wave_amplitude, wave_frequency, wave_axis, is_wave_enabled, wave_speed, lod_level, is_lod_enabled, is_export_lod_structure, export_lod_directory
