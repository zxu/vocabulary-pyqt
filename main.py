import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QGuiApplication, QKeySequence
from PyQt5.QtWidgets import QApplication, QAction, QStyle, QMainWindow, QLabel, QFrame

import mainwindow
from database import Database
from dictionary import Dictionary


class ExampleApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.database = Database()
        self.dictionary = Dictionary()
        self.dictionary.load(database=self.database)

        self.show_marked_only = False

        self.setupUi(self)

        self.statusLabel = QLabel(self.centralWidget)
        self.statusLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.statusLabel.setText('Press any key to continue')

        self.statusLabelMarked = QLabel(self.centralWidget)

        self.statusLabelRight = QLabel(self.centralWidget)
        self.statusLabelRight.setFrameStyle(QFrame.NoFrame)

        self.statusBar.addWidget(self.statusLabel)
        self.statusBar.addWidget(self.statusLabelMarked)
        self.statusBar.addPermanentWidget(self.statusLabelRight)

        self.nextButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.nextButton.clicked.connect(self.next_word)
        self.nextButton.setShortcut(QKeySequence(QKeySequence(Qt.Key_N)))

        mark_action = QAction(self.style().standardIcon(QStyle.SP_DialogApplyButton), 'Mark', self)
        mark_action.setShortcut('Ctrl+M')
        mark_action.triggered.connect(lambda: self.mark_word(True))
        mark_action.setStatusTip("Mark current word for later review")

        remove_mark_action = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton),
                                     'Un-mark', self)
        remove_mark_action.setShortcut('Ctrl+U')
        remove_mark_action.triggered.connect(lambda: self.mark_word(False))
        remove_mark_action.setStatusTip("Remove mark for current word")

        save_reviewed_action = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), 'Save', self)
        save_reviewed_action.setShortcut('Ctrl+S')
        save_reviewed_action.triggered.connect(self.save_reviewed)
        save_reviewed_action.setStatusTip("Save current progress")

        show_marked_only_action = QAction('Show Marked Only', self)
        show_marked_only_action.setStatusTip('Only display marked words')
        show_marked_only_action.setCheckable(True)
        show_marked_only_action.setChecked(False)
        show_marked_only_action.triggered.connect(self.toggle_marked_only)

        reset_progress_action = QAction('Reset Progress', self)
        reset_progress_action.setStatusTip('Reset review progress')
        reset_progress_action.triggered.connect(self.reset_progress)

        self.toolbar = self.addToolBar('Vocabulary')
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.toolbar.addAction(mark_action)
        self.toolbar.addAction(remove_mark_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(save_reviewed_action)

        menu_bar = self.menuBar()
        words_menu = menu_bar.addMenu('Words')
        words_menu.addAction(mark_action)
        words_menu.addAction(remove_mark_action)
        words_menu.addSeparator()
        words_menu.addAction(save_reviewed_action)
        words_menu.addSeparator()
        words_menu.addAction(show_marked_only_action)
        words_menu.addAction(reset_progress_action)

        self.display_total_marked()

    def keyPressEvent(self, event):
        if event.key() < 100:
            self.next_word()

    def next_word(self):
        word = self.dictionary.next_word(self.database.marked_indices if self.show_marked_only else None)
        if word:
            self.lineEdit.setText(word['word'])
            self.statusLabel.setText(' %d of %d reviewed' % (self.dictionary.total_reviewed(),
                                                             self.dictionary.total_words))
            self.highlight_marked(self.database.is_marked(word['idx']))

            QGuiApplication.clipboard().setText(word['word'])

    def highlight_marked(self, marked):
        if marked:
            self.statusLabelRight.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.statusLabelRight.setPixmap(self.style().standardIcon(
                QStyle.SP_DialogApplyButton).pixmap(QSize(16, 16)))
        else:
            self.statusLabelRight.setFrameStyle(QFrame.NoFrame)
            self.statusLabelRight.clear()

    def display_total_marked(self):
        total_marked = len(self.database.marked_indices)
        if total_marked > 0:
            self.statusLabelMarked.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.statusLabelMarked.setText('%d marked' % total_marked)
        else:
            self.statusLabelMarked.setFrameStyle(QFrame.NoFrame)
            self.statusLabelMarked.clear()

    def save_reviewed(self):
        _str = self.dictionary.reviewed_as_string()
        if _str is None:
            return
        self.database.save_settings('reviewed', _str)

    def toggle_marked_only(self):
        self.show_marked_only = not self.show_marked_only

    def reset_progress(self):
        self.dictionary.reset_progress()

    def mark_word(self, mark):
        if self.dictionary.current_word and \
                'word' in self.dictionary.current_word and 'idx' in self.dictionary.current_word:
            if mark:
                self.database.mark(
                    self.dictionary.current_word['word'],
                    self.dictionary.current_word['idx']
                )
            else:
                self.database.un_mark(self.dictionary.current_word['word'])

            self.highlight_marked(self.database.is_marked(self.dictionary.current_word['idx']))
            self.display_total_marked()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(app.style().standardIcon(QStyle.SP_DesktopIcon))
    form = ExampleApp()
    form.show()

    app.aboutToQuit.connect(form.save_reviewed)
    app.exec_()


if __name__ == '__main__':
    main()
