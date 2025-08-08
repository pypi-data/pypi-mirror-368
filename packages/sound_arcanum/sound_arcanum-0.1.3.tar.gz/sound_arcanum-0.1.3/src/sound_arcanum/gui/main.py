import os
import pickle
import sys
import time
import threading

import mido
import numpy as np
import sounddevice as sd

from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    qApp,
    QApplication,
    QFrame,
    QListWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QSlider,
    QVBoxLayout,
    QShortcut,
)
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import pyqtSlot

import port_dialog
import preset_dialog
import messages_from_dead
import save_wav


class SliderFrame(QFrame):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        global do_it

        def do_it():

            def sine_wave(f, detune=0.0):
                y = np.sin((f + detune) * self.x + ramp_0 *
                           np.sin(((f + detune) * 0.5) * self.x + (np.sin(((f + detune) * fm) * self.x) * 0.5)))
                return y
            
            def triangle(f, detune=0.0):
                y = 2 / np.pi * np.arcsin(np.sin((f + detune) * self.x + ramp_0 * 
                                                 np.sin(((f + detune) * 0.5) * self.x + (np.sin((f + detune) * fm) * self.x) * 0.5)))
                return y * 0.8
            
            applying_sliders_flag[0] = True
            self.label_apply.hide()
            fm = 0.25
            freq3 = 440.0
            detune_freq = self.detune_slider.value() / 10
            self.duration = self.duration_slider.value() / 10
            self.octave_freq = (2 ** self.octave_slider.value()) * 220
            ramp_amount = self.ramp_slider.value() / 100
            roll_amount = self.delay_slider.value() 
            st = self.shape_slider.value() / 20
            volume = self.volume_slider.value() / 200
            tm = st * 1.2
            sm = 1 - st
            attack_size = self.attack_slider.value() / 100
            fade_size = self.fade_slider.value() / 100
            if midi_on_flag[0] is True:
                num_range = midi_range
                keys[:] = note_nums[:]
            else:
                if self.key_change_bool[0] is True:
                    num_range = c_range
                else:
                    num_range = e_range

            self.x = np.linspace(0, 2 * np.pi * self.duration, int(self.duration * new_samplerate[0]))
            ramp_0 = np.logspace(1, 0, np.size(self.x), base=10) * ramp_amount
            fade_size = int(np.size(self.x) * fade_size)
            attack = np.linspace(0, 1, int(np.size(self.x) * attack_size))
            fade = np.linspace(1, 0, fade_size if fade_size >= 1 else 1)

            self.notes = []
            for i in num_range:
                factor = 2 ** (1.0 * i / 12.0)
                waveform_mod = (sine_wave(self.octave_freq * factor) * sm) + (triangle(freq3 * factor, detune_freq) * tm)
                waveform = (
                    sine_wave(self.octave_freq * factor) * sm
                ) + (triangle(freq3 * factor) * tm)
                waveform_detune = (sine_wave(
                    self.octave_freq * factor, detune_freq
                ) * sm) + (triangle(freq3 * factor, detune_freq) * tm)

                waveform = ((waveform + waveform_detune) * (waveform_mod / 2 + 0.5))

                waveform = (waveform / np.max(np.abs(waveform))) * volume

                waveform[:np.size(attack)] *= attack
                waveform[-np.size(fade):] *= fade
                waveform2 = np.roll(waveform, roll_amount, axis=None)
                waveform3 = np.vstack((waveform2, waveform)).T

                self.notes.append(waveform3)

            global key_notes
            key_notes = dict(zip(keys, self.notes))
            applying_sliders_flag[0] = False
            return key_notes
        
        def changed_duration():
            val = self.duration_slider.value() * 0.1
            self.duration_val_label.setText(str('{:2.1f}'.format(val)))
            self.duration_val_label.adjustSize()
            show_apply()

        def changed_detune():
            val = self.detune_slider.value() * 0.1
            self.detune_val_label.setText(str('{:2.1f}'.format(val)))
            self.detune_val_label.adjustSize()
            show_apply()

        def changed_octave():
            val = (2 ** self.octave_slider.value()) * 220
            self.octave_val_label.setText(str(val))
            self.octave_val_label.adjustSize()
            show_apply()

        def changed_ramp():
            val = self.ramp_slider.value() * 0.01
            self.ramp_val_label.setText(str('{:3.2f}'.format(val)))
            self.ramp_val_label.adjustSize()
            show_apply()

        def changed_roll():
            val = self.delay_slider.value()
            self.delay_val_label.setText(str('{:4.3f}\nSeconds'.format(val / 48000)))
            self.delay_val_label.adjustSize()
            show_apply()

        def changed_attack():
            val = self.attack_slider.value() * 0.01
            self.attack_val_label.setText(str('{:3.2f}'.format(val)))
            self.attack_val_label.adjustSize()
            show_apply()

        def changed_fade():
            val = self.fade_slider.value() * 0.01
            # self.fade_val_label.setText('{:3.2f}'.format(val))
            self.fade_val_label.setText(str('{:3.2f}'.format(val)))
            self.fade_val_label.adjustSize()
            show_apply()

        def changed_vol():
            val = self.volume_slider.value() * 0.01
            self.vol_val_label.setText(str("{:3.2f}".format(val)))
            self.vol_val_label.adjustSize()
            show_apply()

        def show_apply():
            self.label_apply.show()

        def change_key():
            if midi_on_flag[0] is True:
                return
            else:
                self.key_change_bool[0] = not self.key_change_bool[0]
                if self.key_change_bool[0] is True:
                    keys[:] = c_keys[:]
                    self.key_button.setText('C4')
                else:
                    keys[:] = e_keys[:]
                    self.key_button.setText('E4')
                do_it()

        keys[:] = e_keys[:]
        c_range = range(-9, 9)
        e_range = range(-5, 13)
        self.key_change_bool = [False]

        self.shortcut_apply = QShortcut(QKeySequence('Ctrl+A'), self)
        self.shortcut_apply.activated.connect(do_it)

        self.apply_button = QPushButton('Apply Settings', self)
        self.apply_button.setStatusTip("Apply any changes made to sliders.")
        self.apply_button.move(10, 10)
        self.apply_button.clicked.connect(do_it)

        self.change_key_label = QLabel(self)
        self.change_key_label.setText("Change Key")
        self.change_key_label.move(10, 300)

        self.key_button = QPushButton("E4", self)
        self.key_button.move(115, 295)
        self.key_button.clicked.connect(change_key)

        self.shortcut_key = QShortcut(QKeySequence('Ctrl+K'), self)
        self.shortcut_key.activated.connect(change_key)

        close_button = QPushButton('Close', self)
        close_button.move(10, 390)
        close_button.clicked.connect(close)

        self.duration_label = QLabel(self)
        self.duration_label.setText('Duration')
        self.duration_label.move(10, 50)

        self.set0 = 10
        self.duration_slider = QSlider(Qt.Horizontal, self)
        self.duration_slider.setMinimumWidth(200)
        self.duration_slider.setMinimum(0)
        self.duration_slider.setMaximum(50)
        self.duration_slider.setValue(self.set0)
        self.duration_slider.setSingleStep(2)
        self.duration_slider.move(80, 50)
        self.duration_slider.valueChanged.connect(changed_duration)

        self.duration_val_label = QLabel(self)
        self.duration_val_label.setText(str(self.set0 * 0.1))
        self.duration_val_label.move(290, 50)

        self.detune_label = QLabel(self)
        self.detune_label.setText('Detune')
        self.detune_label.move(10, 90)

        self.set1 = 20
        self.detune_slider = QSlider(Qt.Horizontal, self)
        self.detune_slider.setMinimumWidth(200)
        self.detune_slider.setMinimum(0)
        self.detune_slider.setMaximum(130)
        self.detune_slider.setSingleStep(1)
        self.detune_slider.setValue(self.set1)
        self.detune_slider.move(80, 90)
        self.detune_slider.valueChanged.connect(changed_detune)

        self.detune_val_label = QLabel(self)
        self.detune_val_label.setText(str('{:2.1f}'.format(self.set1 / 10)))
        self.detune_val_label.move(290, 90)

        self.octave_label = QLabel(self)
        self.octave_label.setText('Octave')
        self.octave_label.move(10, 130)

        self.set2 = 1
        self.octave_slider = QSlider(Qt.Horizontal, self)
        self.octave_slider.setMinimumWidth(13)
        self.octave_slider.setMinimum(0)
        self.octave_slider.setMaximum(4)
        self.octave_slider.setValue(self.set2)
        self.octave_slider.move(80, 130)
        self.octave_slider.valueChanged.connect(changed_octave)

        self.octave_val_label = QLabel(self)
        self.octave_val_label.setText(str((2**self.set2) * 220))
        self.octave_val_label.move(190, 130)

        self.ramp_label = QLabel(self)
        self.ramp_label.setText('Ramp')
        self.ramp_label.move(10, 170)

        set3 = 50
        self.ramp_slider = QSlider(Qt.Horizontal, self)
        self.ramp_slider.setMinimumWidth(200)
        self.ramp_slider.setMinimum(0)
        self.ramp_slider.setMaximum(200)
        self.ramp_slider.setSingleStep(1)
        self.ramp_slider.setValue(set3)
        self.ramp_slider.move(80, 170)
        self.ramp_slider.valueChanged.connect(changed_ramp)

        self.ramp_val_label = QLabel(self)
        self.ramp_val_label.setText(str('{:3.2f}'.format(set3 * 0.01)))
        self.ramp_val_label.move(290, 170)

        self.delay_label = QLabel(self)
        self.delay_label.setText('Delay')
        self.delay_label.move(10, 210)

        set4 = 400
        self.delay_slider = QSlider(Qt.Horizontal, self)
        self.delay_slider.setMinimumWidth(200)
        self.delay_slider.setMinimum(0)
        self.delay_slider.setMaximum(8000)
        self.delay_slider.setSingleStep(100)
        self.delay_slider.setValue(set4)
        self.delay_slider.move(80, 210)
        self.delay_slider.valueChanged.connect(changed_roll)

        self.delay_val_label = QLabel(self)
        self.delay_val_label.setText(str('{:4.3f}\nSeconds'.format(set4 / 48000)))
        self.delay_val_label.move(290, 204)

        self.sine_label = QLabel(self)
        self.sine_label.setText('Sine')
        self.sine_label.move(10, 250)

        self.shape_slider = QSlider(Qt.Horizontal, self)
        self.shape_slider.setMinimumWidth(200)
        self.shape_slider.setMinimum(0)
        self.shape_slider.setMaximum(20)
        self.shape_slider.setSingleStep(1)
        self.shape_slider.setValue(0)
        self.shape_slider.move(80, 250)
        self.shape_slider.valueChanged.connect(show_apply)

        self.attack_label = QLabel(self)
        self.attack_label.setText("Attack")
        self.attack_label.move(368, 20)

        self.attack_slider = QSlider(Qt.Vertical, self)
        self.attack_slider.setMinimumHeight(100)
        self.attack_slider.setMinimum(0)
        self.attack_slider.setMaximum(100)
        self.attack_slider.setSingleStep(1)
        self.attack_slider.setValue(0)
        self.attack_slider.move(380, 50)
        self.attack_slider.valueChanged.connect(changed_attack)

        self.attack_val_label = QLabel(self)
        self.attack_val_label.setText(str('{:3.2f}'.format(0)))
        self.attack_val_label.move(377, 160)

        self.fade_label = QLabel(self)
        self.fade_label.setText("Fade")
        self.fade_label.move(442, 20)

        self.set_7 = 20
        self.fade_slider = QSlider(Qt.Vertical, self)
        self.fade_slider.setMinimumHeight(100)
        self.fade_slider.setMinimum(0)
        self.fade_slider.setMaximum(100)
        self.fade_slider.setSingleStep(1)
        self.fade_slider.setValue(self.set_7)
        self.fade_slider.move(450, 50)
        self.fade_slider.valueChanged.connect(changed_fade)

        self.fade_val_label = QLabel(self)
        self.fade_val_label.setText(str('{:3.2f}'.format(self.set_7 * 0.01)))
        self.fade_val_label.move(447, 160)

        self.volume_label = QLabel(self)
        self.volume_label.setText('Volume')
        self.volume_label.move(526, 20)

        self.set_vol = 70
        self.volume_slider = QSlider(Qt.Vertical, self)
        self.volume_slider.setMinimumHeight(100)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setSingleStep(1)
        self.volume_slider.setValue(self.set_vol)
        self.volume_slider.move(540, 50)
        self.volume_slider.valueChanged.connect(changed_vol)

        self.vol_val_label = QLabel(self)
        self.vol_val_label.setText(str("{:3.2f}".format(self.set_vol * 0.01)))
        self.vol_val_label.move(538, 160)

        self.triangle_label = QLabel(self)
        self.triangle_label.setText('Triangle')
        self.triangle_label.move(290, 250)

        self.label_pic = QLabel(self)
        self.label_apply = QLabel(self)

        self.pixmap = QPixmap("images/kira.png")
        self.pixmap_1 = QPixmap("images/say_apply.png")
        self.label_pic.setPixmap(self.pixmap)
        self.label_pic.move(410, 180)

        self.label_apply.setPixmap(self.pixmap_1)
        self.label_apply.move(410, 180)
        self.label_apply.hide()

        do_it()

    def keyPressEvent(self, event):
        if midi_on_flag[0] is True:
            return
        else:
            global sound
            if key_notes.get(event.text()) is None:
                return
            else:
                sound = key_notes.get(event.text())


