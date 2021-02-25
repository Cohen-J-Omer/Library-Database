import os, re
from utils.style_constants import STYLE_LINE, STYLE_BTN_TOOLTIP
from PyQt5.QtGui import QTextCursor, QBrush, QColor
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from msg_box import MsgIcon, display_msg


class PhraseTab(QtWidgets.QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.db.tune_in_new_book(self.update_phrase_appear)
        self.db.tune_in_import(self.import_update)
        # Defining Gui attributes:
        self.tbl_phrase = QtWidgets.QTableWidget(self)
        self.cmb_phrs = QtWidgets.QComboBox(self)
        self.line_input_phrs = QtWidgets.QLineEdit(self)
        self.img = QtWidgets.QLabel(self)
        self.txt_phrs_appr = QtWidgets.QTextBrowser(self)
        # configuring aforementioned Gui attributes:
        self.tbl_config()
        self.input_config()
        self.button_config()
        self.preview_txt_config()
        self.labels_config()
        self.img_config()

    def create_phrase(self):
        """connects DB to insert phrase and the words within the phrase, if valid values were given."""
        text = self.line_input_phrs.text().lower().strip()  # removes redundant spaces and return lower case
        self.line_input_phrs.setText("")
        words = re.findall(r'\w+', text)
        if len(words) < 2:
            display_msg(MsgIcon.WARNING, "Warning",
                        "Please write a complete phrase, which contains upwards of two words.")
            return

        phrase_id = self.db.insert_phrase(text)
        if phrase_id:  # if phrase has been added to the DB, attribute phrase_words to phrase:

            for offset, word in enumerate(words):

                # bypassing cache to get id straight from the DB to avoid automatically returning
                # None values from cache, in case word was foreign to DB on last function call.
                word_id = self.db.get_word_id.__wrapped__(self.db, word)

                if not word_id:  # insert words in phrase that don't exist in DB and get their id
                    word_id = self.db.insert_word(word)
                self.db.insert_word_in_phrase(word_id[0], phrase_id, offset)
            self.cmb_phrs.addItem(text)  # update combo_box
            self.db.notify_stats()  # update stats tab

    def import_update(self):
        """Updates combo boxes and clears the table and the text_browser when user imports to DB."""
        self.txt_phrs_appr.clear()
        self.cmb_phrs.clear()
        self.cmb_phrs.addItem("Select a Phrase")
        for phrase in self.db.get_phrases():
            self.cmb_phrs.addItem(phrase[0])
        self.cmb_phrs.setCurrentIndex(0)  # resetting to default selection

    def update_phrase_appear(self):
        """ updates phrase occurrences when user selects a phrase or adds a new book. """
        self.txt_phrs_appr.clear()
        self.tbl_phrase.setRowCount(0)
        phrase_txt = self.cmb_phrs.currentText()

        if phrase_txt != '' and phrase_txt != 'Select a Phrase' and self.db.get_sum_books() > 0:
            for row_pos, row in enumerate(self.db.get_phrase_appear(phrase_txt)):
                self.tbl_phrase.setRowCount(row_pos + 1)
                for column_pos in range(6):
                    item = QTableWidgetItem(str(row[column_pos]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tbl_phrase.setItem(row_pos, column_pos, item)

    def update_preview(self):
        """ writes text surrounding selected word to text browser and highlights it """
        self.txt_phrs_appr.clear()
        index = self.tbl_phrase.selectionModel().currentIndex()
        title = index.sibling(index.row(), 0).data()
        author = index.sibling(index.row(), 1).data()
        line = int(index.sibling(index.row(), 4).data())
        line_index = int(index.sibling(index.row(), 5).data())
        path = self.db.get_book_path(title, author)
        phrase_txt = self.cmb_phrs.currentText()  # used to set cursor at the end of the phrase
        wrd_txt = phrase_txt.split(" ")[0]  # gets the first word of the phrase. used in get_char_offset()

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
                # writing lines, surrounding the phrase, into the preview
                for line_no, row in enumerate(file, start=1):
                    end -= 1
                    if end < 0:
                        break
                    if line_no == relative_line:
                        char_offset = self.get_char_offset(wrd_txt, row.lower(), line_index)

                    # following 3 rows replaces append() line, to abstain from adding an
                    # empty line with every row.
                    self.txt_phrs_appr.moveCursor(QTextCursor.End)
                    self.txt_phrs_appr.insertPlainText(row)
                    self.txt_phrs_appr.moveCursor(QTextCursor.End)

        except IOError:
            display_msg(MsgIcon.WARNING, "Warning", "failed to load preview. \n could not find / open file")
            return

        # Marks, within the text preview, the exact phrase instance the user selected:
        self.mark_selected_phrase(relative_line, char_offset, len(phrase_txt))

    def get_char_offset(self, target_word, line, line_index):
        """ :returns the character index of target_word in line provided"""

        # gets occurrence number of target_word in provided line
        occurrence = 0
        for word_index, word in enumerate(re.findall(r'\w+', line)):
            if word == target_word:
                occurrence += 1
            if word_index == line_index:
                break

        # returns the index of the required (as calculated above) occurrence of target_word
        matches = re.finditer(r'\b' + target_word + r'\b', line, re.MULTILINE)
        for num, match in enumerate(matches, start=1):  # start = 1, since occurrence is 1 based index.
            if num == occurrence:
                return match.span()[0]

    def mark_selected_phrase(self, relative_line, char_offset, phrase_len):
        cursor = self.txt_phrs_appr.textCursor()
        # defining format to mark selected phrase with:
        fmt = self.txt_phrs_appr.textCursor().charFormat()
        fmt.setBackground(QBrush(QColor(220, 220, 20, 200)))
        # reset cursor position to the beginning
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
        # move it down to the right line
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, relative_line - 1)
        # set cursor down to the word in search, to avoid having to scroll down to the highlighted word
        self.txt_phrs_appr.setTextCursor(cursor)
        # position cursor at the beginning of the word
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, char_offset)
        # move cursor to the end of the word
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, phrase_len)
        # apply format (defined earlier) on text between cursor position at MoveAnchor and KeepAnchor
        cursor.mergeCharFormat(fmt)

    def del_phrase(self):
        """removes a previously entered phrase from the database and updates statistics """
        phrase = self.cmb_phrs.currentText()
        if phrase != 'Select a Phrase':
            self.db.del_phrase(phrase)
            self.update_phrases()
            self.db.notify_stats()

    def update_phrases(self):
        self.cmb_phrs.clear()
        self.cmb_phrs.addItem('Select a Phrase')
        for phrase in self.db.get_phrases():
            self.cmb_phrs.addItem(phrase[0])

    def labels_config(self):
        lbl_srch_phrs = QtWidgets.QLabel(self)
        lbl_srch_phrs.setGeometry(QtCore.QRect(520, 30, 341, 41))
        lbl_srch_phrs.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; "
                              "text-decoration: underline; color:#ffffd5;\">Search Custom Phrases:"
                              "</span></p></body></html>")

        lbl_sel_phrs = QtWidgets.QLabel(self)
        lbl_sel_phrs.setGeometry(QtCore.QRect(230, 190, 271, 31))
        lbl_sel_phrs.setText(
            "<html><head/><body><p><span style=\" font-size:18pt; color:#ffffd5;\">Select a phrase:</span></p></body></html>")

        lbl_ent_phrase = QtWidgets.QLabel(self)
        lbl_ent_phrase.setGeometry(QtCore.QRect(230, 90, 271, 31))
        lbl_ent_phrase.setText(
            "<html><head/><body><p><span style=\" font-size:18pt; color:#ffffd5;\">Enter a new phrase:</span></p></body></html>")

        lbl_res_phrs = QtWidgets.QLabel(self)
        lbl_res_phrs.setEnabled(True)
        lbl_res_phrs.setGeometry(QtCore.QRect(440, 240, 490, 50))
        lbl_res_phrs.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:19pt; text-decoration: underline; "
            "color:#ffffd5;\">Occurrences of Selected Phrase:</span></p></body></html>")

        lbl_phrs_appr = QtWidgets.QLabel(self)
        lbl_phrs_appr.setGeometry(QtCore.QRect(490, 540, 420, 50))
        lbl_phrs_appr.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:19pt; text-decoration: underline; "
            "color:#ffffd5;\">Preview of Selected Occurrence:</span></p></body></html>")

    def img_config(self):
        self.img.setGeometry(QtCore.QRect(-10, 0, 1541, 891))
        self.img.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname('__file__'), "images/library.png")))
        self.img.setScaledContents(True)
        self.img.lower()  # set image at the background.

    def tbl_config(self):
        self.tbl_phrase.setGeometry(QtCore.QRect(290, 290, 801, 251))
        self.tbl_phrase.setStyleSheet("background-color: rgb(255, 255, 213);\n"
                                      "font: bold 16pt \"Segoe UI\";")
        self.tbl_phrase.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tbl_phrase.setColumnCount(6)
        self.tbl_phrase.setRowCount(0)
        self.tbl_phrase.setHorizontalHeaderItem(0, QTableWidgetItem("Book"))
        self.tbl_phrase.setColumnWidth(0, 200)
        self.tbl_phrase.setHorizontalHeaderItem(1, QTableWidgetItem("Author"))
        self.tbl_phrase.setColumnWidth(1, 200)
        self.tbl_phrase.setHorizontalHeaderItem(2, QTableWidgetItem("Par."))
        self.tbl_phrase.setColumnWidth(2, 75)
        self.tbl_phrase.setHorizontalHeaderItem(3, QTableWidgetItem("Sentence"))
        self.tbl_phrase.setColumnWidth(3, 110)
        self.tbl_phrase.setHorizontalHeaderItem(4, QTableWidgetItem("Line"))
        self.tbl_phrase.setColumnWidth(4, 90)
        self.tbl_phrase.setHorizontalHeaderItem(5, QTableWidgetItem("Index"))
        self.tbl_phrase.setColumnWidth(5, 105)
        self.tbl_phrase.verticalHeader().setVisible(False)
        self.tbl_phrase.setShowGrid(False)
        self.tbl_phrase.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # enable read-only
        self.tbl_phrase.cellClicked.connect(self.update_preview)

    def input_config(self):
        self.cmb_phrs.setGeometry(QtCore.QRect(480, 190, 511, 31))
        self.cmb_phrs.setStyleSheet(STYLE_LINE)
        self.cmb_phrs.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.cmb_phrs.addItem("Select a Phrase")
        self.cmb_phrs.currentTextChanged.connect(self.update_phrase_appear)

        self.line_input_phrs.setGeometry(QtCore.QRect(480, 90, 511, 31))
        self.line_input_phrs.setStyleSheet(STYLE_LINE)
        self.line_input_phrs.setAlignment(QtCore.Qt.AlignCenter)

    def button_config(self):
        btn_add_phrs = QtWidgets.QPushButton(self)
        btn_add_phrs.setGeometry(QtCore.QRect(660, 135, 141, 41))
        btn_add_phrs.setToolTip("Store phrase for later look-ups")
        btn_add_phrs.setStyleSheet(STYLE_BTN_TOOLTIP)
        btn_add_phrs.setText("Add")
        btn_add_phrs.clicked.connect(self.create_phrase)

        btn_del_phrs = QtWidgets.QPushButton(self)
        btn_del_phrs.setGeometry(QtCore.QRect(1010, 180, 141, 41))
        btn_del_phrs.setToolTip("Remove selected phrase")
        btn_del_phrs.setStyleSheet(STYLE_BTN_TOOLTIP)
        btn_del_phrs.setText("Remove")
        btn_del_phrs.clicked.connect(self.del_phrase)

    def preview_txt_config(self):
        self.txt_phrs_appr.setGeometry(QtCore.QRect(290, 590, 801, 231))
        self.txt_phrs_appr.setStyleSheet(STYLE_LINE)
        self.txt_phrs_appr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.txt_phrs_appr.setReadOnly(True)
