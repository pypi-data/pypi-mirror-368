from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtGui import QIcon



class Messages(QWidget):
    def __init__(self, title, mssg):
        self.title = title
        self.mssg = mssg
        super().__init__()

        self.setGeometry(80, 280, 500, 150)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("mssg_win")

        self.message_label = QLabel(self)
        self.message_label.setWordWrap(True)
        self.message_label.setText(self.mssg)
        self.message_label.move(10, 10)

        self.close_mss_button = QPushButton("OK", self)
        self.close_mss_button.move(200, 80)
        self.close_mss_button.clicked.connect(lambda: self.close())
