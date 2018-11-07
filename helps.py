from PyQt5.QtCore import QObject, pyqtSignal


class Communicate(QObject):
    total_marked_signal = pyqtSignal(int)
    progress_signal = pyqtSignal(int, int)


communicate = Communicate()
