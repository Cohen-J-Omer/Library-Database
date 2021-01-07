import os, re
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


class StatsTab(QtWidgets.QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.db.tune_in_new_book(self.new_book_update)
        self.db.tune_in_import(self.import_update)
        self.db.tune_in_stats(self.update_phrase_and_group)
        # Defining Gui attributes:
        self.tbl_freq = QtWidgets.QTableWidget(self)
        self.box_stats = QtWidgets.QGroupBox(self)
        self.box_word_stats = QtWidgets.QGroupBox(self)
        self.box_char_stats = QtWidgets.QGroupBox(self)
        self.img = QtWidgets.QLabel(self)
        # labels of general_stats:
        self.lbl_book_num = QtWidgets.QLabel(self.box_stats)
        self.lbl_size = QtWidgets.QLabel(self.box_stats)
        self.lbl_num_phrs = QtWidgets.QLabel(self.box_stats)
        self.lbl_grp_num = QtWidgets.QLabel(self.box_stats)
        self.lbl_par_num = QtWidgets.QLabel(self.box_stats)
        self.lbl_line_num = QtWidgets.QLabel(self.box_stats)
        self.lbl_sen_num = QtWidgets.QLabel(self.box_stats)
        # labels of words_stats:
        self.lbl_wrd_num = QtWidgets.QLabel(self.box_word_stats)
        self.lbl_unq_wrd = QtWidgets.QLabel(self.box_word_stats)
        self.lbl_avg_wrd_par = QtWidgets.QLabel(self.box_word_stats)
        self.lbl_avg_wrd_sen = QtWidgets.QLabel(self.box_word_stats)
        self.lbl_avg_wrd_line = QtWidgets.QLabel(self.box_word_stats)
        self.lbl_avg_wrd_book = QtWidgets.QLabel(self.box_word_stats)
        # labels of words_stats:
        self.lbl_chr_num = QtWidgets.QLabel(self.box_char_stats)
        self.lbl_avg_chr_par = QtWidgets.QLabel(self.box_char_stats)
        self.lbl_avg_chr_sen = QtWidgets.QLabel(self.box_char_stats)
        self.lbl_avg_chr_line = QtWidgets.QLabel(self.box_char_stats)
        self.lbl_avg_chr_book = QtWidgets.QLabel(self.box_char_stats)
        self.lbl_avg_chr_wrd = QtWidgets.QLabel(self.box_char_stats)
        # configuring aforementioned Gui attributes:
        self.tbl_config()
        self.general_stats_config()
        self.words_stats_config()
        self.char_stats_config()
        self.labels_config()
        self.img_config()

    def update_phrase_and_group(self):
        """Updates phrase and group labels when new ones are added.
          designed to benefit performance by updating specific values rather than the whole tab. """
        self.lbl_grp_num.setText(re.split(r'\d', self.lbl_grp_num.text())[0]
                                 + str(self.db.get_sum_groups()))
        self.lbl_num_phrs.setText(re.split(r'\d', self.lbl_num_phrs.text())[0] +
                                  str(self.db.get_sum_phrases()))

    def import_update(self):
        """Piggybacking on existing new_book_update, to update stats from scratch rather
        than incrementally. clear utility also calls this function."""
        self.new_book_update(True)

    def new_book_update(self, importing=False):
        """Updates widgets in stats_tab when user enters a new book or imports (with flag = true)"""
        self.update_tbl()
        self.update_labels(importing)

    def update_tbl(self):
        """Updates words frequency table. """
        self.tbl_freq.setRowCount(0)
        for row_num, row in enumerate(self.db.get_wrd_freq()):
            self.tbl_freq.setRowCount(row_num + 1)
            for column_pos in range(0, 3):
                item = QTableWidgetItem(str(row[column_pos - 1])) if column_pos \
                    else QTableWidgetItem(str(row_num + 1))
                item.setTextAlignment(Qt.AlignCenter)
                self.tbl_freq.setItem(row_num, column_pos, item)

    def update_labels(self, importing):
        """Updates labels to represent statistical values regarding current DB state.
        params: importing - flag that dictates whether stats should:
        1. be calculated from scratch, when importing or clearing the catch
        or
        2. updated with latest book added, when a new book is added to the database,
        which greatly contributes to run-time performance """

        if importing:
            last_book_inserted = 'All'
        else:  # user added a new book to the database
            last_book_inserted = self.db.get_last_book()

        books = self.db.get_sum_books()
        size = round(self.db.get_sum_size(), 2)
        phrases = self.db.get_sum_phrases()
        groups = self.db.get_sum_groups()

        paragraphs = 0 if not books else self.db.get_sum_par(last_book_inserted)
        if not importing:
            paragraphs += int(re.split(r':', self.lbl_par_num.text())[1])

        lines = 0 if not books else self.db.get_sum_line(last_book_inserted)
        if not importing:
            lines += int(re.split(r':', self.lbl_line_num.text())[1])

        sentences = 0 if not books else self.db.get_sum_sent(last_book_inserted)
        if not importing:
            sentences += int(re.split(r':', self.lbl_sen_num.text())[1])

        words = 0 if not books else self.db.get_overall_words(last_book_inserted)
        if not importing:
            words += int(re.split(r':', self.lbl_wrd_num.text())[1])

        unq_words = 0 if not books else self.db.get_unique_words()

        chars = 0 if not books else self.db.get_sum_char(last_book_inserted)
        if not importing:
            chars += int(re.split(r':', self.lbl_chr_num.text())[1])

        # update the value part of 19 of labels presented to user:

        self.lbl_book_num.setText(re.split(r'\d', self.lbl_book_num.text())[0] + str(books))
        self.lbl_size.setText(re.split(r'\d', self.lbl_size.text())[0] + str(size))
        self.lbl_num_phrs.setText(re.split(r'\d', self.lbl_num_phrs.text())[0] + str(phrases))
        self.lbl_grp_num.setText(re.split(r'\d', self.lbl_grp_num.text())[0] + str(groups))
        self.lbl_par_num.setText(re.split(r'\d', self.lbl_par_num.text())[0] + str(paragraphs))
        self.lbl_line_num.setText(re.split(r'\d', self.lbl_line_num.text())[0] + str(lines))
        self.lbl_sen_num.setText(re.split(r'\d', self.lbl_sen_num.text())[0] + str(sentences))

        self.lbl_wrd_num.setText(re.split(r'\d', self.lbl_wrd_num.text())[0] + str(words))
        self.lbl_unq_wrd.setText(re.split(r'\d', self.lbl_unq_wrd.text())[0] + str(unq_words))
        self.lbl_avg_wrd_par.setText(re.split(r'\d', self.lbl_avg_wrd_par.text())[0] +
                                     str(0 if paragraphs == 0 else round(words / paragraphs)))
        self.lbl_avg_wrd_sen.setText(re.split(r'\d', self.lbl_avg_wrd_sen.text())[0] +
                                     str(0 if paragraphs == 0 else round(words / sentences)))
        self.lbl_avg_wrd_line.setText(re.split(r'\d', self.lbl_avg_wrd_line.text())[0] +
                                      str(0 if paragraphs == 0 else round(words / lines)))
        self.lbl_avg_wrd_book.setText(re.split(r'\d', self.lbl_avg_wrd_book.text())[0] +
                                      str(0 if paragraphs == 0 else round(words / books)))

        self.lbl_chr_num.setText(re.split(r'\d', self.lbl_chr_num.text())[0] + str(chars))
        self.lbl_avg_chr_par.setText(re.split(r'\d', self.lbl_avg_chr_par.text())[0] +
                                     str(0 if paragraphs == 0 else round(chars / paragraphs)))
        self.lbl_avg_chr_sen.setText(re.split(r'\d', self.lbl_avg_chr_sen.text())[0] +
                                     str(0 if paragraphs == 0 else round(chars / sentences)))
        self.lbl_avg_chr_line.setText(re.split(r'\d', self.lbl_avg_chr_line.text())[0] +
                                      str(0 if paragraphs == 0 else round(chars / lines)))
        self.lbl_avg_chr_wrd.setText(re.split(r'\d', self.lbl_avg_chr_wrd.text())[0] +
                                     str(0 if paragraphs == 0 else round(chars / words)))
        self.lbl_avg_chr_book.setText(re.split(r'\d', self.lbl_avg_chr_book.text())[0] +
                                      str(0 if paragraphs == 0 else round(chars / books)))

    def img_config(self):
        self.img.setGeometry(QtCore.QRect(-10, 0, 1541, 891))
        self.img.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname('__file__'), "images/library.png")))
        self.img.setScaledContents(True)
        self.img.lower()  # set image at the background.

    def general_stats_config(self):
        self.box_stats.setGeometry(QtCore.QRect(470, 20, 831, 201))
        self.box_stats.setStyleSheet("font: bold 16pt \"Segoe UI\"; color: rgb(255, 255, 213);")
        self.box_stats.setTitle("General Statistics")
        self.box_stats.setAlignment(QtCore.Qt.AlignCenter)

        self.lbl_book_num.setGeometry(QtCore.QRect(20, 40, 261, 29))
        self.lbl_book_num.setText("Overall books: 0")

        self.lbl_size.setGeometry(QtCore.QRect(290, 40, 271, 29))
        self.lbl_size.setText("Overall size(MB): 0")

        self.lbl_num_phrs.setGeometry(QtCore.QRect(570, 40, 261, 29))
        self.lbl_num_phrs.setText("Phrases created: 0")

        self.lbl_grp_num.setGeometry(QtCore.QRect(20, 100, 261, 29))
        self.lbl_grp_num.setText("Groups created: 0")

        self.lbl_par_num.setGeometry(QtCore.QRect(290, 100, 271, 29))
        self.lbl_par_num.setText("Overall paragraphs: 0")

        self.lbl_line_num.setGeometry(QtCore.QRect(570, 100, 261, 29))
        self.lbl_line_num.setText("Overall lines: 0")

        self.lbl_sen_num.setGeometry(QtCore.QRect(20, 160, 271, 29))
        self.lbl_sen_num.setText("Overall sentences: 0")

    def tbl_config(self):
        self.tbl_freq.setGeometry(QtCore.QRect(20, 60, 401, 751))
        self.tbl_freq.setStyleSheet("background-color: rgb(255, 255, 213); font: bold 16pt \"Segoe UI\";")
        self.tbl_freq.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tbl_freq.setColumnCount(3)
        self.tbl_freq.setRowCount(0)

        self.tbl_freq.setHorizontalHeaderItem(0, QTableWidgetItem("Rank"))
        self.tbl_freq.setColumnWidth(0, 80)
        self.tbl_freq.setHorizontalHeaderItem(1, QTableWidgetItem("Word"))
        self.tbl_freq.setColumnWidth(1, 160)
        self.tbl_freq.setHorizontalHeaderItem(2, QTableWidgetItem("Frequency"))
        self.tbl_freq.setColumnWidth(2, 140)
        self.tbl_freq.verticalHeader().setVisible(False)
        self.tbl_freq.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # enable read-only

    def labels_config(self):
        lbl_wrd_freq = QtWidgets.QLabel(self)
        lbl_wrd_freq.setGeometry(QtCore.QRect(25, 10, 395, 45))
        lbl_wrd_freq.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; text-decoration: underline; "
            "color:#ffffd5;\">Top 100 Most Frequent Words:</span></p></body></html>")

    def words_stats_config(self):
        self.box_word_stats.setGeometry(QtCore.QRect(470, 290, 831, 161))
        self.box_word_stats.setStyleSheet("font: bold 16pt \"Segoe UI\";color: rgb(255, 255, 213);")
        self.box_word_stats.setTitle("Words Analysis")
        self.box_word_stats.setAlignment(QtCore.Qt.AlignCenter)
        self.box_word_stats.setObjectName("box_word_stats")

        self.lbl_wrd_num.setGeometry(QtCore.QRect(20, 40, 261, 29))
        self.lbl_wrd_num.setText("Overall words: 0")

        self.lbl_unq_wrd.setGeometry(QtCore.QRect(280, 40, 261, 29))
        self.lbl_unq_wrd.setText("Unique words: 0")

        self.lbl_avg_wrd_par.setGeometry(QtCore.QRect(540, 40, 291, 29))
        self.lbl_avg_wrd_par.setText("Avg. per paragraph: 0")

        self.lbl_avg_wrd_sen.setGeometry(QtCore.QRect(20, 100, 261, 29))
        self.lbl_avg_wrd_sen.setText("Avg. per sentence: 0")

        self.lbl_avg_wrd_line.setGeometry(QtCore.QRect(280, 100, 251, 29))
        self.lbl_avg_wrd_line.setText("Avg. per line: 0")

        self.lbl_avg_wrd_book.setGeometry(QtCore.QRect(540, 100, 281, 29))
        self.lbl_avg_wrd_book.setText("Avg. per book: 0")

    def char_stats_config(self):
        self.box_char_stats.setGeometry(QtCore.QRect(470, 530, 831, 161))
        self.box_char_stats.setStyleSheet("font: bold 16pt \"Segoe UI\"; color: rgb(255, 255, 213);")
        self.box_char_stats.setTitle("Characters Analysis")
        self.box_char_stats.setAlignment(QtCore.Qt.AlignCenter)

        self.lbl_chr_num.setGeometry(QtCore.QRect(20, 40, 281, 29))
        self.lbl_chr_num.setText("Overall characters: 0")

        self.lbl_avg_chr_par.setGeometry(QtCore.QRect(300, 40, 271, 29))
        self.lbl_avg_chr_par.setText("Avg. per paragraph: 0")

        self.lbl_avg_chr_sen.setGeometry(QtCore.QRect(580, 40, 241, 29))
        self.lbl_avg_chr_sen.setText("Avg. per sentence: 0")

        self.lbl_avg_chr_line.setGeometry(QtCore.QRect(20, 100, 251, 29))
        self.lbl_avg_chr_line.setText("Avg. per line: 0")

        self.lbl_avg_chr_book.setGeometry(QtCore.QRect(300, 100, 251, 29))
        self.lbl_avg_chr_book.setText("Avg. per book: 0")

        self.lbl_avg_chr_wrd.setGeometry(QtCore.QRect(580, 100, 251, 29))
        self.lbl_avg_chr_wrd.setText("Avg. per word: 0")

