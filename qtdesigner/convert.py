import os

os.system(r"pyuic6 ./qtdesigner/mainwindow_2.ui -o ./app/gui/views/mainwindow.py")
os.system(r"pyuic6 ./qtdesigner/dialog.ui -o ./app/gui/views/dialog.py")
