import sys

from PySide6.QtWidgets import QApplication

from main import _AboutDialog

app = QApplication(sys.argv)
for polish in (True, False):
    dialog = _AboutDialog(polish)
    dialog.show()
    app.processEvents()
    dialog.grab().save(f".dev/about_{ 'pl' if polish else 'en' }.png")
    dialog.close()
print("previews saved")
