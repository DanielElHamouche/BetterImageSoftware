from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import math

class ExponentialSlider(QSlider):
    """
    implemented based on https://www.desmos.com/calculator/xz7vkxtyfh
    Reasoning:
    First half of slider should be linear from 0-100. (S set to 100)
    Second half of slider should be exponential from 100-200, with y1 (self.max_zoom) being the max zoom value.
    max zoom should be calculated based on the image size to be 1 pixel full screen.
    For now hardset to 500
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.end = 200
        self.split = 100
        self.max_zoom = 500
        self.d = (self.end**2-2*self.end*self.split+self.split**2)/(self.max_zoom-self.end)
        self.setRange(0,self.end)


    def value(self):
        if (value := super().value()) <= 100: return super().value()
        return int(value + ((value-self.split)**2)/self.d) 
            

class CustomStatusBar(QStatusBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background-color: green; color: white;")
        self.setSizeGripEnabled(False)

        self.status_label = QLabel("Status: OK")
        self.addPermanentWidget(self.status_label, 1)

        self.slider = ExponentialSlider(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.slider.setRange(1, 200)
        self.slider.setValue(100)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(lambda: self.status_label.setText(f"Value: {self.slider.value()}"))
        self.addPermanentWidget(self.slider, 1)
