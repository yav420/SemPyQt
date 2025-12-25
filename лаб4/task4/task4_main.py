import sys, random, os
from PyQt6 import QtWidgets, QtCore, uic

UI_PATH = os.path.join(os.path.dirname(__file__), 'task4.ui')

class Task4App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); uic.loadUi(UI_PATH, self)
        self.button = QtWidgets.QPushButton('Нажми меня', self); self.button.resize(120,40); self.button.move(50,50)
        self.setMouseTracking(True); self.button.setMouseTracking(True)
    def mouseMoveEvent(self, event):
        bx,by = self.button.x(), self.button.y(); bw, bh = self.button.width(), self.button.height()
        mx,my = event.position().x(), event.position().y(); cx,cy = bx + bw/2, by + bh/2
        dist = ((mx-cx)**2 + (my-cy)**2)**0.5
        if dist < 100:
            w, h = self.width(), self.height(); newx = min(max(0, int(random.uniform(0, w - bw))), w - bw); newy = min(max(0, int(random.uniform(0, h - bh))), h - bh)
            self.button.move(newx, newy)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv); w = Task4App(); w.resize(500,400); w.show(); sys.exit(app.exec())
