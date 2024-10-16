import imgui

def point_cloud_lod_control_interface(lod_level, max_lod_level, is_lod_enabled, is_auto_lod, update_lod_callback):
    is_hovered = False
    if imgui.begin("Point Cloud LOD Control", True):
        imgui.text("Adjust the Level of Detail (LOD) for the point cloud rendering.")

        # LOD Enable Checkbox
        changed, is_lod_enabled = imgui.checkbox("Enable LOD", is_lod_enabled)
        if changed:
            update_lod_callback(lod_level, is_lod_enabled)

        # Auto LOD Checkbox (only enabled if LOD is enabled)
        if is_lod_enabled:
            changed, is_auto_lod = imgui.checkbox("Auto LOD", is_auto_lod)
            if changed:
                update_lod_callback(lod_level, is_lod_enabled)

        # LOD Level Slider (only enabled if LOD is enabled and not auto)
        if is_lod_enabled and not is_auto_lod:
            changed, lod_level = imgui.slider_int(
                "LOD Level", lod_level, 0, max_lod_level, "LOD = %d"
            )
            if changed:
                update_lod_callback(lod_level, is_lod_enabled)

        is_hovered = imgui.is_window_hovered()
        imgui.end()
    return lod_level, is_lod_enabled, is_auto_lod, is_hovered