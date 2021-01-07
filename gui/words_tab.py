import re,os
from msg_box import MsgIcon, display_msg

from PyQt5.QtGui import QFont, QTextCursor, QColor, QBrush
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from utils.style_constants import STYLE_LINE_TOOLTIP, STYLE_LINE, STYLE_BTN


class ComboBox(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        """ override showPopup by first emitting signal before displaying items.
            signal will be caught and lead to an update on this combo box's items """
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()


class WordsTab(QtWidgets.QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.db.tune_in_new_book(self.update)
        self.db.tune_in_import(self.update)
        self.last_search_filters = []
        # Defining Gui attributes:
        self.tbl_word_appr = QtWidgets.QTableWidget(self)
        self.tbl_res = QtWidgets.QTableWidget(self)
        self.box_filter = QtWidgets.QGroupBox(self)
        self.cmb_books = QtWidgets.QComboBox(self.box_filter)
        self.cmb_grp = ComboBox(self.box_filter)
        self.line_wrd = QtWidgets.QLineEdit(self.box_filter)
        self.line_par = QtWidgets.QLineEdit(self.box_filter)
        self.line_line = QtWidgets.QLineEdit(self.box_filter)
        self.line_line_ind = QtWidgets.QLineEdit(self.box_filter)
        self.line_sentence = QtWidgets.QLineEdit(self.box_filter)
        self.btn_srch_wrd = QtWidgets.QPushButton(self.box_filter)
        self.txt_wrd_appr = QtWidgets.QTextEdit(self)
        self.img = QtWidgets.QLabel(self)
        # configuring aforementioned Gui attributes:
        self.tbl_word_appr_config()
        self.tbl_res_config()
        self.search_filters_config()
        self.labels_config()
        self.preview_txt_config()
        self.img_config()

    def update(self):
        """Updates key widgets in words_tab. Called upon in case user imports or clears DB"""
        self.update_cmb_books()
        self.update_word_list()
        self.update_cmb_groups()

    def update_cmb_books(self):
        """Updates available books selection when user either enters a new book, or imports / clears DB. """
        curr_selection = self.cmb_books.currentText()
        self.cmb_books.clear()
        self.cmb_books.addItem("All Books")
        for title_and_author in self.db.get_book_titles_authors():
            self.cmb_books.addItem(title_and_author[0] + " by " + title_and_author[1])
        # resetting to former book selection
        index = self.cmb_books.findText(curr_selection)
        self.cmb_books.setCurrentIndex(index)

    def update_cmb_groups(self):
        """Updates groups selection in selection box.
         Triggered manually by clicking the box or when user imports/clears DB. """
        curr_selection = self.cmb_grp.currentText()
        self.cmb_grp.clear()
        self.cmb_grp.addItem("None")
        for group in self.db.get_groups():
            self.cmb_grp.addItem(group[0])
        # resetting to former group selection
        index = self.cmb_grp.findText(curr_selection)
        self.cmb_grp.setCurrentIndex(index if index != -1 else 0)  # condition needed when user clears DB

    def get_filters(self):
        """:returns user inserted filters, adjusted to database's values. """

        book_id = "All Books"
        if self.cmb_books.currentText() != "All Books":
            matches = re.search(r'([\s\S]*) by ([\s\S]*)', self.cmb_books.currentText())
            book_id = self.db.get_book_id(matches.group(1), matches.group(2))[0]

        word_txt = self.line_wrd.text().strip()
        if len(word_txt.split(" ")) > 1:
            display_msg(MsgIcon.WARNING, "Warning", "Please enter a *single* word")
            return
        if word_txt == '':
            word_id = ''  # empty string is a flag that indicates that user hasn't chosen to filter words
        else:
            if self.cmb_grp.currentText() != 'None':
                display_msg(MsgIcon.INFORMATION, "Take Notice",
                            "Attention: \n1.) By opting to search for words within a selected group, the single "
                            "word you chose separately will be ignored.\n2.) In case you'd like to incorporate "
                            "it in the search alongside the group, consider adding it to said group.")
            self.db.clear_cache()
            word_id = self.db.get_word_id(word_txt)
            if word_id:  # handles None in case word doesn't exist in DB, i.e - in the books.
                word_id = word_id[0]

        # since none int types are converted to 0 in MySQL when compared with int type such as line_index
        # and since this is the only variable that 0 is a viable value for it, it has a special edge case:
        # if line_index isn't spaces and isn't numeric, a query for word list cannot return anything
        # else other than an empty result set.
        offset = self.line_line_ind.text().strip()
        if offset and not offset.isnumeric():
            return

        return [book_id, word_id, self.cmb_grp.currentText(), self.line_par.text(),
                self.line_line.text(), offset, self.line_sentence.text()]

    def update_word_list(self):
        """Updates list of results (words) filtered by user (filter func). triggered by "Search" button. """
        # after user clicks "Search" the search parameters will be saved until overridden by next search.
        self.last_search_filters = self.get_filters()
        self.tbl_res.setRowCount(0)
        self.tbl_word_appr.setRowCount(0)  # resets tbl_word_appr where instances of last word picked were displayed
        self.txt_wrd_appr.clear()  # clean preview text area in case it was written to during the last query

        for row_pos, row in enumerate(self.db.get_wrd_res(self.last_search_filters)):
            self.tbl_res.setRowCount(row_pos + 1)
            for column_pos in range(0, 2):
                item = QTableWidgetItem(str(row[column_pos]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tbl_res.setItem(row_pos, column_pos, item)

    def update_word_instances(self):
        """ word instances are shown based on the state of filters when Search button was pressed,
            thus allowing user to edit filters without necessarily committing to them."""
        self.db.clear_cache()
        index = self.tbl_res.selectionModel().currentIndex()
        wrd_txt = index.sibling(index.row(), 0).data()
        filters = self.last_search_filters  # use filters user chose at the time of search
        filters[1] = self.db.get_word_id(wrd_txt)[0]  # getting word_id fitting to user's latest choice
        self.tbl_word_appr.setRowCount(0)
        for row_pos, row in enumerate(self.db.get_wrd_instances(filters)):
            self.tbl_word_appr.setRowCount(row_pos + 1)
            for column_pos in range(0, 6):
                item = QTableWidgetItem(str(row[column_pos]))
                item.setTextAlignment(Qt.AlignHCenter)
                self.tbl_word_appr.setItem(row_pos, column_pos, item)

    def update_preview(self):
        """ writes text surrounding selected word to text browser """
        self.txt_wrd_appr.clear()
        index = self.tbl_word_appr.selectionModel().currentIndex()
        title = index.sibling(index.row(), 0).data()
        author = index.sibling(index.row(), 1).data()
        line = int(index.sibling(index.row(), 4).data())
        line_index = int(index.sibling(index.row(), 5).data())
        path = self.db.get_book_path(title, author)
        index = self.tbl_res.selectionModel().currentIndex()
        wrd_txt = index.sibling(index.row(), 0).data()

        radius = 15
        start, end, relative_line, char_offset = line - radius, 2 * radius, radius, 1
        if line < radius:
            start = 0
            end = 3 * radius - line
            relative_line = line

        try:
            with open(path, 'r') as file:
                for _ in range(start):  # skipping rows in file to starting point
                    next(file)
                for line_no, row in enumerate(file, start=1):
                    end -= 1
                    if end < 0:
                        break
                    if line_no == relative_line:
                        char_offset = self.get_char_offset(wrd_txt, row.lower(), line_index)

                    # following 3 rows replaces append() to abstain from adding a new line with every row.
                    self.txt_wrd_appr.moveCursor(QTextCursor.End)
                    self.txt_wrd_appr.insertPlainText(row)
                    self.txt_wrd_appr.moveCursor(QTextCursor.End)

        except IOError:
            display_msg(MsgIcon.WARNING, "Warning", "failed to load preview. \n could not find / open file")
            return

        # Marks, within the text preview, the exact word instance the user selected:
        self.mark_selected_word(relative_line, char_offset, len(wrd_txt))

    def get_char_offset(self, target_word, line, line_index):
        """ :returns the character index of target_word in line provided. update_preview's helper func."""

        # gets occurrence number of target_word
        occurrence = 0
        for word_index, word in enumerate(re.findall(r'\w+', line)):
            if word == target_word:
                occurrence += 1
            if word_index == line_index:
                break

        matches = re.finditer(r'\b' + target_word + r'\b', line, re.MULTILINE)
        for num, match in enumerate(matches, start=1):
            if num == occurrence:
                return match.span()[0]

    def mark_selected_word(self, relative_line, char_offset, word_len):
        cursor = self.txt_wrd_appr.textCursor()
        # defining format to mark selected word with:
        fmt = self.txt_wrd_appr.textCursor().charFormat()
        fmt.setBackground(QBrush(QColor(220, 220, 20, 200)))
        # reset cursor position to the beginning
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        # move it down to the right line
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, relative_line - 1)
        # scroll scrollbar down to the word in search, so it would appear in the current page of the text browser
        self.txt_wrd_appr.setTextCursor(cursor)
        # position cursor at the beginning of the word
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, char_offset)
        # move cursor to the end of the word
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, word_len)
        # apply format (defined earlier) on text between cursor position at MoveAnchor and KeepAnchor
        cursor.mergeCharFormat(fmt)

    def img_config(self):
        self.img.setGeometry(QtCore.QRect(-10, 0, 1541, 891))
        self.img.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname('__file__'), "images/library.png")))
        self.img.setScaledContents(True)
        self.img.lower()  # set image at the background.

    def tbl_word_appr_config(self):
        self.tbl_word_appr.setGeometry(QtCore.QRect(430, 250, 791, 251))
        self.tbl_word_appr.setStyleSheet("background-color: rgb(255, 255, 213);\n"
                                         "font: bold 16pt \"Segoe UI\";")
        self.tbl_word_appr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tbl_word_appr.setColumnCount(6)
        self.tbl_word_appr.setRowCount(0)
        self.tbl_word_appr.setHorizontalHeaderItem(0, QTableWidgetItem("Book"))
        self.tbl_word_appr.setColumnWidth(0, 200)
        self.tbl_word_appr.setHorizontalHeaderItem(1, QTableWidgetItem("Author"))
        self.tbl_word_appr.setColumnWidth(1, 200)
        self.tbl_word_appr.setHorizontalHeaderItem(2, QTableWidgetItem("Par."))
        self.tbl_word_appr.setColumnWidth(2, 75)
        self.tbl_word_appr.setHorizontalHeaderItem(3, QTableWidgetItem("Sentence"))
        self.tbl_word_appr.setColumnWidth(3, 110)
        self.tbl_word_appr.setHorizontalHeaderItem(4, QTableWidgetItem("Line"))
        self.tbl_word_appr.setColumnWidth(4, 90)
        self.tbl_word_appr.setHorizontalHeaderItem(5, QTableWidgetItem("Index"))
        self.tbl_word_appr.setColumnWidth(5, 95)
        self.tbl_word_appr.setShowGrid(False)
        self.tbl_word_appr.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # enable read-only

        self.tbl_word_appr.verticalHeader().setVisible(False)
        self.tbl_word_appr.cellClicked.connect(self.update_preview)

    def tbl_res_config(self):
        self.tbl_res.setGeometry(QtCore.QRect(50, 250, 311, 570))
        self.tbl_res.setStyleSheet("background-color: rgb(255, 255, 213); font: bold 16pt \"Segoe UI\"; ")
        self.tbl_res.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tbl_res.setColumnCount(2)
        self.tbl_res.setRowCount(0)
        self.tbl_res.verticalHeader().setVisible(False)
        self.tbl_res.setHorizontalHeaderItem(0, QTableWidgetItem("Word"))
        self.tbl_res.setColumnWidth(0, 150)
        self.tbl_res.horizontalHeaderItem(0).setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.tbl_res.setHorizontalHeaderItem(1, QTableWidgetItem("Instances"))
        self.tbl_res.setColumnWidth(1, 140)
        self.tbl_res.horizontalHeaderItem(1).setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.tbl_res.setShowGrid(False)
        self.tbl_res.cellClicked.connect(self.update_word_instances)
        self.tbl_res.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def labels_config(self):
        self.box_filter.setGeometry(QtCore.QRect(60, 10, 1171, 171))
        self.box_filter.setStyleSheet("font: bold 18pt \"Segoe UI\";\n"
                                      "color: rgb(255, 255, 213);")
        self.box_filter.setTitle("Search Filters")
        self.box_filter.setAlignment(QtCore.Qt.AlignCenter)

        lbl_res = QtWidgets.QLabel(self)
        lbl_res.setGeometry(QtCore.QRect(70, 190, 271, 51))
        lbl_res.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; text-decoration: underline; "
            "color:#ffffd5;\">Search Results:</span></p></body></html>")

        lbl_appr = QtWidgets.QLabel(self)
        lbl_appr.setGeometry(QtCore.QRect(590, 190, 431, 51))
        lbl_appr.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; text-decoration: underline; "
            "color:#ffffd5;\">Occurrences of Selected Word:</span></p></body></html>")

        lbl_wrd_preview = QtWidgets.QLabel(self)
        lbl_wrd_preview.setGeometry(QtCore.QRect(590, 520, 431, 51))
        lbl_wrd_preview.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; text-decoration: underline; "
            "color:#ffffd5;\">Preview of Selected Occurrence:</span></p></body></html>")

        lbl_sel_book = QtWidgets.QLabel(self.box_filter)
        lbl_sel_book.setGeometry(QtCore.QRect(10, 30, 124, 29))
        lbl_sel_book.setText(
            "<html><head/><body><p><span style=\" font-size:16pt; color:#ffffd5;\">Search in</span></p></body></html>")

        lbl_wrd = QtWidgets.QLabel(self.box_filter)
        lbl_wrd.setGeometry(QtCore.QRect(420, 30, 124, 29))
        lbl_wrd.setText(
            "<html><head/><body><p><span style=\" font-size:16pt; color:#ffffd5;\">Search word</span></p></body></html>")

        lbl_grp = QtWidgets.QLabel(self.box_filter)
        lbl_grp.setGeometry(QtCore.QRect(810, 30, 124, 29))
        lbl_grp.setText(
            "<html><head/><body><p><span style=\" font-size:14pt; color:#ffffd5;\">Word group</span></p></body></html>")

        lbl_par = QtWidgets.QLabel(self.box_filter)
        lbl_par.setGeometry(QtCore.QRect(10, 80, 124, 29))
        lbl_par.setText(
            "<html><head/><body><p><span style=\" font-size:16pt; color:#ffffd5;\">Paragraph</span></p></body></html>")

        lbl_line = QtWidgets.QLabel(self.box_filter)
        lbl_line.setGeometry(QtCore.QRect(420, 80, 124, 29))
        lbl_line.setText(
            "<html><head/><body><p><span style=\" font-size:16pt; color:#ffffd5;\">Line</span></p></body></html>")

        lbl_sent = QtWidgets.QLabel(self.box_filter)
        lbl_sent.setGeometry(QtCore.QRect(10, 130, 124, 29))
        lbl_sent.setText(
            "<html><head/><body><p><span style=\" font-size:16pt; color:#ffffd5;\">Sentence</span></p></body></html>")

        lbl_line_ind = QtWidgets.QLabel(self.box_filter)
        lbl_line_ind.setGeometry(QtCore.QRect(810, 80, 124, 29))
        lbl_line_ind.setToolTip("Word index in line")
        lbl_line_ind.setText(
            "<html><head/><body><p><span style=\" font-size:16pt; color:#ffffd5;\">Line index</span></p></body></html>")
        lbl_line_ind.setStyleSheet(STYLE_LINE_TOOLTIP)

    def search_filters_config(self):
        self.line_wrd.setGeometry(QtCore.QRect(560, 30, 231, 29))
        self.line_wrd.setStyleSheet(STYLE_LINE)
        self.line_wrd.setAlignment(QtCore.Qt.AlignCenter)

        self.cmb_books.setGeometry(QtCore.QRect(120, 30, 271, 31))
        self.cmb_books.setStyleSheet("background-color: rgb(255, 255, 213);\n"
                                     "font: bold 14pt \"Segoe UI\";\n"
                                     "color: rgb(0, 0, 0);")
        self.cmb_books.addItem("All Books")
        self.cmb_books.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.cmb_grp.setGeometry(QtCore.QRect(940, 30, 191, 31))
        self.cmb_grp.setStyleSheet("background-color: rgb(255, 255, 213);\n"
                                   "font: bold 14pt \"Segoe UI\";\n"
                                   "color: rgb(0, 0, 0);")
        self.cmb_grp.addItem("None")
        self.cmb_grp.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.cmb_grp.popupAboutToBeShown.connect(self.update_cmb_groups)

        self.line_par.setGeometry(QtCore.QRect(120, 80, 231, 29))
        self.line_par.setStyleSheet(STYLE_LINE)
        self.line_par.setAlignment(QtCore.Qt.AlignCenter)

        self.line_line.setGeometry(QtCore.QRect(560, 80, 231, 29))
        self.line_line.setStyleSheet(STYLE_LINE)
        self.line_line.setAlignment(QtCore.Qt.AlignCenter)

        self.line_line_ind.setGeometry(QtCore.QRect(940, 80, 191, 31))
        self.line_line_ind.setStyleSheet(STYLE_LINE)
        self.line_line_ind.setAlignment(QtCore.Qt.AlignCenter)

        self.line_sentence.setGeometry(QtCore.QRect(120, 130, 231, 29))
        self.line_sentence.setStyleSheet(STYLE_LINE)
        self.line_sentence.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_srch_wrd.setGeometry(QtCore.QRect(590, 120, 161, 41))
        self.btn_srch_wrd.setStyleSheet(STYLE_BTN)
        self.btn_srch_wrd.setText("Search")
        self.btn_srch_wrd.clicked.connect(self.update_word_list)

    def preview_txt_config(self):
        self.txt_wrd_appr.setGeometry(QtCore.QRect(425, 580, 801, 231))
        self.txt_wrd_appr.setStyleSheet(STYLE_LINE)
        self.txt_wrd_appr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.txt_wrd_appr.setReadOnly(True)

