from PyQt5 import QtWidgets, QtCore, QtGui

from skippy.core import scpclient

from skippy.gui import sitebox, thread, utils

from skippy.utils import translator
import skippy.config

from typing import Optional
import os


class DownloadWorker(thread.AbstractWorker):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, site: str, page: str):
        super(DownloadWorker, self).__init__()
        self.site = site
        self.page = page

    def run(self):
        pageData = scpclient.SCPClient().download(self.site, self.page)
        self.finished.emit(pageData)


class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtCore.QObject] = None):
        super(DownloadDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel(
            translator.Translator().translate("DIALOG_ENTER_PAGE_LABEL"), self
        )

        self.site_box = sitebox.SiteBox(self)

        self.page_box = QtWidgets.QLineEdit()
        self.page_box.setPlaceholderText(
            translator.Translator().translate("DIALOG_PAGE_BOX_PLACEHOLDER")
        )

        self.button = QtWidgets.QPushButton(
            translator.Translator().translate("DIALOG_OK_BUTTON"), self
        )
        self.button.clicked.connect(self.download)

        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.site_box)
        self.layout.addWidget(self.page_box)
        self.layout.addWidget(self.button, alignment=QtCore.Qt.AlignRight)

        self.setLayout(self.layout)

        self.setWindowTitle(f"Skippy - {skippy.config.version}")
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(skippy.config.RESOURCES_FOLDER, "skippy.ico"))
        )
        self.move(300, 300)
        self.resize(200, 100)

        self.show()

    def download(self):
        site = self.site_box.currentText()
        page = self.page_box.text()

        self._thread = thread.Thread(DownloadWorker(site, page))
        self._thread.worker.finished.connect(lambda pageData: utils.getMainWindow().tab.newTab(*pageData.values()))
        self._thread.start()
        
        self.close()
