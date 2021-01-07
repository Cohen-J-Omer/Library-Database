import os
from PyQt5.QtGui import QFont, QBrush, QColor
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from msg_box import MsgIcon, display_msg
from utils import txt_parser
from utils.style_constants import STYLE_LINE, STYLE_BTN


class BooksTab(QtWidgets.QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.db.tune_in_import(self.update_cmbs)  # updates combo boxes and table when importing
        self.book_details = None  # keeps track of current book loaded
        # Defining Gui attributes:
        self.tbl_books = QtWidgets.QTableWidget(self)
        self.cmb_title = QtWidgets.QComboBox(self)
        self.cmb_author = QtWidgets.QComboBox(self)
        self.box_book_id = QtWidgets.QGroupBox(self)
        self.line_author = QtWidgets.QLineEdit(self.box_book_id)
        self.line_date = QtWidgets.QLineEdit(self.box_book_id)
        self.line_title = QtWidgets.QLineEdit(self.box_book_id)
        self.img = QtWidgets.QLabel(self)
        # configuring aforementioned Gui attributes:
        self.box_config()
        self.tbl_config()
        self.btn_config()
        self.cmb_config()
        self.separator_config()
        self.labels_config()
        self.img_config()

    def browse_book(self):
        """ displays user a preview of the book it selected and saves it's details """
        file_name = QFileDialog.getOpenFileName(self, "pick a book", "", "txt files (*.txt)")
        if file_name[0]:  # filename's fields will be empty if no file was chosen.
            self.book_details = txt_parser.get_book_details(file_name[0])
            if self.book_details:
                self.line_title.setText(self.book_details[0])
                self.line_author.setText(self.book_details[1])
                self.line_date.setText(self.book_details[2])
            else:
                display_msg(MsgIcon.WARNING, "Warning", "Please choose a Gutenberg project text file.")

    def insert_book(self):
        """called by "insert" UI button. inserts a book previously chosen by user. """
        if self.book_details:
            book_id = self.db.insert_book(self.book_details)
            self.line_title.setText("")
            self.line_author.setText("")
            self.line_date.setText("")
            if book_id:
                self.book_details = self.book_details + book_id  # combining tuples: after successful insert, saves book_id.
                self.cmb_title.addItem(self.book_details[0])
                self.cmb_author.addItem(self.book_details[1])
                self.update_book_table()
                self.extract_words(self.book_details[4])
                self.db.notify_new_book()  # notify relevant tabs that a new book has been added to the db.

            self.book_details = None  # resets last book's details
        else:
            display_msg(MsgIcon.WARNING, "Attention", "Please choose a book first.")

    def update_cmbs(self):
        """updates multi-selection combo boxes and table when [importing to] / [clearing the] DB.
           author's combo box is updated automatically through "update_authors_on_title_change". """
        self.cmb_title.clear()
        self.cmb_title.addItem("ALL")
        self.cmb_title.setCurrentText("ALL")
        for row in self.db.get_book_titles_authors():
            self.cmb_title.addItem(row[0])
        self.update_book_table()

    def update_authors_on_title_change(self):
        """updates authors' combo_box upon an update to current selection in titles' combo_box,
        thus assisting user by narrowing selection only to authors who might have written current title."""
        curr_title = self.cmb_title.currentText()
        curr_author = self.cmb_author.currentText()
        self.cmb_author.clear()
        self.cmb_author.addItem("ALL")
        for row in self.db.get_book_authors(curr_title):
            self.cmb_author.addItem(row[0])
        # try and restore last author the user selected in the author's list:
        index = self.cmb_author.findText(curr_author)
        self.cmb_author.setCurrentIndex(index if index != -1 else 0)
        self.update_book_table()

    def update_book_table(self):
        """ updates books table. updates when user changes selection of combo boxes or inserts a new book.  """
        title = self.cmb_title.currentText()
        author = self.cmb_author.currentText()
        self.tbl_books.setRowCount(0)  # removes the table's rows including data
        for row_pos, row in enumerate(self.db.query_book_table(title, author)):
            self.tbl_books.setRowCount(row_pos + 1)
            for column_pos in range(1, 6):  # skipping attribute book_id.
                item = QTableWidgetItem(row[column_pos])
                item.setTextAlignment(Qt.AlignHCenter)
                if column_pos == 5:
                    item.setForeground(QBrush(QColor(0, 128, 255)))
                    self.tbl_books.setItem(row_pos, column_pos - 1, item)
                else:
                    self.tbl_books.setItem(row_pos, column_pos - 1, item)

    def extract_words(self, file_name):
        """reads words parser and inserts them into the database.
        to facilitate insertion of values to the DB, values are first stockpiled and only then inserted"""
        words = set()
        instances = []
        book_id = self.book_details[-1]

        for word_data in txt_parser.get_next_word(file_name):
            words.add('(\'' + word_data[0] + '\')')
        self.db.insert_mult_word(words)

        for word_data in txt_parser.get_next_word(file_name):
            # finds the word's id and adds it to the instance's attributes
            word_id = self.db.get_word_id(word_data[0])[0]
            instances.append((word_id, word_data[1], book_id,
                              word_data[2], word_data[3], word_data[4], word_data[5]))

        self.db.insert_mult_word_instance(instances)

    def start_file(self):
        """Opens the book the user double clicked. """
        index = self.tbl_books.selectionModel().currentIndex()
        file_path = index.sibling(index.row(), 4).data()
        try:
            os.startfile(file_path)
        except WindowsError:
            display_msg(MsgIcon.WARNING, "Warning", "Cannot locate file. "
                                                    "\nCheck whether it was removed from "
                                                    "it's original location")
            return

    def explain(self):
        display_msg(MsgIcon.INFORMATION, "Information",
                    "To open a book, i.e. the original file provided, double click the associated row."
                    "\nTo remove a book, first choose desired row from the table, then click \"Remove Book\" ")

    def del_book(self):
        index = self.tbl_books.selectionModel().currentIndex()
        title = index.sibling(index.row(), 0).data()
        author = index.sibling(index.row(), 1).data()
        if title and author:  # user selected row in the table before clicking the button
            self.db.del_book(title, author)
            #self.update_cmbs()
        self.db.notify_import()  # to re-render GUI

    def tbl_config(self):
        self.tbl_books.setGeometry(QtCore.QRect(100, 540, 1150, 231))
        self.tbl_books.setStyleSheet("background-color: rgb(255, 255, 213); font: bold 16pt \"Segoe UI\"; ")
        self.tbl_books.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tbl_books.setColumnCount(5)
        self.tbl_books.setRowCount(0)
        self.tbl_books.verticalHeader().setVisible(False)
        self.tbl_books.setHorizontalHeaderItem(0, QTableWidgetItem("Title"))
        self.tbl_books.setColumnWidth(0, 300)
        self.tbl_books.horizontalHeaderItem(0).setBackground(QtGui.QColor(255, 170, 0))
        self.tbl_books.horizontalHeaderItem(0).setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.tbl_books.setHorizontalHeaderItem(1, QTableWidgetItem("Author"))
        self.tbl_books.setColumnWidth(1, 250)
        self.tbl_books.horizontalHeaderItem(1).setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.tbl_books.setHorizontalHeaderItem(2, QTableWidgetItem("Date"))
        self.tbl_books.setColumnWidth(2, 125)
        self.tbl_books.horizontalHeaderItem(2).setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.tbl_books.setHorizontalHeaderItem(3, QTableWidgetItem("Size"))
        self.tbl_books.setColumnWidth(3, 100)
        self.tbl_books.horizontalHeaderItem(3).setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.tbl_books.setHorizontalHeaderItem(4, QTableWidgetItem("Path"))
        self.tbl_books.setColumnWidth(4, 375)
        self.tbl_books.horizontalHeaderItem(4).setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.tbl_books.cellDoubleClicked.connect(self.start_file)
        self.tbl_books.setShowGrid(False)
        self.tbl_books.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # enable read-only

    def btn_config(self):
        btn_insert_book = QtWidgets.QPushButton(self)
        btn_insert_book.setGeometry(QtCore.QRect(420, 270, 451, 41))
        btn_insert_book.setStyleSheet(STYLE_BTN)
        btn_insert_book.clicked.connect(self.insert_book)
        btn_insert_book.setText("Insert Into The Database")

        btn_load_book = QtWidgets.QPushButton(self)
        btn_load_book.setGeometry(QtCore.QRect(25, 165, 200, 40))
        btn_load_book.setStyleSheet(STYLE_BTN)
        btn_load_book.clicked.connect(self.browse_book)
        btn_load_book.setText("Load a Book")

        btn_question = QtWidgets.QPushButton(self)
        btn_question.setGeometry(QtCore.QRect(1190, 490, 60, 50))
        btn_question.setStyleSheet(STYLE_BTN)
        btn_question.clicked.connect(self.explain)
        btn_question.setText("?")

        btn_del_book = QtWidgets.QPushButton(self)
        btn_del_book.setGeometry(QtCore.QRect(560, 770, 200, 40))
        btn_del_book.setStyleSheet(STYLE_BTN)
        btn_del_book.clicked.connect(self.del_book)
        btn_del_book.setText("Remove Book")

    def cmb_config(self):
        style_14pt_bold = "background-color: rgb(255, 255, 213); font: bold 14pt \"Segoe UI\"; "
        self.cmb_title.setGeometry(QtCore.QRect(280, 440, 321, 31))
        self.cmb_title.setStyleSheet(style_14pt_bold)
        self.cmb_title.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cmb_title.addItem("ALL")
        self.cmb_title.currentTextChanged.connect(self.update_authors_on_title_change)

        self.cmb_author.setGeometry(QtCore.QRect(790, 440, 361, 31))
        self.cmb_author.setStyleSheet(style_14pt_bold)
        self.cmb_author.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cmb_author.addItem("ALL")
        self.cmb_author.currentTextChanged.connect(self.update_book_table)

    def separator_config(self):
        sep_books_1 = QtWidgets.QFrame(self)
        sep_books_1.setGeometry(QtCore.QRect(200, 330, 951, 21))
        sep_books_1.setFrameShadow(QtWidgets.QFrame.Raised)
        sep_books_1.setLineWidth(4)
        sep_books_1.setMidLineWidth(0)
        sep_books_1.setFrameShape(QtWidgets.QFrame.HLine)

    def labels_config(self):
        lbl_app_header = QtWidgets.QLabel(self)
        lbl_app_header.setGeometry(QtCore.QRect(530, 20, 281, 50))
        lbl_app_header.setText(
            "<html><head/><body><p><span style=\" font-size:23pt; color:#ffffd5;text-decoration: underline;\""
            ">Library Database</span></p></body></html>")

        lbl_srch_book = QtWidgets.QLabel(self)
        lbl_srch_book.setGeometry(QtCore.QRect(510, 350, 281, 40))
        lbl_srch_book.setText(
            "<html><head/><body><p><span style=\" font-size:21pt; color:#ffffd5;text-decoration: underline;\">"
            "Books in Database:</span></p></body></html>")

        lbl_cmb_title = QtWidgets.QLabel(self)
        lbl_cmb_title.setGeometry(QtCore.QRect(210, 430, 71, 41))
        lbl_cmb_title.setText(
            "<html><head/><body><p><span style=\" font-size:18pt; color:#ffffd5;\">Title:</span></p></body></html>")

        lbl_cmb_author = QtWidgets.QLabel(self)
        lbl_cmb_author.setGeometry(QtCore.QRect(690, 430, 91, 41))
        lbl_cmb_author.setText(
            "<html><head/><body><p><span style=\" font-size:18pt; color:#ffffd5;\">Author:</span></p></body></html>")

    def img_config(self):
        self.img.setGeometry(QtCore.QRect(-10, 0, 1541, 891))
        self.img.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname('__file__'), "images/library.png")))
        self.img.setScaledContents(True)
        self.img.lower()  # set image at the background.

    def box_config(self):
        self.box_book_id.setGeometry(QtCore.QRect(250, 90, 801, 161))
        self.box_book_id.setStyleSheet("color: rgb(255, 255, 213); font: bold 18pt \"Segoe UI\"; ")
        self.box_book_id.setTitle("Book\'s Identifiers")
        self.box_book_id.setAlignment(QtCore.Qt.AlignCenter)

        self.line_author.setStyleSheet(STYLE_LINE)
        self.line_author.setAlignment(QtCore.Qt.AlignCenter)
        self.line_author.setReadOnly(True)

        self.line_date.setStyleSheet(STYLE_LINE)
        self.line_date.setAlignment(QtCore.Qt.AlignCenter)
        self.line_date.setReadOnly(True)

        self.line_title.setStyleSheet(STYLE_LINE)
        self.line_title.setAlignment(QtCore.Qt.AlignCenter)
        self.line_title.setReadOnly(True)

        lbl_date = QtWidgets.QLabel(self.box_book_id)
        lbl_date.setText(
            "<html><head/><body><p><span style=\" color:#ffffd5;\">Release Date</span></p></body></html>")

        lbl_author = QtWidgets.QLabel(self.box_book_id)
        lbl_author.setText("<html><head/><body><p><span style=\" color:#ffffd5;\">Author</span></p></body></html>")

        lbl_title = QtWidgets.QLabel(self.box_book_id)
        lbl_title.setText("<html><head/><body><p><span style=\" color:#ffffd5;\">Title</span></p></body></html>")

        grid_layout = QtWidgets.QGridLayout(self.box_book_id)
        grid_layout.addWidget(self.line_author, 1, 1, 1, 1)
        grid_layout.addWidget(lbl_date, 2, 0, 1, 1)
        grid_layout.addWidget(lbl_author, 1, 0, 1, 1)
        grid_layout.addWidget(lbl_title, 0, 0, 1, 1)
        grid_layout.addWidget(self.line_date, 2, 1, 1, 1)
        grid_layout.addWidget(self.line_title, 0, 1, 1, 1)
