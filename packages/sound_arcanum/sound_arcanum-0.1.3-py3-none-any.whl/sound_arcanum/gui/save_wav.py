import os
import time

import scipy.io.wavfile as wf
from numpy import int16
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QListWidget,
    QSlider,
    QVBoxLayout,
    QLineEdit,
)
from PyQt5.QtGui import QIcon

import messages_from_dead


class SaveWavDialog(QWidget):
    def __init__(self, notes, sample_rate):
        self.notes = notes
        self.sample_rate = sample_rate
        super().__init__()

        def save_stuff():
            print(str(self.sample_rate))
            self.dir_name = self.dirname_entry.text()
            if len(self.dir_name) == 0:
                self.dir_name = "./audio{}-{}Hz".format(time.strftime("%d-%m-%Y-%H-%M-%S", time.gmtime()), self.sample_rate)
            try:
                os.mkdir(self.dir_name)
            except FileExistsError:
                mssg = messages_from_dead.Messages(
                    "FileExistsError",
                    "Aborted. Directory already exists."
                )
                mssg.show()
                return
            else:
                for e, i in enumerate(self.notes, start=1):
                    if len(str(e)) < 2:
                        i = int16(i * 32767)
                        wf.write(f"{self.dir_name}/a0{e}.wav", self.sample_rate, i)
                    else:
                        i = int16(i * 32767)
                        wf.write(f"{self.dir_name}/a{e}.wav", self.sample_rate, i)
                
                mssg = messages_from_dead.Messages(
                    "Saved",
                    f"Wav files saved in directory: {self.dir_name}"
                )
                mssg.show()
                self.close()

        self.setGeometry(200, 500, 600, 200)
        self.setWindowTitle("Save Wav Files")
        self.setWindowIcon(QIcon('imags/knotperfect-icon.png'))
        self.setObjectName("preset_win")

        self.save_label = QLabel(self)
        self.save_label.setText("Directory Name")
        self.save_label.move(20, 10)

        self.dirname_entry = QLineEdit(self)
        self.dirname_entry.setMaxLength(32)
        self.dirname_entry.move(20, 50)
        self.dirname_entry.resize(280, 40)

        self.button = QPushButton("Save", self)
        self.button.move(220, 110)

        self.button.clicked.connect(save_stuff)

        self.close_button = QPushButton("Close", self)
        self.close_button.setMinimuWidth(130)
        self.close_button.move(400, 140)
        self.close_button.clicked.connect(lambda: self.close())
        