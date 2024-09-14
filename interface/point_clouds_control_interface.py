import imgui

def point_clouds_control_interface(point_size, show_depth_scene, depth_range, depth_axis):
    is_hovered = False
    if imgui.begin("Point Clouds Control", True):
        imgui.push_item_width(150)
        changed_point_size, point_size = imgui.slider_float("Point Size", point_size, 1.0, 10.0, "size = %.1f")
        imgui.pop_item_width()

        _, show_depth_scene = imgui.checkbox("Show Depth Scene", show_depth_scene)
        
        depth_axis_labels = ["X-Axis", "Y-Axis", "Z-Axis"]
        changed_depth_axis, depth_axis = imgui.combo("Depth Axis", depth_axis, depth_axis_labels)
        
        changed_depth_range, depth_range = imgui.slider_float("Depth Range", depth_range, 0.1, 100.0, "range = %.1f")

        is_hovered = imgui.is_window_hovered()
        imgui.end()
    return point_size, show_depth_scene, depth_range, depth_axis, is_hovered