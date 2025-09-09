import sys, math, random, time, json
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QCursor


class IrisTray(QtWidgets.QSystemTrayIcon):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # Config
        self.config = {
            "random_blink": True,
            "sleepy_mode": True,
            "refresh_rate": 25  # 40 FPS
        }
        self.load_config()

        # Eye parameters (Bigger eyes & faster pupils)
        self.eye_size = 160
        self.eye_radius = 65
        self.pupil_radius = 28
        self.spacing = 40

        # Cursor & timing
        self.last_mouse_pos = QCursor.pos()
        self.last_active_time = time.time()
        self.blink_left = False
        self.blink_right = False
        self.next_blink_time = time.time() + random.randint(3, 8)

        # Smooth pupil movement (faster now)
        self.pupil_left_dx = 0
        self.pupil_left_dy = 0
        self.pupil_right_dx = 0
        self.pupil_right_dy = 0
        self.smooth_speed = 0.45  # was 0.2 → now more responsive

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_eye)
        self.timer.start(self.config["refresh_rate"])

        # Tray menu
        self.setup_tray_menu()
        self.activated.connect(self.handle_click)

        # --- Icon for Tray ---
        self.setIcon(QtGui.QIcon("assets/iris_icon.png"))  # use your icon file
        self.show()

    # --- Tray Menu ---
    def setup_tray_menu(self):
        self.menu = QtWidgets.QMenu()
        self.pref_menu = self.menu.addMenu("Preferences")

        self.blink_action = QtWidgets.QAction("Random Blink", self, checkable=True)
        self.blink_action.setChecked(self.config["random_blink"])
        self.blink_action.triggered.connect(self.toggle_random_blink)
        self.pref_menu.addAction(self.blink_action)

        self.sleepy_action = QtWidgets.QAction("Sleepy Mode", self, checkable=True)
        self.sleepy_action.setChecked(self.config["sleepy_mode"])
        self.sleepy_action.triggered.connect(self.toggle_sleepy_mode)
        self.pref_menu.addAction(self.sleepy_action)

        self.pref_menu.addSeparator()
        self.speed_menu = self.pref_menu.addMenu("Refresh Speed")
        for label, val in [("Slow", 200), ("Normal", 50), ("Fast", 25)]:
            action = QtWidgets.QAction(label, self, checkable=True)
            if val == self.config["refresh_rate"]:
                action.setChecked(True)
            action.triggered.connect(lambda checked, v=val: self.set_refresh_rate(v))
            self.speed_menu.addAction(action)

        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        self.menu.addSeparator()
        self.setContextMenu(self.menu)

    # --- Event Handlers ---
    def handle_click(self, reason):
        if reason == self.Trigger:
            self.blink_left = True
        elif reason == self.Context:
            self.blink_right = True
        elif reason == self.DoubleClick:
            self.roll_eyes()

    # --- Update Loop ---
    def update_eye(self):
        mouse_pos = QCursor.pos()
        if mouse_pos != self.last_mouse_pos:
            self.last_active_time = time.time()
        self.last_mouse_pos = mouse_pos

        # Random blink
        if self.config["random_blink"] and time.time() >= self.next_blink_time:
            if random.choice([True, False]):
                self.blink_left = True
            else:
                self.blink_right = True
            self.next_blink_time = time.time() + random.randint(3, 8)

        # Sleepy mode
        idle = time.time() - self.last_active_time
        sleepy = self.config["sleepy_mode"] and idle > 10

        # Draw eyes
        self.draw_eyes(mouse_pos.x(), mouse_pos.y(), sleepy)

        # Reset blink flags
        self.blink_left = self.blink_right = False

    # --- Drawing ---
    def draw_eyes(self, mouseX, mouseY, sleepy=False, roll_angle=None):
        width = self.eye_size * 2 + self.spacing
        height = self.eye_size
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        left_center = (self.eye_size // 2, self.eye_size // 2)
        right_center = (self.eye_size + self.spacing + self.eye_size // 2, self.eye_size // 2)

        self.draw_single_eye(painter, left_center, mouseX, mouseY, sleepy,
                             blink=self.blink_left, smooth_dxdy=(self.pupil_left_dx, self.pupil_left_dy))
        self.draw_single_eye(painter, right_center, mouseX, mouseY, sleepy,
                             blink=self.blink_right, smooth_dxdy=(self.pupil_right_dx, self.pupil_right_dy))

        painter.end()
        self.setIcon(QtGui.QIcon(pixmap))

    def draw_single_eye(self, painter, center, mouseX, mouseY, sleepy, blink=False, smooth_dxdy=(0, 0)):
        cx, cy = center

        # Blink
        if blink:
            painter.setBrush(QtCore.Qt.black)
            painter.drawRect(cx - self.eye_radius, cy - 5, self.eye_radius * 2, 10)
            return

        # Eye white
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtCore.Qt.black)
        painter.drawEllipse(cx - self.eye_radius, cy - self.eye_radius,
                            self.eye_radius * 2, self.eye_radius * 2)

        # Sleepy
        if sleepy:
            painter.setBrush(QtCore.Qt.gray)
            painter.drawEllipse(cx - self.eye_radius, cy - 4, self.eye_radius * 2, 10)
            return

        # --- Edge-safe pupil calculation ---
        screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
        screen_w, screen_h = screen_geometry.width(), screen_geometry.height()

        mouseX = max(0, min(mouseX, screen_w))
        mouseY = max(0, min(mouseY, screen_h))

        dx = mouseX - cx
        dy = mouseY - cy
        distance = math.hypot(dx, dy)

        max_offset = self.eye_radius - self.pupil_radius
        if distance > max_offset:
            dx = dx / distance * max_offset
            dy = dy / distance * max_offset

        # Smooth interpolation
        smooth_dx, smooth_dy = smooth_dxdy
        smooth_dx += (dx - smooth_dx) * self.smooth_speed
        smooth_dy += (dy - smooth_dy) * self.smooth_speed

        # Save smooth positions
        if center[0] < self.eye_size:  # left eye
            self.pupil_left_dx, self.pupil_left_dy = smooth_dx, smooth_dy
        else:  # right eye
            self.pupil_right_dx, self.pupil_right_dy = smooth_dx, smooth_dy

        # Draw pupil
        painter.setBrush(QtCore.Qt.black)
        painter.drawEllipse(cx - self.pupil_radius + int(smooth_dx),
                            cy - self.pupil_radius + int(smooth_dy),
                            self.pupil_radius * 2,
                            self.pupil_radius * 2)

    # --- Eye Rolling ---
    def roll_eyes(self):
        for i in range(0, 360, 30):
            angle = math.radians(i)
            self.draw_eyes(QCursor.pos().x(), QCursor.pos().y(), roll_angle=angle)
            QtWidgets.QApplication.processEvents()
            QtCore.QThread.msleep(25)

    # --- Preferences ---
    def toggle_random_blink(self, checked):
        self.config["random_blink"] = checked
        self.save_config()

    def toggle_sleepy_mode(self, checked):
        self.config["sleepy_mode"] = checked
        self.save_config()

    def set_refresh_rate(self, value):
        self.config["refresh_rate"] = value
        self.timer.setInterval(value)
        self.save_config()

    # --- Config ---
    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_config()

    def quit_app(self):
        self.save_config()
        self.app.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tray = IrisTray(app)
    sys.exit(app.exec_())
