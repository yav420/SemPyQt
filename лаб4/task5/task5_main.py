import sys, os
from PyQt6 import QtWidgets, QtGui, QtCore, uic

UI_PATH = os.path.join(os.path.dirname(__file__), 'task5.ui')

class UFOWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent); self.setText('🛸'); self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter); self.resize(48,48); self.setStyleSheet('font-size:28pt;')

class Task5App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); uic.loadUi(UI_PATH, self); self.ufo = UFOWidget(self); self.ufo.move(100,100); self.step = 20; self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    def keyPressEvent(self, event):
        x,y = self.ufo.x(), self.ufo.y(); w,h = self.width(), self.height()
        if event.key() == QtCore.Qt.Key.Key_Left: x -= self.step
        elif event.key() == QtCore.Qt.Key.Key_Right: x += self.step
        elif event.key() == QtCore.Qt.Key.Key_Up: y -= self.step
        elif event.key() == QtCore.Qt.Key.Key_Down: y += self.step
        if x < -50: x = w
        if x > w: x = -50
        if y < -50: y = h
        if y > h: y = -50
        self.ufo.move(x,y)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv); w = Task5App(); w.resize(600,400); w.show(); sys.exit(app.exec())
