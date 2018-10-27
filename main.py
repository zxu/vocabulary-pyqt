import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import random

import mainwindow  # This file holds our MainWindow and all design related things
from dictionary import Dictionary


class ExampleApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DesktopIcon))
        self.nextButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight))

        dictionary = Dictionary()
        dictionary.load()
        self.data = dictionary.data
        self.reviewed = set([])

        self.nextButton.clicked.connect(self.next_word)
        self.nextButton.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence(QtCore.Qt.Key_N)))

    def keyPressEvent(self, event):
        if event.key() < 100:
            self.next_word()

    def next_word(self):
        column_size = self.data.columns.size
        row_size = self.data['Word'].size
        if column_size > 0 and row_size > 0:
            idx = random.randint(0, row_size - 1)
            self.lineEdit.setText(self.data['Word'][idx])
            self.reviewed.add(idx)
            self.statusLabel.setText(" %d of %d reviewed" % (len(self.reviewed), row_size))
            QtGui.QGuiApplication.clipboard().setText(self.data['Word'][idx])


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
