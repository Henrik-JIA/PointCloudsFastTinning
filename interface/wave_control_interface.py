import imgui

def wave_control_interface(is_wave_enabled, wave_amplitude, wave_frequency, wave_speed, wave_axis):
    is_hovered = False
    if imgui.begin("Wave Controls", True):
        imgui.text("Adjust wave effect settings:")

        _, is_wave_enabled = imgui.checkbox("Enable Wave Effect", is_wave_enabled)
        
        imgui.push_item_width(150)
        
        changed_wave_amplitude, wave_amplitude = imgui.slider_float("Wave Amplitude", wave_amplitude, 0.0, 10.0, "amplitude = %.1f")
        changed_wave_frequency, wave_frequency = imgui.slider_float("Wave Frequency", wave_frequency, 0.0, 10.0, "frequency = %.1f")
        changed_wave_speed, wave_speed = imgui.slider_float("Wave Speed", wave_speed, 0.0, 1.0, "speed = %.2f")
        wave_axis_labels = ["X-Axis", "Y-Axis", "Z-Axis"]
        changed_wave_axis, wave_axis = imgui.combo("Wave Axis", wave_axis, wave_axis_labels)
        imgui.pop_item_width()

        is_hovered = imgui.is_window_hovered()
        imgui.end()
    return is_wave_enabled, wave_amplitude, wave_frequency, wave_speed, wave_axis, is_hovered