from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont
from utils.Exceptions import Abort
from enum import Enum


class MsgIcon(Enum):
    QUESTION = QMessageBox.Question
    INFORMATION = QMessageBox.Information
    WARNING = QMessageBox.Warning
    CRITICAL = QMessageBox.Critical


def display_msg(icon, title, message,extra_info=None):
    msg = QMessageBox(QMessageBox.Icon(icon.value), title, message)
    msg.setFont(QFont("Segoe UI", 12, QFont.Bold))
    if extra_info:
        msg.setInformativeText(extra_info)
    if icon == MsgIcon.WARNING:
        msg.exec()
    if icon == MsgIcon.QUESTION:
        msg.setStandardButtons(QMessageBox.Abort | QMessageBox.Yes)
        msg.setDefaultButton(QMessageBox.Abort)
        res = msg.exec()
        if res == QMessageBox.Abort:
            raise Abort()
    if icon == MsgIcon.INFORMATION:
        msg.exec()