def close():
    QApplication.quit()


def open_custom_kb_dialog():
    if midi_on_flag[0] is True:
        return
    else:
        global custom_kb_dialog
        if custom_kb_dialog is None or custom_kb_dialog.isVisible() is False:
            custom_kb_dialog = CustomKeyBinder()
            custom_kb_dialog.show()
        else:
            return
        

def open_output_dialog():
    global output_dialog
    if output_dialog is None or output_dialog.isVisible() is False:
        output_dialog = OutputDialog()
        output_dialog.show()
    else:
        return
    

def open_kb_window():
    global kb_window
    if kb_window is None or kb_window.isVisible() is False:
        kb_window = KeybindWindow()
        kb_window.show()
    else:
        return
    

def open_kb_preset_save():
    global save_kb_preset_window
    if save_kb_preset_window is None or save_kb_preset_window.isVisible() is False:
        save_kb_preset_window = SaveKeyboardConfig()
        save_kb_preset_window.show()
    else:
        return
    

def open_kb_preset_recall():
    global recall_window
    if recall_window is None or recall_window.isVisible() is False:
        recall_window = RecallKeyboardConfig()
        recall_window.show()
    else:
        return 
    

def open_midi_dialog():
    if midi_on_flag[0] is True:
        print("Close application to run midi.")
    else:
        global midi_dialog
        if midi_dialog is None or midi_dialog.isVisible() is False:
            midi_dialog = port_dialog.ChoosePort(midi_on_flag, activate_midi, applying_sliders_flag)
            midi_dialog.show()
        else:
            return
        

