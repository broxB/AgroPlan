import os

os.system(r"pyuic6 ./qtdesigner/AgroPlan/mainwindow.ui -o ./app/gui/views/mainwindow.py")
os.system(r"pyuic6 ./qtdesigner/AgroPlan/dialog.ui -o ./app/gui/views/dialog.py")
