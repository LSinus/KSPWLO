#https://www.python.it/wiki/show/qttutorial/

import sys 
from PyQt5 import QtWidgets, QtGui, QtCore

class MainWindow(QtWidgets.QMainWindow):
        def __init__(self):
                super().__init__()
                self.resize(1000, 750)
                #self.setWindowTitle('MainWindow')
                self.statusBar().showMessage('ApplicazioneMappa')

                # #self.setWindowTitle('Pulsanti')
                # button=QtWidgets.QPushButton('Quit') #creiamo nuovo pulsante con nome quit
                # button.setFont(QtGui.QFont("Georgia", 15, QtGui.QFont.Bold))
                # button.clicked.connect(self.close)
                # self.setCentralWidget(button)


                cWidget=QtWidgets.QWidget(self) #cosi creiamo un widget astratto che non ha alcuna funzione grafica se non quella di
                #contenere tutti gli altri

                #layout orizzontale
                hBox=QtWidgets.QHBoxLayout()
                hBox.setSpacing(10)

                #Etichetta
                label=QtWidgets.QLabel('Enter the information', cWidget)
                hBox.addWidget(label)

                #textEdit
                textEdit=QtWidgets.QTextEdit(cWidget)
                if textEdit.isReadOnly():
                    textEdit.setReadOnly(False)
                hBox.addWidget(textEdit)

                #layout verticale per i pulsanti
                vBox=QtWidgets.QVBoxLayout()
                vBox.setSpacing(10)
                hBox.addLayout(vBox)

                #pulsanti
                button1=QtWidgets.QPushButton('Go!', cWidget) #creiamo nuovo pulsante con nome go!
                button1.setFont(QtGui.QFont("Georgia", 15, QtGui.QFont.Bold))
                vBox.addWidget(button1)
                button2=QtWidgets.QPushButton('Reset!', cWidget) #creiamo nuovo pulsante con nome go!
                button2.setFont(QtGui.QFont("Georgia", 15, QtGui.QFont.Bold))
                vBox.addWidget(button2)

                #impostazione layout
                cWidget.setLayout(hBox)
                self.setCentralWidget(cWidget)


app=QtWidgets.QApplication(sys.argv) #inizializzazione PyQt5 da porre sempre a inizo ogni codice
main=MainWindow() #inizializzazione oggetto QtWindow
main.show()
sys.exit(app.exec_())