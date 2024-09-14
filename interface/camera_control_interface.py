import imgui

def camera_control_interface(mouse_controller):
    is_hovered = False
    if imgui.begin("Camera Control", True):
        if imgui.button(label='rot 180'):
            mouse_controller.rotation[0] += 180
        
        imgui.same_line()
        if imgui.button(label="Reset Position"):
            mouse_controller.reset_position()

        imgui.push_item_width(150)

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

        imgui.pop_item_width()

        is_hovered = imgui.is_window_hovered()
        imgui.end()
    return is_hovered