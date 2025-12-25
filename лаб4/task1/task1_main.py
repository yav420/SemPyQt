import os, sys
from PyQt6 import QtWidgets, QtGui, QtCore, uic
import pandas as pd

UI_PATH = os.path.join(os.path.dirname(__file__), 'task1.ui')

class Task1App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self.schoolCombo = QtWidgets.QComboBox(self)
        self.classCombo = QtWidgets.QComboBox(self)
        self.filterBtn = QtWidgets.QPushButton('Применить', self)
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(QtWidgets.QLabel('Школа:'))
        top_layout.addWidget(self.schoolCombo)
        top_layout.addWidget(QtWidgets.QLabel('Класс:'))
        top_layout.addWidget(self.classCombo)
        top_layout.addWidget(self.filterBtn)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        self.table = QtWidgets.QTableView(self)
        main_layout.addWidget(self.table)

        self.model = QtGui.QStandardItemModel(self)
        self.table.setModel(self.model)

        self.filterBtn.clicked.connect(self.apply_filter)
        self.load_data()

    def load_data(self):
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'rez.csv')
        if not os.path.exists(csv_path):
            QtWidgets.QMessageBox.warning(self, 'Файл не найден', f'Поместите rez.csv в {os.path.dirname(csv_path)}')
            return
        df = pd.read_csv(csv_path, sep=',', header=0, dtype=str)
        if 'login' not in df.columns or 'user_name' not in df.columns or 'Score' not in df.columns:
            QtWidgets.QMessageBox.warning(self, 'Неправильный формат', 'В файле должны быть колонки login, user_name, Score')
            return
        def school_from_login(s):
            try:
                return s.split('-')[2]
            except:
                return ''
        def class_from_login(s):
            try:
                return s.split('-')[3]
            except:
                return ''
        df['school'] = df['login'].apply(school_from_login)
        df['class'] = df['login'].apply(class_from_login)
        df['Score_numeric'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        self.df = df
        self.schoolCombo.addItem('Все', userData=None)
        for s in sorted(df['school'].dropna().unique()):
            self.schoolCombo.addItem(s, userData=s)
        self.classCombo.addItem('Все', userData=None)
        for c in sorted(df['class'].dropna().unique()):
            self.classCombo.addItem(c, userData=c)
        self.show_df(df)

    def show_df(self, df):
        cols = ['login','user_name','Score']
        self.model.clear()
        self.model.setHorizontalHeaderLabels(cols)
        for _, row in df.iterrows():
            items = [QtGui.QStandardItem(str(row.get(c,''))) for c in cols]
            self.model.appendRow(items)
        scores = sorted(df['Score_numeric'].unique(), reverse=True)
        top3 = scores[:3]
        for r in range(self.model.rowCount()):
            try:
                score_val = float(self.model.item(r,2).text() or 0)
            except:
                score_val = 0.0
            if score_val in top3:
                idx = top3.index(score_val)
                if idx == 0:
                    color = QtGui.QColor(255, 223, 186)
                elif idx == 1:
                    color = QtGui.QColor(192, 192, 192)
                else:
                    color = QtGui.QColor(205, 127, 50)
                for c in range(self.model.columnCount()):
                    self.model.item(r,c).setBackground(color)
        self.table.resizeColumnsToContents()

    def apply_filter(self):
        df = self.df.copy()
        s = self.schoolCombo.currentData()
        c = self.classCombo.currentData()
        if s:
            df = df[df['school'] == s]
        if c:
            df = df[df['class'] == c]
        self.show_df(df)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Task1App(); w.resize(800,600); w.show(); sys.exit(app.exec())
