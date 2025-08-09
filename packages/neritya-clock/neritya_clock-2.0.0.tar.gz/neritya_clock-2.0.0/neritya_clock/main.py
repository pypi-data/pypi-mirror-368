import sys, os, re
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QStackedLayout
from PySide6.QtCore import Qt, QTimer, QTime, QVariantAnimation, QAbstractAnimation
from PySide6.QtGui import QColor, QPainter, QFontDatabase, QFont
from .resources import get_font_path

# === SETTINGS ===
FONT_PATH = get_font_path("FFFFORWA.TTF")
TIME_FONT_PATH = get_font_path("Gameshow.ttf")
BACKGROUND = QColor("black")
DEFAULT_TEXT_COLOR = QColor("#00FF00")
BASE_FONT_SCALE = 0.40
LETTER_SPACING = 0
DOT_FONT_SIZE = 50
SAVE_FILE = os.path.expanduser("~/.neritya_clock_color.txt")
hex_regex = re.compile(r"^#([0-9A-Fa-f]{6})$")


class ClockWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.text_color = self.load_saved_color()
        self.input_triggered = False
        self.special_mode = False

        # Load fonts
        time_font_id = QFontDatabase.addApplicationFont(TIME_FONT_PATH)
        self.time_font_family = QFontDatabase.applicationFontFamilies(time_font_id)[0] if time_font_id != -1 else "Courier"

        font_id = QFontDatabase.addApplicationFont(FONT_PATH)
        self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Courier"

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.clock_label = QLabel(alignment=Qt.AlignCenter)
        self.clock_label.setSizePolicy(self.clock_label.sizePolicy().horizontalPolicy(), self.clock_label.sizePolicy().verticalPolicy())
        self.main_layout.addWidget(self.clock_label, stretch=10, alignment=Qt.AlignCenter)

        self.bottom_widget = QWidget()
        self.bottom_widget.setContentsMargins(0, 0, 0, 20)
        self.stack = QStackedLayout(self.bottom_widget)
        self.stack.setAlignment(Qt.AlignCenter)

        self.dot_label = QLabel("...", alignment=Qt.AlignCenter)
        self.input_label = QLabel("#", alignment=Qt.AlignCenter)
        self.input_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.stack.addWidget(self.dot_label)
        self.stack.addWidget(self.input_label)

        self.main_layout.addWidget(self.bottom_widget, alignment=Qt.AlignCenter, stretch=1)

        screen = QApplication.primaryScreen()
        size = screen.size()
        self.dynamic_font_size = int(size.height() * BASE_FONT_SCALE)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        self.dot_label.mousePressEvent = lambda e: self.morph_to_input()

        self.showFullScreen()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.update_colors()

    def update_colors(self):
        self.clock_label.setStyleSheet(f"color:{self.text_color.name()}")
        font = QFont(self.font_family, DOT_FONT_SIZE)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        self.dot_label.setFont(font)
        self.dot_label.setStyleSheet(f"color:{self.text_color.name()}")
        self.input_label.setFont(font)
        self.input_label.setStyleSheet(f"color:{self.text_color.name()}; background:{BACKGROUND.name()}")

    def update_time(self):
        self.clock_label.setText(QTime.currentTime().toString("HH:mm"))
        font = QFont(self.time_font_family, self.dynamic_font_size)
        font.setLetterSpacing(QFont.AbsoluteSpacing, LETTER_SPACING)
        font.setWeight(QFont.Bold)
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        self.clock_label.setFont(font)

    def morph_to_input(self):
        self.stack.setCurrentIndex(1)
        self.input_text = "#"
        self.input_label.setText("#|")
        self.grabKeyboard()

    def keyPressEvent(self, e):
        key = e.key()
        ch = e.text()

        if key == Qt.Key_Escape:
            self.close()
            return

        if self.special_mode:
            self.back_to_dots()
            return

        if not self.input_triggered:
            self.morph_to_input()
            self.input_triggered = True
            return

        if self.stack.currentIndex() == 1:
            if key in (Qt.Key_Shift, Qt.Key_CapsLock):
                return

            if key in (Qt.Key_Return, Qt.Key_Enter):
                self.apply_hex_change()
                return

            if key == Qt.Key_Backspace:
                if len(self.input_text) > 1:
                    self.input_text = self.input_text[:-1]
                    self.input_label.setText(self.input_text + "|")
                else:
                    self.back_to_dots()
                return

            if ch and len(self.input_text) < 7:
                self.input_text += ch
                if self.input_text.lower() == "#coder":
                    self.input_label.setText("#neritya")
                    self.special_mode = True
                else:
                    if len(self.input_text) >= 7:
                        self.input_label.setText(self.input_text)
                    else:
                        self.input_label.setText(self.input_text + "|")

    def apply_hex_change(self):
        text = self.input_text.strip()

        if text.lower() == "#coder":
            self.input_label.setText("#neritya")
            self.special_mode = True
            return

        if len(text) == 7 and hex_regex.match(text):
            new_color = QColor(text)
            if new_color != BACKGROUND:
                self.fade_color_change(new_color)
                self.save_color(text)

        self.back_to_dots()

    def fade_color_change(self, new_color):
        if hasattr(self, 'anim') and self.anim.state() == QAbstractAnimation.Running:
            self.anim.stop()

        self.anim = QVariantAnimation(
            startValue=self.text_color,
            endValue=new_color,
            duration=500
        )
        self.anim.valueChanged.connect(lambda c: self.set_text_color(c))
        self.anim.finished.connect(self.update_colors)
        self.anim.start()

    def set_text_color(self, color):
        self.text_color = color
        self.update_colors()

    def back_to_dots(self):
        self.stack.setCurrentIndex(0)
        self.releaseKeyboard()
        self.input_triggered = False
        self.special_mode = False

    def paintEvent(self, e):
        QPainter(self).fillRect(self.rect(), BACKGROUND)
        super().paintEvent(e)

    def save_color(self, hex_code):
        try:
            with open(SAVE_FILE, "w") as f:
                f.write(hex_code)
        except Exception as e:
            print(f"Failed to save color: {e}")

    def load_saved_color(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    hex_code = f.read().strip()
                    if hex_regex.match(hex_code):
                        return QColor(hex_code)
            except Exception:
                pass
        return DEFAULT_TEXT_COLOR


def main():
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    app = QApplication(sys.argv)
    window = ClockWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