def open_save_presets():
    global save_preset_window
    if save_preset_window is None or save_preset_window.isVisible() is False:
        settings_list = [
            ex.widget.duration_slider.value(),
            ex.widget.detune_slider.value(),
            ex.widget.octave_slider.value(),
            ex.widget.ramp_slider.value(),
            ex.widget.delay_slider.value(),
            ex.widget.shape_slider.value(),
            ex.widget.volume_slider.value(),
            ex.widget.attack_slider.value(),
            ex.widget.fade_slider.value(),
            ex.widget.key_change_bool[0]
        ]
        save_preset_window = preset_dialog.PresetSaveDialog(settings_list)
        save_preset_window.show()
    else:
        return
    

def open_recall_preset():
    global recall_presets
    if recall_presets is None or recall_presets.isVisible() is False:
        recall_presets = preset_dialog.PresetRecallDialog(ex.widget, midi_on_flag)
        recall_presets.show()
    else:
        return
    

def open_messages(title, blah):
    message_window = messages_from_dead.Messages(title, blah)
    message_window.show()


def open_save_wav_dialog():
    global save_wav_window
    if save_wav_window is None or save_wav_window.isVisible() is False:
        save_wav_window = save_wav.SaveWavDialog(ex.widget.notes, new_samplerate[0])
        save_wav_window.show()
    else:
        return
    

