import sys, random, os
from PyQt6 import QtWidgets, QtGui, QtCore, uic

UI_PATH = os.path.join(os.path.dirname(__file__), 'task3.ui')

class Canvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); self.shapes = []; self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    def mousePressEvent(self, event):
        x, y = event.position().x(), event.position().y(); size = random.randint(10,60)
        color = QtGui.QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if event.button() == QtCore.Qt.MouseButton.LeftButton: self.shapes.append(('circle', x, y, size, color))
        elif event.button() == QtCore.Qt.MouseButton.RightButton: self.shapes.append(('square', x, y, size, color))
        self.update()
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Space:
            pos = self.mapFromGlobal(QtGui.QCursor.pos()); x, y = pos.x(), pos.y(); size = random.randint(10,60)
            color = QtGui.QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255)); self.shapes.append(('triangle', x, y, size, color)); self.update()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        for t,x,y,s,col in self.shapes:
            painter.setBrush(col)
            if t == 'circle': painter.drawEllipse(int(x-s/2), int(y-s/2), s, s)
            elif t == 'square': painter.drawRect(int(x-s/2), int(y-s/2), s, s)
            elif t == 'triangle':
                p1 = QtCore.QPoint(int(x), int(y-int(s/2))); p2 = QtCore.QPoint(int(x-int(s/2)), int(y+int(s/2))); p3 = QtCore.QPoint(int(x+int(s/2)), int(y+int(s/2)))
                painter.drawPolygon(p1, p2, p3)

class Task3App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(); uic.loadUi(UI_PATH, self); self.canvas = Canvas(); self.setCentralWidget(self.canvas)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv); w = Task3App(); w.resize(600,400); w.show(); sys.exit(app.exec())
