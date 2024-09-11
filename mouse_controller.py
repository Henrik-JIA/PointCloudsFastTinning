import glfw

class MouseController:
    def __init__(self):
        self.rotation = [0, 0]
        self.zoom = 1.0
        self.last_mouse_pos = [0, 0]
        self.left_mouse_pressed = False
        self.right_mouse_pressed = False
        self.translation = [0, 0]
        self.enabled = True  # 添加一个标志来控制鼠标输入是否启用

    def mouse_button_callback(self, window, button, action, mods):
        if not self.enabled:
            return
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.left_mouse_pressed = True
            elif action == glfw.RELEASE:
                self.left_mouse_pressed = False
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.right_mouse_pressed = True
            elif action == glfw.RELEASE:
                self.right_mouse_pressed = False

    def cursor_position_callback(self, window, xpos, ypos):
        if not self.enabled:
            return
        if self.left_mouse_pressed:
            dx = xpos - self.last_mouse_pos[0]
            dy = ypos - self.last_mouse_pos[1]
            self.rotation[0] += dy * 0.5
            self.rotation[1] += dx * 0.5
        elif self.right_mouse_pressed:
            dx = xpos - self.last_mouse_pos[0]
            dy = ypos - self.last_mouse_pos[1]
            self.translation[0] -= dx * 0.01  # 调整平移方向
            self.translation[1] += dy * 0.01  # 调整平移方向
        self.last_mouse_pos = [xpos, ypos]

    def scroll_callback(self, window, xoffset, yoffset):
        if not self.enabled:
            return
        self.zoom += yoffset * 0.1
        self.zoom = max(0.1, min(self.zoom, 10.0))

    def update(self, enabled):
        self.enabled = enabled