class RecallKeyboardConfig(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 520, 600, 200)
        self.setWindowTitle("Recall Keyboard Preset File")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("k_recall_win")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.listWidget = QListWidget()
        for n, f in enumerate(os.listdir("./keyboards")):
            self.listWidget.insertItem(n, f)
        self.listWidget.clicked.connect(self.clicked)
        layout.addWidget(self.listWidget)

        self.info_label = QLabel(self)
        self.info_label.setText("Select file and click the Change Key button back on the main window.")
        layout.addWidget(self.info_label)

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(lambda: self.close())
        layout.addWidget(self.close_button)

    def clicked(self, qmodelindex):
        pickle_item = self.listWidget.currentItem().text()
        try:
            with open(f"./keyboards/{pickle_item}", "rb") as fp:
                kb_config = pickle.load(fp)
            c_keys[:] = kb_config[0]
            e_keys[:] = kb_config[1]

        except Exception as e:
            print(f"{type(e).__name__}: {str(e)}")
        self.close()


class SaveKeyboardConfig(QWidget):
    def __init__(self):
        super().__init__()

        def saver():
            keyboard_config = [c_keys, e_keys]
            stamp = self.filename_entry.text()
            if len(stamp) == 0:
                stamp = "KB-{}.pickle".format(
                    str(time.ctime()[-16:].replace(" ", "-").replace(":", "-"))
                )
            else:
                stamp = f"{stamp}.pickle"

            with open(f"keyboards/{stamp}", "wb+") as fp:
                pickle.dump(keyboard_config, fp)
            open_messages("File Saved", f"File saved as {stamp}")
            time.sleep(1)
            self.close()

        self.setGeometry(200, 500, 600, 200)
        self.setWindowTitle("Save as Preset File")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("k_preset_win")

        self.info_label = QLabel(self)
        self.info_label.setText("Give it a filename")
        self.info_label.move(20, 10)

        self.filename_entry = QLineEdit(self)
        self.filename_entry.setMaxLength(32)
        self.filename_entry.move(20, 50)
        self.filename_entry.resize(280, 40)

        self.button = QPushButton("Save", self)
        self.button.move(220, 110)

        self.button.clicked.connect(saver)

        self.close_kp_button = QPushButton("Close", self)
        self.close_kp_button.move(400, 140)
        self.close_kp_button.clicked.connect(lambda: self.close())


