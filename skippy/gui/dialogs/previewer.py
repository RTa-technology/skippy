from PyQt5 import QtWebEngineWidgets, QtWidgets, QtCore, QtGui

from skippy.api import PageData

from skippy.core import preview

from skippy.gui import thread, utils

import skippy.config

from typing import Optional
import tempfile
import os


class PreviewerWorker(thread.AbstractWorker):
    finished = QtCore.pyqtSignal(str)

    def __init__(self, pdata: PageData):
        super(PreviewerWorker, self).__init__()
        self.pdata = pdata

    def run(self):
        self.finished.emit(preview.render(self.pdata))


class Previewer(QtWidgets.QDialog):
    def __init__(self, pdata: PageData, parent: Optional[QtWidgets.QWidget] = None):
        super(Previewer, self).__init__(parent)
        self._layout = QtWidgets.QVBoxLayout(self)

        self.webEngineView = QtWebEngineWidgets.QWebEngineView(self)

        self._thread = thread.Thread(PreviewerWorker(pdata))
        self._thread.worker.finished.connect(self.load)
        self._thread.start()

        self._layout.addWidget(self.webEngineView)

        self.setLayout(self._layout)

        self.setWindowTitle(f"Skippy - {skippy.config.version}")
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(skippy.config.RESOURCES_FOLDER, "skippy.ico"))
        )

        mainwindow = utils.getMainWindow()

        self.move(mainwindow.x(), mainwindow.y())
        self.resize(mainwindow.width(), mainwindow.height())
        self.setWindowState(mainwindow.windowState())

        self.exec_()

    def load(self, html: str):
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(html)
            self.webEngineView.load(QtCore.QUrl.fromLocalFile(tmp.name))
