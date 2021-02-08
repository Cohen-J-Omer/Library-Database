import os
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QPushButton, QLabel, QLineEdit, QDialog)


class LoginForm(QDialog):
    """A login form for the user to fill, requesting details regarding the MySQL server it has established"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_username = QLineEdit(self)
        self.line_password = QLineEdit(self)
        self.line_host = QLineEdit(self)
        self.line_database = QLineEdit(self)

        self.setWindowIcon(QIcon((os.path.join(os.path.dirname('__file__'), "images/login_icon.png"))))
        self.setWindowTitle('Login Form')
        self.resize(510, 420)
        self.setStyleSheet("background-color: rgb(54, 54, 54);")

        self.labels_config()
        self.lines_config()
        self.btn_config()

    def get_credentials(self):
        """:returns the MySQL server the user filled"""
        return {'user': self.line_username.text(), 'password': self.line_password.text(),
                'host': self.line_host.text(), 'database': self.line_database.text()}

    def test_login(self):
        """:returns the details of the MySQL test server for developing and debugging """
        self.line_username.setText('root')
        self.line_password.setText('1234')
        self.line_host.setText('127.0.0.1')
        self.line_database.setText('testdatabase')
        self.accept()

    def enter(self):
        """emits the accept signal required to close the Dialog window without raising an error"""
        self.accept()

    def labels_config(self):
        label_style_sheet = "font-size: 15pt; color: rgb(255, 170, 0)"

        lbl_welcome = QLabel('Welcome', self)
        lbl_welcome.setGeometry(QtCore.QRect(190, 15, 151, 61))
        lbl_welcome.setStyleSheet("color: rgb(225, 225, 225);font-size:28pt;")

        lbl_instructions = QLabel('Please enter your MySQL server credentials:', self)
        lbl_instructions.setGeometry(QtCore.QRect(140, 75, 261, 21))
        lbl_instructions.setStyleSheet("color: rgb(225, 225, 225); font-size: 10pt;")

        lbl_user = QLabel('Username:', self)
        lbl_user.setGeometry(QtCore.QRect(30, 130, 101, 21))
        lbl_user.setStyleSheet(label_style_sheet)

        lbl_password = QLabel('Password:', self)
        lbl_password.setGeometry(QtCore.QRect(30, 180, 91, 21))
        lbl_password.setStyleSheet(label_style_sheet)

        lbl_host = QLabel('Host-IP:', self)
        lbl_host.setGeometry(QtCore.QRect(30, 230, 91, 21))
        lbl_host.setStyleSheet(label_style_sheet)

        lbl_database = QLabel('Database:', self)
        lbl_database.setGeometry(QtCore.QRect(30, 280, 91, 21))
        lbl_database.setStyleSheet(label_style_sheet)

    def lines_config(self):
        label_style_sheet = "font-size: 13pt; color: rgb(225, 225, 225);"

        self.line_username.setGeometry(QtCore.QRect(160, 130, 310, 31))
        self.line_username.setStyleSheet(label_style_sheet)
        self.line_username.setPlaceholderText('Please enter your username')

        self.line_password.setGeometry(QtCore.QRect(160, 180, 310, 31))
        self.line_password.setStyleSheet(label_style_sheet)
        self.line_password.setPlaceholderText('Please enter your password')

        self.line_host.setGeometry(QtCore.QRect(160, 230, 310, 31))
        self.line_host.setStyleSheet(label_style_sheet)
        self.line_host.setPlaceholderText('Please enter the IP address of the host')

        self.line_database.setGeometry(QtCore.QRect(160, 280, 310, 31))
        self.line_database.setStyleSheet(label_style_sheet)
        self.line_database.setPlaceholderText('Please enter the name of your database')

    def btn_config(self):
        btn_login = QPushButton('Login', self)
        btn_login.clicked.connect(self.enter)
        btn_login.setGeometry(QtCore.QRect(235, 330, 91, 41))
        btn_login.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:\n"
                                "0 rgba(255, 178, 102, 255), stop:0.55 rgba(235, 148, 61, 255), \n"
                                "stop:0.98 rgba(0, 0, 0, 255), stop:1 rgba(0, 0, 0, 0)); color: rgb(0, 0, 0);\n "
                                "font: bold 16pt")

        btn_test = QPushButton('Test Login', self)
        btn_test.setGeometry(QtCore.QRect(10, 380, 91, 31))
        btn_test.setStyleSheet('background-color: rgb(167, 168, 167);font: 12pt "Mongolian Baiti";')
        btn_test.clicked.connect(self.test_login)


