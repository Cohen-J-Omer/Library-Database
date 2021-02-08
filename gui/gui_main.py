import os, sys

from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtCore, QtGui, QtWidgets

from menu_actions import export_db_json, export_db_sql, import_to_db_json, import_to_db_sql, clear_db, export_db_csv
from functools import partial

from msg_box import MsgIcon, display_msg
from utils.Exceptions import Abort
from login import LoginForm

from database.database import Database
from books_tab import BooksTab
from group_tab import GroupTab
from words_tab import WordsTab
from phrase_tab import PhraseTab
from stats_tab import StatsTab


class Manager(QtWidgets.QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db

    def closeEvent(self, event):
        """overriding QMainWindow's closeEvent to clear Database when closing app."""
        try:
            display_msg(MsgIcon.QUESTION, "Confirm Your Action",
                        "You are about to shut-down the app."
                        "\nAlthough the Database you created will not be erased,"
                        "\nconsider exporting the database beforehand."
                        "\nAdvance?")
        except Abort:  # user chose to abort closing the DB
            event.ignore()  # ignore app shutdown event.
            return
        # else: App closes as close-event propagates


class UiMainWindow:

    def __init__(self, main_window):
        db = main_window.db
        self.central_widget = QtWidgets.QWidget(main_window)
        self.tabs = QtWidgets.QTabWidget(self.central_widget)
        self.menu_bar = QtWidgets.QMenuBar(main_window)  # not necessary to define main_window as parent
        self.menu_config(db)
        self.tabs_config(db)
        self.main_window_config(main_window)

    def tabs_config(self, db):
        self.tabs.setGeometry(QtCore.QRect(0, 0, 1341, 861))

        tabs_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        tabs_size_policy.setHorizontalStretch(0)
        tabs_size_policy.setVerticalStretch(0)
        tabs_size_policy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())

        self.tabs.setSizePolicy(tabs_size_policy)
        self.tabs.setMinimumSize(QtCore.QSize(1341, 861))
        self.tabs.setFont(QtGui.QFont("Segoe UI", 14, QFont.Bold))
        self.tabs.setTabShape(QtWidgets.QTabWidget.Triangular)

        tab_books = BooksTab(db)
        self.tabs.addTab(tab_books, "Books")

        tab_group = GroupTab(db)
        self.tabs.addTab(tab_group, "Word Group")

        tab_words = WordsTab(db)
        self.tabs.addTab(tab_words, "Word Search")

        tab_phrase = PhraseTab(db)
        self.tabs.addTab(tab_phrase, "Phrase Search")

        tab_stats = StatsTab(db)
        self.tabs.addTab(tab_stats, "Statistics")

        self.tabs.setCurrentIndex(0)

    def main_window_config(self, main_window):
        main_window.setCentralWidget(self.central_widget)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())

        main_window.setSizePolicy(size_policy)
        main_window.setMinimumSize(QtCore.QSize(1364, 907))
        main_window.setMaximumSize(QtCore.QSize(1364, 907))
        main_window.setWindowTitle("Library")
        main_window.setWindowIcon(QIcon((os.path.join(os.path.dirname('__file__'), "images/book.png"))))

        main_window.setMenuBar(self.menu_bar)

    def menu_config(self, db):
        self.menu_bar.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.menu_bar.setStyleSheet("\"border: 1px solid black;\"")

        menu_file = QtWidgets.QMenu(self.menu_bar)
        menu_file.setTitle("Menu")

        font_menu_action = QtGui.QFont("Segoe UI", 12, QFont.Bold)

        action_clear = QtWidgets.QAction(QIcon((os.path.join(os.path.dirname('__file__'), "images/clear.png"))),
                                         "Clear", menu_file)
        action_clear.setFont(font_menu_action)
        action_clear.setShortcut('Ctrl+O')
        action_clear.triggered.connect(partial(clear_db, db))

        action_export_json = QtWidgets.QAction(
            QIcon((os.path.join(os.path.dirname('__file__'), "images/save.png"))),
            "Export to Json", menu_file)
        action_export_json.setFont(font_menu_action)
        action_export_json.setShortcut('Ctrl+J')
        action_export_json.triggered.connect(partial(export_db_json, db, self.central_widget))

        action_export_sql = QtWidgets.QAction(
            QIcon((os.path.join(os.path.dirname('__file__'), "images/save.png"))),
            "Export to SQL", menu_file)
        action_export_sql.setFont(font_menu_action)
        action_export_sql.setShortcut('Ctrl+S')
        action_export_sql.triggered.connect(partial(export_db_sql, self.central_widget, db.credentials))

        action_export_csv = QtWidgets.QAction(
            QIcon((os.path.join(os.path.dirname('__file__'), "images/save.png"))),
            "Export to Excel", menu_file)
        action_export_csv.setFont(font_menu_action)
        action_export_csv.setShortcut('Ctrl+X')
        action_export_csv.triggered.connect(partial(export_db_csv, db, self.central_widget))

        action_import_json = QtWidgets.QAction(
            QIcon((os.path.join(os.path.dirname('__file__'), "images/upload.png"))),
            "Import Json", menu_file)
        action_import_json.setFont(font_menu_action)
        action_import_json.setShortcut('shift+J')
        action_import_json.triggered.connect(partial(import_to_db_json, db, self.central_widget))

        action_import_sql = QtWidgets.QAction(
            QIcon((os.path.join(os.path.dirname('__file__'), "images/upload.png"))),
            "Import SQL", menu_file)
        action_import_sql.setFont(font_menu_action)
        action_import_sql.setShortcut('shift+S')
        action_import_sql.triggered.connect(partial(import_to_db_sql, db, self.central_widget, db.credentials))

        menu_file.addAction(action_export_json)
        menu_file.addAction(action_export_sql)
        menu_file.addAction(action_export_csv)
        menu_file.addSeparator()
        menu_file.addAction(action_import_json)
        menu_file.addAction(action_import_sql)
        menu_file.addSeparator()
        menu_file.addAction(action_clear)
        self.menu_bar.addAction(menu_file.menuAction())


def start_app():
    app = QtWidgets.QApplication(sys.argv)
    login = LoginForm()
    credentials = None
    if login.exec():
        credentials = login.get_credentials()
    db = Database(credentials)
    manager = Manager(db)
    UiMainWindow(manager)
    manager.show()
    db.notify_import()  # alerts all tabs to update their content in case database isn't empty
    sys.exit(app.exec_())  # app.exec_() will run main thread on our code and the app's event loop