class CustomKeybinder(QWidget):
    def __init__(self):
        super().__init__()

        def change_key_list():
            self.is_e_list = not self.is_e_list
            if self.is_e_list:
                self.selection_label.setText("Key of E")
            else:
                self.selection_label.setText("Key of C")

        self.custom_e_list = []
        self.is_e_list = True
        self.setGeometry(400, 450, 600, 200)
        self.setWindowTitle("Set Custom Keybindings")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("ck_win")

        self.blah_label = QLabel(self)
        self.blah_label.setText(
            "Type the keys in the order you want, to whatever scale\n"
            "then go back and click the Change Key button."
        )
        self.blah_label.move(10, 10)

        self.list_label = QLabel(self)
        self.list_label.setText("")
        self.list_label.resize(550, 25)
        self.list_label.move(10, 50)
        self.list_label.setObjectName("l_label")

        self.key_button = QPushButton("Select Key", self)
        self.key_button.move(11, 100)
        self.key_button.clicked.connect(change_key_list)

        self.selection_label = QLabel(self)
        self.selection_label.setText("Key of E")
        self.selection_label.move(130, 105)

        self.close_ckb_button = QPushButton("Close", self)
        self.close_ckb_button.move(420, 150)
        self.close_ckb_button.clicked.connect(lambda: self.close())

    def keyPressEvent(self, event):
        if midi_on_flag[0] is True:
            return 
        else:
            if len(self.custom_e_list) >= 10:
                if self.is_e_list:
                    e_keys[:] = self.custom_e_list[:]
                else:
                    c_keys[:] = self.custom_e_list[:]
                self.close()

            self.custom_e_list.append(event.text())
            self.list_label.setText(str(self.custom_e_list))


