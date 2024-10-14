import imgui

def point_clouds_tinning_control_interface(is_thinning_enabled, ds, dh, tinning_level, simplify_callback, load_ply_callback, fps):
    is_hovered = False
    if imgui.begin("Point Cloud Tinning Controls", True):
        # 显示FPS
        imgui.text(f"FPS: {fps:.1f}")

        imgui.text("Adjust point cloud settings:")

        _, is_thinning_enabled = imgui.checkbox("Enable Thinning", is_thinning_enabled)
        
        imgui.push_item_width(150)
        
        changed_ds, ds = imgui.slider_float("Distance Threshold (ds)", ds, 0.1, 100.0)
        changed_dh, dh = imgui.slider_float("Height Threshold (dh)", dh, 0.1, 100.0)
        changed_lod, tinning_level = imgui.slider_float("Tinning Level", tinning_level, 0.001, 1.0)
        
        imgui.pop_item_width()

        if imgui.button("Load PLY File"):
            load_ply_callback()
        
        if imgui.button("Save Simplified Point Cloud"):
            if is_thinning_enabled:
                simplify_callback(tinning_level)

        is_hovered = imgui.is_window_hovered()
        imgui.end()
    return is_thinning_enabled, ds, dh, tinning_level, is_hovered
