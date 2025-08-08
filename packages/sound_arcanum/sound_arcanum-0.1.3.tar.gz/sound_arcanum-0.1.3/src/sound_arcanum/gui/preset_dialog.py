import os
import pickle
import time

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


class PresetSaveDialog(QWidget):
    def __init__(self, setting_list):
        self.settings_list = setting_list
        super().__init__()

        def save_stuff():
            stamp = self.filename_entry.text()
            if len(stamp) == 0:
                stamp = "Presets-{}.pickle".format(
                    str(time.ctime()[-16:].replace(" ", "-").replace(":", "-")
                ))
            else:
                stamp = f"{stamp}.pickle"
            
            with open(f"presets/{stamp}", "wb+") as fp:
                pickle.dump(self.settings_list, fp)
            
            self.close()

        self.setGeometry(200, 500, 600, 200)
        self.setWindowTitle("Save Presets")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("preset_win")

        self.save_label = QLabel(self)
        self.save_label.setText("Give Presets a Filename")
        self.save_label.move(20, 10)

        self.filename_entry = QLineEdit(self)
        self.filename_entry.setMaxLength(32)
        self.filename_entry.move(20, 50)
        self.filename_entry.resize(280, 40)

        self.button = QPushButton('Save', self)
        self.button.move(220, 110)

        self.button.clicked.connect(save_stuff)

        self.close_button = QPushButton("Close", self)
        self.close_button.setMinimumWidth(130)
        self.close_button.move(400, 140)
        self.close_button.clicked.connect(lambda: self.close())


class PresetRecallDialog(QWidget):
    def __init__(self, all_that, is_midi):
        self.all_that = all_that
        self.is_midi = is_midi
        super().__init__()

        self.setGeometry(100, 520, 600, 200)
        self.setWindowTitle("Recall Preset File")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("p_recall_win")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.listWidget = QListWidget()
        for n, f in enumerate(os.listdir("./presets")):
            self.listWidget.insertItem(n, f)
        self.listWidget.clicked.connect(self.clicked)
        layout.addWidget(self.listWidget)

        self.info_label = QLabel(self)
        self.info_label.setText("Select file and click the Apply Settings button back on the main window.")
        layout.addWidget(self.info_label)

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(lambda: self.close())
        layout.addWidget(self.close_button)

    def clicked(self, qmodelindex):
        pickle_item = self.listWidget.currentItem().text()
        try:
            with open(f"./presets/{pickle_item}", "rb") as fp:
                preset_values = pickle.load(fp)
            
            self.all_that.duration_slider.setValue(preset_values[0])
            self.all_that.detune_slider.setValue(preset_values[1])
            self.all_that.octave_slider.setValue(preset_values[2])
            self.all_that.ramp_slider.setValue(preset_values[3])
            self.all_that.delay_slider.setValue(preset_values[4])
            self.all_that.shape_slider.setValue(preset_values[5])
            self.all_that.volume_slider.setValue(preset_values[6])
            self.all_that.attack_slider.setValue(preset_values[7])
            self.all_that.fade_slider.setValue(preset_values[8])
            if self.is_midi[0] is False:
                self.all_that.key_change_bool[0] = preset_values[9]
                if self.all_that.key_change_bool[0] is True:
                    self.all_that.key_button.setText('C4')
                else:
                    self.all_that.key_button.setText('E4')
        
        except Exception as err:
            print(f"{type(e).__name__}: {str(e)}")
        self.close()

        