class OutputDialog(QWidget):
    def __init__(self):
        super().__init__()

        def stream_restart():
            do_it()
            streaming[0] = True
            stream_thread = threading.Thread(
                target=stream_func,
                args=[
                    output_device[0],
                    new_blocksize[0],
                    new_samplerate[0]
                ],
                daemon=True
            )
            stream_thread.start()

        def reset_default_func():
            new_blocksize[0] = default_blocksize
            output_device[0] = -1
            new_samplerate[0] = sample_rate
            close_devices_dialog()

        def close_devices_dialog():
            stream_restart()
            self.close()

        def changed_blocksize():
            new_blocksize[0] = int(2 ** self.blocksize_slider.value())
            self.blocksize_val_label.setText(f"Blocksize = {new_blocksize[0]}")
            self.blocksize_val_label.adjustSize()

        def changed_samplerate():
            new_samplerate[0] = self.samplerate_slider.value()
            if new_samplerate[0] == 0:
                new_samplerate[0] = 44100
                self.samplerate_val_label.setText(f"Samplerate = {new_samplerate[0]}")
            else:
                new_samplerate[0] = 48000
                self.samplerate_val_label.setText(f"Samplerate = {new_samplerate[0]}")

        streaming[0] = False
        query = repr(sd.query_devices())
        query = query.split("\n")
        self.setGeometry(40, 200, 500, 600)
        self.setWindowTitle("Set Output Device and Blocksize")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("op_win")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.listWidget = QListWidget()
        for i in range(len(query)):
            self.listWidget.insertItem(i, query[i])
        self.listWidget.clicked.connect(self.clicked)
        layout.addWidget(self.listWidget)

        self.blocksize_slider_label = QLabel(self)
        self.blocksize_slider_label.setText("Set Blocksize Slider")
        self.blocksize_slider_label.setMaximumWidth(200)
        self.blocksize_slider_label.setObjectName("bl_label")
        layout.addWidget(self.blocksize_slider_label)

        self.blocksize_slider = QSlider(Qt.Horizontal, self)
        self.blocksize_slider.setMaximumWidth(100)
        self.blocksize_slider.setMinimum(5)
        self.blocksize_slider.setMaximum(11)
        self.blocksize_slider.setValue(int(np.log2(new_blocksize[0])))
        self.blocksize_slider.valueChanged.connect(changed_blocksize)
        layout.addWidget(self.blocksize_slider)

        self.blocksize_val_label = QLabel(self)
        self.blocksize_val_label.setText(f"Blocksize - {new_blocksize[0]}")
        layout.addWidget(self.blocksize_val_label)

        self.samplerate_slider_label = QLabel(self)
        self.samplerate_slider_label.setText("Samplerate")
        self.samplerate_slider_label.setObjectName("sr_label")
        self.samplerate_slider_label.setMaximumWidth(200)
        layout.addWidget(self.samplerate_slider_label)

        self.samplerate_slider = QSlider(Qt.Horizontal, self)
        self.samplerate_slider.setMaximumWidth(50)
        self.samplerate_slider.setMinimum(0)
        self.samplerate_slider.setMaximum(1)
        self.samplerate_slider.setValue(1 if new_samplerate[0] == 48000 else 0)
        self.samplerate_slider.valueChanged.connect(changed_samplerate)
        layout.addWidget(self.samplerate_slider)

        self.samplerate_val_label = QLabel(self)
        self.samplerate_val_label.setText(f"Samplerate = {new_samplerate[0]}")
        layout.addWidget(self.samplerate_val_label)

        self.reset_button = QPushButton("reset Defaults")
        self.reset_button.setMaximumWidth(150)
        self.reset_button.clicked.connect(reset_default_func)
        layout.addWidget(self.reset_button)

        self.close_bsw_button = QPushButton("Set / Close", self)
        self.close_bsw_button.clicked.connect(close_devices_dialog)
        layout.addWidget(self.close_bsw_button)

    def clicked(self, qmodelindex):
        item = self.listWidget.currentItem()
        ploo = item.text()[:4].replace('*', '').strip()
        try:
            output_device[0] = int(ploo)
        except Exception as e:
            print(f"{type(e).__name__}: {str(e)}")
            output_device[0] = -1


class KeybindWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(550, 200, 447, 400)
        self.setWindowTitle("Keyboard Layout")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))
        self.setObjectName("kb_win")

        self.c_kb_image = QPixmap("images/kb_c.jpg")
        self.e_kb_image = QPixmap("images/kb_e.jpg")

        self.label_c_kb = QLabel(self)
        self.label_c_kb.setPixmap(self.c_kb_image)
        self.label_c_kb.move(13, 5)

        self.label_e_kb = QLabel(self)
        self.label_e_kb.setPixmap(self.e_kb_image)
        self.label_e_kb.move(13, 150)

        self.close_kbw_button = QPushButton("Close", self)
        self.close_kbw_button.move(250, 320)
        self.close_kbw_button.clicked.connect(lambda: self.close())


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.exitAc = QAction(QIcon('exit.png'), '&Exit', self)
        self.exitAc.setShortcut('Ctrl+Q')
        self.exitAc.setStatusTip('Exit Application')
        self.exitAc.triggered.connect(qApp.quit)

        self.kb_layout_ac = QAction('Keyboard Layout', self)
        self.kb_layout_ac.setStatusTip('Keyboard layout diagrams for scale of C and E')
        self.kb_layout_ac.triggered.connect(open_kb_window)

        self.op_dialog_ac = QAction("Set Output Device, Blocksize, or Samplerate", self)
        self.op_dialog_ac.setStatusTip("Select output device and set a blocksize or samplerate for output stream")
        self.op_dialog_ac.triggered.connect(open_output_dialog)

        self.custom_kb_dialog_ac = QAction("Custom Keybinder", self)
        self.custom_kb_dialog_ac.setStatusTip("Bind whatever keys to the scales instead of the qwerty configuration")
        self.custom_kb_dialog_ac.triggered.connect(open_custom_kb_dialog)

        self.save_kb_config_ac = QAction("Save current Keyboard Configuration", self)
        self.save_kb_config_ac.setStatusTip("Save current keyboard configuration as a preset file")
        self.save_kb_config_ac.triggered.connect(open_kb_preset_save)

        self.recall_kb_config_ac = QAction("Recall Keyboard Configuration", self)
        self.recall_kb_config_ac.setStatusTip("Recall a saved keyboard configuration preset file and apply configuration")
        self.recall_kb_config_ac.triggered.connect(open_kb_preset_recall)

        self.midi_ac = QAction("Open Midi Input Port", self)
        self.midi_ac.setStatusTip("Open dialogue to choose midi input port for midi keyboard")
        self.midi_ac.triggered.connect(open_midi_dialog)

        self.save_preset_ac = QAction("Save as Presets", self)
        self.save_preset_ac.setStatusTip("Open dialogue to save settings as presets")
        self.save_preset_ac.triggered.connect(open_save_presets)

        self.recall_presets_ac = QAction("Recall Presets", self)
        self.recall_presets_ac.setStatusTip("Open dialogue to recall setting presets from a file")
        self.recall_presets_ac.triggered.connect(open_recall_preset)

        self.save_wav_ac = QAction("Save Notes as .wav file")
        self.save_wav_ac.setStatusTip("Creates a directory filled with a wav file for each note")
        self.save_wav_ac.triggered.connect(open_save_wav_dialog)

        self.status_bar = self.statusBar()
        self.status_bar.setObjectName("status_bar_obj")

        self.menubar = self.menuBar()
        self.settingsMenu = self.menubar.addMenu("Stuff")
        self.settingsMenu.addAction(self.exitAc)
        self.settingsMenu.addAction(self.kb_layout_ac)
        self.settingsMenu.addAction(self.op_dialog_ac)
        self.settingsMenu.addAction(self.custom_kb_dialog_ac)
        self.settingsMenu.addAction(self.save_kb_config_ac)
        self.settingsMenu.addAction(self.recall_kb_config_ac)
        self.settingsMenu.addAction(self.midi_ac)
        self.settingsMenu.addAction(self.save_preset_ac)
        self.settingsMenu.addAction(self.recall_presets_ac)
        self.settingsMenu.addAction(self.save_wav_ac)
        self.menubar.setObjectName("menubar_obj")

        self.setWindowTitle("Sound Arcanum - Synthboard")
        self.setWindowIcon(QIcon('images/knotperfect-icon.png'))

        self.setGeometry(20, 100, 750, 500)

        self.widget = SliderFrame()
        self.setCentralWidget(self.widget)

        self.show()


