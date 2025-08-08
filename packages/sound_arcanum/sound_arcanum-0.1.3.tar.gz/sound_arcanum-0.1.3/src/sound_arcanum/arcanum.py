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
            
        ]

