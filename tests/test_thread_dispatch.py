import os
import threading
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEventLoop, QObject, Qt, QTimer, Signal, Slot, QThread
from PySide6.QtWidgets import QApplication

from mouse_shortcut import MouseShortcutService


class SignalReceiver(QObject):
    received = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.callback_thread: QThread | None = None

    @Slot()
    def handle(self) -> None:
        self.callback_thread = QThread.currentThread()
        self.received.emit()


class ThreadDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_worker_signal_is_queued_to_receiver_thread(self) -> None:
        service = MouseShortcutService("middle")
        receiver = SignalReceiver()
        loop = QEventLoop()
        receiver.received.connect(loop.quit)
        service.menu_requested.connect(receiver.handle, Qt.ConnectionType.QueuedConnection)

        worker = threading.Thread(target=service.menu_requested.emit)
        worker.start()
        QTimer.singleShot(2000, loop.quit)
        loop.exec()
        worker.join()

        self.assertIs(receiver.callback_thread, self.app.thread())


if __name__ == "__main__":
    unittest.main()