def stream_func(device=-1, blocksize=256, sample_rate=48000):
    def callback(outdata, frames, time, status):
        try:
            data = next(sound_slice)
            outdata[:, :] = data
        except ValueError:
            outdata[:, :] = np.zeros((blocksize, 2))

    def gen():
        global sound
        sound = np.zeros((blocksize, 2))
        while True:
            # _slice = sound[:blocksize, ]
            _slice = sound[:blocksize, :]
            yield _slice
            sound = sound[blocksize:, :]

    sound_slice = gen()
    try:
        device = device if device >= 0 else None
    except TypeError:
        device = None
    
    print(f"blocksize: {blocksize}")
    print(f"samplerate: {sample_rate}")
    stream = sd.OutputStream(
        device=device,
        channels=2,
        callback=callback,
        blocksize=blocksize,
        samplerate=sample_rate
    )
    with stream:
        while streaming[0] is True:
            time.sleep(0.5)
        else:
            stream.__exit__()


def midi_stuff(port_arg):
    def play_note(event):
        global key_notes
        if applying_sliders_flag[0] is True:
            return
        else:
            try:
                global sound
                sound = key_notes.get(event)
            except TypeError:
                return

    if len(port_arg) > 1:
        portname = port_arg
    else:
        portname = None

    with mido.open_input(portname) as port:
        print("Using {}".format(port))
        print("Waiting for messages...")
        for message in port:
            if message.type == "note_on" and message.velocity > 0:
                play_note(message.note)


def activate_midi(port_arg):
    midi_thread = threading.Thread(
        target=midi_stuff,
        args=[port_arg],
        daemon=True
    )

    midi_thread.start()


c_keys = [
    "a",
    "w",
    "s",
    "e",
    "d",
    "f",
    "t",
    "g",
    "y",
    "h",
    "u",
    "j",
    "k",
    "o",
    "l",
    "p",
    ";",
    "'",
]

e_keys = [
    "a",
    "s",
    "e",
    "d",
    "r",
    "f",
    "t",
    "g",
    "h",
    "u",
    "j",
    "i",
    "k",
    "l",
    "p",
    ";",
    "[",
    "'",
]

note_nums = [i for i in range(36, 97)]
midi_range = range(-33, 28)
midi_on_flag = [False]
applying_sliders_flag = [True]
output_device = [-1]
streaming = [True]
keys = []
sample_rate = 48000
new_samplerate = [48000]
blocksize = 256
default_blocksize = 256
new_blocksize = [default_blocksize]
kb_window = None
custom_kb_dialog = None
output_dialog = None
save_kb_preset_window = None
recall_window = None
midi_dialog = None
save_preset_window = None
recall_presets = None
save_wav_window = None

stream_thread = threading.Thread(
    target=stream_func,
    args=[-1, default_blocksize],
    daemon=True
)
stream_thread.start()

app = QApplication(sys.argv)
with open("styles.css", "r") as f:
    styles = f.read()

app.setStyleSheet(styles)
ex = MainWindow()

sys.exit(app.exec_())



