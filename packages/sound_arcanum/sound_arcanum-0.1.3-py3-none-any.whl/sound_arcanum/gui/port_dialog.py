import mido

from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QListWidget,
    QLabel,
    QVBoxLayout,
)
from PyQt5.QtGui import QIcon


class ChoosePort(QWidget):
    def __init__(self, midi_on_flag, activate_midi, applying_sliders_flag):
        self.midi_on_flag = midi_on_flag
        self.applying_sliders_flag = applying_sliders_flag
        self.activate_midi = activate_midi
        super().__init__()

        midi_input_names = mido.get_input_names()
        self.setGeometry(100, 520, 600, 200)
        self.setWindowTitle("Choose Midi Input")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("midi_win")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.listWidget = QListWidget()
        for i, s in enumerate(midi_input_names):
            self.listWidget.insertItem(i, s)
        self.listWidget.clicked.connect(self.clicked)
        layout.addWidget(self.listWidget)

        self.info_label = QLabel(self)
        self.info_label.setText(
            """
Select port, Apply settings in main window and wait a few seconds.
Port will be open until program is closed.
            """
        )
        layout.addWidget(self.info_label)

        self.close_kp_button = QPushButton('Close', self)
        self.close_kp_button.move(400, 140)
        self.close_kp_button.clicked.connect(lambda: self.close())
        layout.addWidget(self.close_kp_button)

    def clicked(self, qmodelindex):
        self.midi_on_flag[0] = True
        self.applying_sliders_flag[0] = True
        self.item = self.listWidget.currentItem().text()
        self.activate_midi(self.item)
        self.close()

        
