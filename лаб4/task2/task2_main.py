import os, sys, sqlite3
from PyQt6 import QtWidgets, QtGui, uic

UI_PATH = os.path.join(os.path.dirname(__file__), 'task2.ui')

class Task2App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self.table = QtWidgets.QTableView(self)
        self.addBtn = QtWidgets.QPushButton('Добавить', self)
        self.editBtn = QtWidgets.QPushButton('Изменить', self)
        self.delBtn = QtWidgets.QPushButton('Удалить', self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        hl = QtWidgets.QHBoxLayout(); hl.addWidget(self.addBtn); hl.addWidget(self.editBtn); hl.addWidget(self.delBtn)
        layout.addLayout(hl)
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'films_db.sqlite')
        self.addBtn.clicked.connect(self.add_record); self.editBtn.clicked.connect(self.edit_record); self.delBtn.clicked.connect(self.delete_record)
        self.load_data()

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def load_data(self):
        if not os.path.exists(self.db_path):
            QtWidgets.QMessageBox.warning(self, 'Файл не найден', f'Поместите films_db.sqlite в {os.path.dirname(self.db_path)}'); return
        conn = self.get_conn(); cur = conn.cursor()
        try:
            cur.execute('PRAGMA table_info(Films)'); cols = [r[1] for r in cur.fetchall()]
            cur.execute('SELECT * FROM Films'); rows = cur.fetchall()
        finally:
            conn.close()
        model = QtGui.QStandardItemModel(self); model.setHorizontalHeaderLabels(cols)
        for row in rows:
            items = [QtGui.QStandardItem(str(x)) for x in row]; model.appendRow(items)
        self.table.setModel(model); self.table.resizeColumnsToContents()

    def add_record(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Добавить', 'Введите значения через запятую (в порядке полей):')
        if not ok or not text.strip(): return
        vals = [v.strip() for v in text.split(',')]
        conn = self.get_conn(); cur = conn.cursor()
        try:
            cur.execute('PRAGMA table_info(Films)'); cols = [r[1] for r in cur.fetchall()]
            if len(vals) != len(cols):
                QtWidgets.QMessageBox.warning(self, 'Ошибка', f'Требуется {len(cols)} значений'); return
            placeholders = ','.join('?'*len(vals))
            cur.execute(f'INSERT INTO Films ({",".join(cols)}) VALUES ({placeholders})', vals); conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', str(e))
        finally:
            conn.close(); self.load_data()

    def edit_record(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Выберите строку для редактирования'); return
        row = sel[0].row(); model = self.table.model()
        values = [model.item(row, c).text() for c in range(model.columnCount())]
        text, ok = QtWidgets.QInputDialog.getText(self, 'Изменить', 'Отредактируйте значения через запятую:', text=','.join(values))
        if not ok: return
        new_vals = [v.strip() for v in text.split(',')]
        conn = self.get_conn(); cur = conn.cursor()
        try:
            cur.execute('PRAGMA table_info(Films)'); cols = [r[1] for r in cur.fetchall()]
            pk_col = cols[0]; pk_val = values[0]
            set_clause = ','.join([f"{c}=?" for c in cols[1:]])
            cur.execute(f'UPDATE Films SET {set_clause} WHERE {pk_col}=?', new_vals[1:]+[pk_val]); conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', str(e))
        finally:
            conn.close(); self.load_data()

    def delete_record(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Выберите запись для удаления'); return
        row = sel[0].row(); model = self.table.model(); pk_val = model.item(row,0).text()
        conn = self.get_conn(); cur = conn.cursor()
        try:
            cur.execute('PRAGMA table_info(Films)'); cols = [r[1] for r in cur.fetchall()]; pk_col = cols[0]
            cur.execute(f'DELETE FROM Films WHERE {pk_col}=?', (pk_val,)); conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', str(e))
        finally:
            conn.close(); self.load_data()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv); w = Task2App(); w.resize(900,600); w.show(); sys.exit(app.exec())
