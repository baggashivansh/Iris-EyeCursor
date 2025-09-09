import sys, math, random, time, json
from PyQt5 import QtWidgets, QtGui, QtCore
from Quartz import CGEventCreate, CGEventGetLocation  # Only what we need

CONFIG_FILE = "config.json"
ICON_PATH = "assets/iris_icon.png"


def get_global_mouse_pos():
    loc = CGEventGetLocation(CGEventCreate(None))
    return int(loc.x), int(loc.y)


class IrisTray(QtWidgets.QSystemTrayIcon):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # Eye parameters
        self.eye_size = 220
        self.eye_radius = 90
        self.pupil_radius = 38
        self.spacing = 60

        # State
        self.last_mouse_pos = get_global_mouse_pos()
        self.last_active_time = time.time()
        self.blink_left = self.blink_right = False
        self.next_blink_time = time.time() + random.randint(3, 8)

        # Config
        self.config = {"random_blink": True, "sleepy_mode": True, "refresh_rate": 25}
        self.load_config()

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_eye)
        self.timer.start(self.config["refresh_rate"])

        # Tray
        self.setup_tray_menu()
        self.setIcon(QtGui.QIcon(ICON_PATH))
        self.show()

    def setup_tray_menu(self):
        menu = QtWidgets.QMenu()
        menu.addAction("Quit", self.quit_app)
        self.setContextMenu(menu)

    def update_eye(self):
        mouseX, mouseY = get_global_mouse_pos()
        if (mouseX, mouseY) != self.last_mouse_pos:
            self.last_active_time = time.time()
        self.last_mouse_pos = (mouseX, mouseY)

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

        self.draw_eyes(mouseX, mouseY, sleepy)
        self.blink_left = self.blink_right = False

    def draw_eyes(self, mouseX, mouseY, sleepy=False):
        width = self.eye_size * 2 + self.spacing
        height = self.eye_size
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        centers = [
            (self.eye_size // 2, self.eye_size // 2),
            (self.eye_size + self.spacing + self.eye_size // 2, self.eye_size // 2),
        ]

        for i, center in enumerate(centers):
            blink = self.blink_left if i == 0 else self.blink_right
            self.draw_single_eye(painter, center, mouseX, mouseY, sleepy, blink)

        painter.end()
        self.setIcon(QtGui.QIcon(pixmap))

    def draw_single_eye(self, painter, center, mouseX, mouseY, sleepy, blink=False):
        cx, cy = center
        if blink:
            painter.setBrush(QtCore.Qt.black)
            painter.drawRect(cx - self.eye_radius, cy - 5, self.eye_radius * 2, 10)
            return

        # Eye background
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtCore.Qt.black)
        painter.drawEllipse(cx - self.eye_radius, cy - self.eye_radius, self.eye_radius * 2, self.eye_radius * 2)

        # Sleepy eyelid
        if sleepy:
            painter.setBrush(QtCore.Qt.gray)
            painter.drawEllipse(cx - self.eye_radius, cy - 4, self.eye_radius * 2, 10)
            return

        # Pupil position
        dx, dy = mouseX - cx, mouseY - cy
        distance = math.hypot(dx, dy)
        max_offset = self.eye_radius - self.pupil_radius
        if distance > max_offset:
            dx = dx / distance * max_offset
            dy = dy / distance * max_offset

        painter.setBrush(QtCore.Qt.black)
        painter.drawEllipse(cx - self.pupil_radius + int(dx),
                            cy - self.pupil_radius + int(dy),
                            self.pupil_radius * 2,
                            self.pupil_radius * 2)

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        except Exception:
            self.save_config()

    def quit_app(self):
        self.save_config()
        self.app.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tray = IrisTray(app)
    sys.exit(app.exec_())
