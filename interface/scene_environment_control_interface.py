import imgui

def scene_environment_control_interface(background_color):
    is_hovered = False
    if imgui.begin("Scene Environment Control", True):
        imgui.text("Adjust the scene environment settings:")
        
        # 使用颜色编辑器来调整背景颜色
        changed, background_color = imgui.color_edit3("Background Color", *background_color)
        
        is_hovered = imgui.is_window_hovered()
        imgui.end()
    return background_color, is_hovered