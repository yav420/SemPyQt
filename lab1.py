import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


# Задание 1 - Перекидыватель слов
class Task1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        self.field1 = QLineEdit()
        self.field2 = QLineEdit()
        self.button = QPushButton("→")
        self.button.clicked.connect(self.switch)
        
        layout.addWidget(self.field1)
        layout.addWidget(self.button)
        layout.addWidget(self.field2)
        self.setLayout(layout)
    
    def switch(self):
        if self.button.text() == "→":
            self.field2.setText(self.field1.text())
            self.field1.clear()
            self.button.setText("←")
        else:
            self.field1.setText(self.field2.text())
            self.field2.clear()
            self.button.setText("→")


# Задание 2 - Калькулятор выражений
class Task2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.input_field = QLineEdit()
        self.result_field = QLineEdit()
        self.result_field.setReadOnly(True)
        self.button = QPushButton("Вычислить")
        self.button.clicked.connect(self.calculate)
        
        layout.addWidget(QLabel("Введите выражение:"))
        layout.addWidget(self.input_field)
        layout.addWidget(self.button)
        layout.addWidget(QLabel("Результат:"))
        layout.addWidget(self.result_field)
        self.setLayout(layout)
    
    def calculate(self):
        try:
            result = eval(self.input_field.text())
            self.result_field.setText(str(result))
        except:
            self.result_field.setText("Ошибка!")


# Задание 3 - Чекбоксы
class Task3(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Создаем виджеты и чекбоксы
        self.widgets = [
            QLineEdit("Текст здесь"),
            QPushButton("Кнопка"),
            QLabel("Метка")
        ]
        
        names = ["Поле ввода", "Кнопка", "Метка"]
        
        for name, widget in zip(names, self.widgets):
            hbox = QHBoxLayout()
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda state, w=widget: w.setVisible(state == 2))
            hbox.addWidget(checkbox)
            hbox.addWidget(widget)
            layout.addLayout(hbox)
        
        self.setLayout(layout)


# Задание 4 - Азбука Морзе
class Task4(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.output = QLineEdit()
        self.output.setReadOnly(True)
        
        # Коды Морзе для A-Z
        morse = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..'
        }
        
        # Создаем кнопки в цикле
        grid = QGridLayout()
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        for i, letter in enumerate(letters):
            btn = QPushButton(letter)
            btn.clicked.connect(lambda checked, l=letter: self.add_code(morse[l]))
            grid.addWidget(btn, i // 6, i % 6)
        
        layout.addWidget(QLabel("Код Морзе:"))
        layout.addWidget(self.output)
        layout.addLayout(grid)
        self.setLayout(layout)
    
    def add_code(self, code):
        self.output.setText(self.output.text() + code + ' ')


# Задание 5 - Ресторан
class Task5(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        # Левая часть - меню
        left = QVBoxLayout()
        left.addWidget(QLabel("Меню:"))
        
        self.dishes = [
            {"name": "Суп", "price": 300},
            {"name": "Салат", "price": 250},
            {"name": "Главное", "price": 500},
            {"name": "Десерт", "price": 200}
        ]
        
        self.checks = []
        self.spins = []
        
        for dish in self.dishes:
            hbox = QHBoxLayout()
            
            check = QCheckBox(f"{dish['name']} - {dish['price']} руб.")
            spin = QSpinBox()
            spin.setRange(0, 10)
            spin.setEnabled(False)
            
            check.stateChanged.connect(lambda state, s=spin: s.setEnabled(state == 2))
            check.stateChanged.connect(self.update_bill)
            spin.valueChanged.connect(self.update_bill)
            
            hbox.addWidget(check)
            hbox.addWidget(QLabel("Кол-во:"))
            hbox.addWidget(spin)
            
            left.addLayout(hbox)
            self.checks.append(check)
            self.spins.append(spin)
        
        # Правая часть - чек
        right = QVBoxLayout()
        self.bill = QPlainTextEdit()
        self.bill.setReadOnly(True)
        self.total = QLabel("Итого: 0 руб.")
        
        right.addWidget(QLabel("Чек:"))
        right.addWidget(self.bill)
        right.addWidget(self.total)
        
        layout.addLayout(left)
        layout.addLayout(right)
        self.setLayout(layout)
    
    def update_bill(self):
        text = "Ваш заказ:\n"
        total = 0
        
        for check, spin, dish in zip(self.checks, self.spins, self.dishes):
            if check.isChecked():
                count = spin.value()
                if count == 0:
                    spin.setValue(1)
                    count = 1
                cost = dish['price'] * count
                text += f"{dish['name']} x{count} = {cost} руб.\n"
                total += cost
        
        text += f"\nИтого: {total} руб."
        self.bill.setPlainText(text)
        self.total.setText(f"Итого: {total} руб.")


# Задание 6 - Калькулятор
class Task6(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        
        # Кнопки калькулятора
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+'],
            ['C']
        ]
        
        grid = QGridLayout()
        
        for row, row_btns in enumerate(buttons):
            for col, btn_text in enumerate(row_btns):
                btn = QPushButton(btn_text)
                btn.clicked.connect(self.click)
                grid.addWidget(btn, row, col)
        
        layout.addWidget(self.display)
        layout.addLayout(grid)
        self.setLayout(layout)
        
        self.current = ''
        self.previous = ''
        self.operation = None
    
    def click(self):
        text = self.sender().text()
        
        if text in '0123456789.':
            self.current += text
            self.display.setText(self.current)
        
        elif text in '+-*/':
            if self.current:
                self.previous = self.current
                self.current = ''
                self.operation = text
        
        elif text == '=':
            if self.previous and self.current and self.operation:
                try:
                    a = float(self.previous)
                    b = float(self.current)
                    
                    if self.operation == '+':
                        result = a + b
                    elif self.operation == '-':
                        result = a - b
                    elif self.operation == '*':
                        result = a * b
                    elif self.operation == '/':
                        if b == 0:
                            self.display.setText("Ошибка!")
                            return
                        result = a / b
                    
                    self.display.setText(str(result))
                    self.current = str(result)
                    self.previous = ''
                    
                except:
                    self.display.setText("Ошибка!")
        
        elif text == 'C':
            self.current = ''
            self.previous = ''
            self.operation = None
            self.display.clear()


# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа 1")
        self.setGeometry(100, 100, 600, 400)
        
        tabs = QTabWidget()
        tabs.addTab(Task1(), "Задание 1")
        tabs.addTab(Task2(), "Задание 2")
        tabs.addTab(Task3(), "Задание 3")
        tabs.addTab(Task4(), "Задание 4")
        tabs.addTab(Task5(), "Задание 5")
        tabs.addTab(Task6(), "Задание 6")
        
        self.setCentralWidget(tabs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())