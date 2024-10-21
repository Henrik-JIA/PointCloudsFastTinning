import imgui
import tkinter as tk
from tkinter import filedialog
import os

def point_cloud_lod_control_interface(lod_level, max_lod_level, is_lod_enabled, is_export_lod_structure, export_lod_directory, update_lod_callback, export_lod_callback):
    is_hovered = False

    if imgui.begin("Point Cloud LOD Control", True):
        imgui.text("Adjust the Level of Detail (LOD) for the point cloud rendering.")

        # LOD Enable Checkbox
        changed, is_lod_enabled = imgui.checkbox("Enable LOD", is_lod_enabled)
        if changed:
            update_lod_callback(lod_level, is_lod_enabled)

        # LOD Level Slider (only enabled if LOD is enabled)
        if is_lod_enabled:
            changed, lod_level = imgui.slider_int(
                "LOD Level", lod_level, 0, max_lod_level, "LOD = %d"
            )
            if changed:
                update_lod_callback(lod_level, is_lod_enabled)

        # Export LOD Structure Checkbox
        changed, is_export_lod_structure = imgui.checkbox("Export LOD Structure", is_export_lod_structure)
        if not is_export_lod_structure:
            export_lod_directory = ""  # 清空文本框内容
        else:
            # Directory selection
            if imgui.button("Browse"):
                root = tk.Tk()
                root.withdraw()
                selected_directory = filedialog.askdirectory(title="Select Export Directory")
                if selected_directory:
                    export_lod_directory = selected_directory
                root.destroy()

            imgui.same_line()
            # 使用输入框显示和编辑导出目录
            buffer_size = 256
            export_lod_directory = imgui.input_text("##export_directory", export_lod_directory, buffer_size)[1]

            # Export button
            if imgui.button("Export"):
                if export_lod_directory:
                    export_lod_callback(export_lod_directory, lod_level)
                else:
                    imgui.text("Please select a directory first.")

        is_hovered = imgui.is_window_hovered()
        imgui.end()
    return lod_level, is_lod_enabled, is_export_lod_structure, export_lod_directory, is_hovered