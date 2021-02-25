import os
from utils.style_constants import STYLE_LINE, STYLE_BTN_TOOLTIP, STYLE_BTN, STYLE_BTN_15pt
from PyQt5 import QtCore, QtGui, QtWidgets
from msg_box import MsgIcon, display_msg


class GroupTab(QtWidgets.QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.db.tune_in_new_book(self.update_groups)
        self.db.tune_in_import(self.update_groups)
        # Defining Gui attributes:
        self.list_grp = QtWidgets.QListWidget(self)
        self.list_wrd_in_grp = QtWidgets.QListWidget(self)
        self.line_grp = QtWidgets.QLineEdit(self)
        self.line_wrd_to_grp = QtWidgets.QLineEdit(self)
        # configuring aforementioned Gui attributes:
        self.lists_config()
        self.labels_config()
        self.buttons_config()
        self.lines_config()
        self.separator_config()
        self.img_config()

    def create_group(self):
        """Adds new group to the database. notifies stats_tab of changes. """
        group_name = self.line_grp.text().strip()  # removes whitespaces from left and right

        if group_name == '':
            display_msg(MsgIcon.WARNING, "Warning", "Please choose a group name")
            return

        self.line_grp.setText("")
        if self.db.insert_group(group_name):  # if creation was successful:
            self.list_grp.addItem(group_name)  # adds new group to the list.
            self.db.notify_stats()  # update stats tab

    def insert_word_to_group(self):
        """ checks if selected word exists in the database. if not, adds it to the db.
            later adds it to word_in_group with an appropriate id.
            called after clicking on '>>' button.
        """
        self.db.clear_cache()
        word_txt = self.line_wrd_to_grp.text().strip().lower()  # remove spaces from the rear and the front
        self.line_wrd_to_grp.setText("")
        index = self.list_grp.selectionModel().currentIndex()
        group_txt = index.sibling(index.row(), 0).data()

        if word_txt == "":
            display_msg(MsgIcon.WARNING, "Warning", "Please enter a word")

        elif len(word_txt.split(" ")) > 1:
            display_msg(MsgIcon.WARNING, "Warning", "Please enter a *single* word")

        elif not group_txt:
            display_msg(MsgIcon.WARNING, "Warning", "Please pick a group to insert the word into")

        else:
            # bypassing the cache while to access the database directly
            word_id = self.db.get_word_id.__wrapped__(self.db, word_txt)
            if not word_id:  # if word doesn't exist yet in the DB insert it
                word_id = self.db.insert_word(word_txt)
            group_id = self.db.get_group_id(group_txt)

            if self.db.insert_word_in_group(word_id[0], group_id):  # if word was inserted successfully
                self.display_grp_words()

    def display_grp_words(self):
        """fills group words (right) list with words of the group the user clicked. """
        index = self.list_grp.selectionModel().currentIndex()
        group_txt = index.sibling(index.row(), 0).data()
        self.list_wrd_in_grp.clear()  # clears group words list (right list).
        for word in self.db.get_group_words(group_txt):
            self.list_wrd_in_grp.addItem(word[0])

    def update_groups(self):
        """Updates group (left) list from DB.
        Used when user either adds a new book or imports to the DB. """

        self.list_grp.clear()
        self.list_wrd_in_grp.clear()  # resets (left) groups list
        for group_name in self.db.get_groups():  # populates groups list from DB.
            self.list_grp.addItem(group_name[0])

    def del_wrd_in_grp(self):
        """removes the word the user selected in the list from the previously selected group"""
        index = self.list_grp.selectionModel().currentIndex()
        group = index.sibling(index.row(), 0).data()
        wrd_index = self.list_wrd_in_grp.selectionModel().currentIndex()
        wrd = wrd_index.sibling(wrd_index.row(), 0).data()
        if not (wrd and group):
            display_msg(MsgIcon.WARNING, "Warning", "Please choose a group "
                                                    "and an associated word you'd like to remove.")
            return
        self.db.del_wrd_in_grp(group, wrd)
        self.display_grp_words()

    def del_group(self):
        """removes the selected group from the database, including all words unique to said group"""
        index = self.list_grp.selectionModel().currentIndex()
        group = index.sibling(index.row(), 0).data()
        if not group:
            display_msg(MsgIcon.WARNING, "Warning", "Please choose a group to remove.")
            return
        self.db.del_group(group)
        self.update_groups()
        self.db.notify_stats()

    def lists_config(self):
        self.list_grp.setGeometry(QtCore.QRect(210, 380, 190, 350))
        self.list_grp.setStyleSheet(STYLE_LINE)
        self.list_grp.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.list_grp.setFlow(QtWidgets.QListView.TopToBottom)
        self.list_grp.setViewMode(QtWidgets.QListView.ListMode)
        self.list_grp.itemClicked.connect(self.display_grp_words)

        self.list_wrd_in_grp.setGeometry(QtCore.QRect(970, 380, 190, 350))
        self.list_wrd_in_grp.setStyleSheet(STYLE_LINE)
        self.list_wrd_in_grp.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.list_wrd_in_grp.setFlow(QtWidgets.QListView.TopToBottom)
        self.list_wrd_in_grp.setViewMode(QtWidgets.QListView.ListMode)

    def img_config(self):
        img = QtWidgets.QLabel(self)
        img.setGeometry(QtCore.QRect(-10, 0, 1541, 891))
        img.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname('__file__'), "images/library.png")))
        img.setScaledContents(True)
        img.lower()  # set image at the background.

    def labels_config(self):
        lbl_crt_grp = QtWidgets.QLabel(self)
        lbl_crt_grp.setGeometry(QtCore.QRect(480, 30, 381, 40))
        lbl_crt_grp.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; "
            "text-decoration: underline; color:#ffffd5;\">Create a New Word Group:"
            "</span></p></body></html>")

        lbl_add_grp = QtWidgets.QLabel(self)
        lbl_add_grp.setGeometry(QtCore.QRect(480, 260, 381, 40))
        lbl_add_grp.setText(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; "
            "text-decoration: underline; color:#ffffd5;\">Add Words to Groups:"
            "</span></p></body></html>")

        lbl_ent_grp = QtWidgets.QLabel(self)
        lbl_ent_grp.setGeometry(QtCore.QRect(150, 98, 310, 31))
        lbl_ent_grp.setText(
            "<html><head/><body><p><span style=\" font-size:18pt; color:#ffffd5;\">Enter name of word group:</span></p></body></html>")

        lbl_wrd_grp = QtWidgets.QLabel(self)
        lbl_wrd_grp.setGeometry(QtCore.QRect(190, 330, 250, 29))
        lbl_wrd_grp.setText(
            "<html><head/><body><p><span style=\" font-size:18pt; color:#ffffd5;\">Select a Word Group:</span></p></body></html>")

        lbl_wrd_to_grp = QtWidgets.QLabel(self)
        lbl_wrd_to_grp.setGeometry(QtCore.QRect(560, 470, 181, 60))
        lbl_wrd_to_grp.setText(
            "<html><head/><body><p><span style=\" font-size:16pt; color:#ffffd5;\">Insert a word to selected group: </span></p></body></html>")
        lbl_wrd_to_grp.setWordWrap(True)

        lbl_wrd_in_grp = QtWidgets.QLabel(self)
        lbl_wrd_in_grp.setGeometry(QtCore.QRect(940, 330, 290, 31))
        lbl_wrd_in_grp.setText(
            "<html><head/><body><p><span style=\" font-size:18pt; color:#ffffd5;\">Words in selected group:</span></p></body></html>")

    def lines_config(self):
        self.line_grp.setGeometry(QtCore.QRect(480, 100, 511, 29))
        self.line_grp.setStyleSheet(STYLE_LINE)
        self.line_grp.setAlignment(QtCore.Qt.AlignCenter)

        self.line_wrd_to_grp.setGeometry(QtCore.QRect(530, 540, 231, 29))
        self.line_wrd_to_grp.setStyleSheet(STYLE_LINE)
        self.line_wrd_to_grp.setAlignment(QtCore.Qt.AlignCenter)

    def buttons_config(self):
        btn_crt_grp = QtWidgets.QPushButton(self)
        btn_crt_grp.setGeometry(QtCore.QRect(600, 160, 161, 41))
        btn_crt_grp.setToolTip("Create a group with a title of your choosing")
        btn_crt_grp.setStyleSheet(STYLE_BTN_TOOLTIP)
        btn_crt_grp.setText("Create")
        btn_crt_grp.clicked.connect(self.create_group)

        btn_wrd_to_grp = QtWidgets.QPushButton(self)
        btn_wrd_to_grp.setGeometry(QtCore.QRect(800, 540, 61, 31))
        btn_wrd_to_grp.setStyleSheet(STYLE_BTN)
        btn_wrd_to_grp.setText(">>")
        btn_wrd_to_grp.clicked.connect(self.insert_word_to_group)

        btn_del_grp = QtWidgets.QPushButton(self)
        btn_del_grp.setGeometry(QtCore.QRect(210, 760, 190, 40))
        btn_del_grp.setStyleSheet(STYLE_BTN_15pt)
        btn_del_grp.setText("Remove Group")
        btn_del_grp.clicked.connect(self.del_group)

        btn_del_wrd = QtWidgets.QPushButton(self)
        btn_del_wrd.setGeometry(QtCore.QRect(970, 760, 190, 40))
        btn_del_wrd.setStyleSheet(STYLE_BTN_15pt)
        btn_del_wrd.setText("Remove Word")
        btn_del_wrd.clicked.connect(self.del_wrd_in_grp)

    def separator_config(self):
        sep_group = QtWidgets.QFrame(self)
        sep_group.setGeometry(QtCore.QRect(200, 220, 951, 21))
        sep_group.setFrameShadow(QtWidgets.QFrame.Raised)
        sep_group.setLineWidth(4)
        sep_group.setMidLineWidth(0)
        sep_group.setFrameShape(QtWidgets.QFrame.HLine)
