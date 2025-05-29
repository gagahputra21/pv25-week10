import sys
import sqlite3
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QMessageBox, QLineEdit, QPushButton

DB_NAME = "mahasiswa.db"

class EditDataWindow(QDialog):
  def __init__(self, parent, id_value, nama, nim, tanggal_lahir):
    super().__init__(parent)
    uic.loadUi("week10/week10Dialog.ui", self)
    self.setWindowTitle("Edit Data Mahasiswa")

    self.name_input = QLineEdit(nama)
    self.nim_input = QLineEdit(nim)
    self.tl_input = QLineEdit(tanggal_lahir)

    self.saveButton = self.findChild(QPushButton, "saveButton")
    self.cancelButton = self.findChild(QPushButton, "cancelButton")

    self.saveButton.clicked.connect(self.saveData)
    self.cancelButton.clicked.connect(self.reject)

    self.id_value = id_value

  def saveData(self):
    nama = self.name_input.text()
    nim = self.nim_input.text()
    tanggal_lahir = self.dob_input.text()
    if nama and nim and tanggal_lahir:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE mahasiswa SET nama = ?, nim = ?, tanggal_lahir = ? WHERE id = ?",
                       (nama, nim, tanggal_lahir, self.id_value))
        conn.commit()
        conn.close()
        self.accept()
    else:
        QMessageBox.warning(self, "Input Error", "Semua field harus diisi.")

class DataManager(QMainWindow):
  def __init__(self):
    super().__init__()
    uic.loadUi("week10/week10.ui", self)
    self.setWindowTitle("Data Mahasiswa")
    self.initDB()
    self.loadData()

    self.table.setColumnCount(4)
    self.table.setHorizontalHeaderLabels(['ID', 'Nama', 'NIM', 'Tanggal Lahir'])

    self.actionSimpan.triggered.connect(self.addEntry)
    self.actionExport.triggered.connect(self.exportCSV)

    self.actionCari.triggered.connect(self.searchInputFocus)
    self.actionHapus.triggered.connect(self.deleteEntry)

    self.table.cellClicked.connect(self.onCellClicked)
    self.table.cellDoubleClicked.connect(self.onCellDoubleClicked)

    self.save_button.clicked.connect(self.addEntry)
    self.export_button.clicked.connect(self.exportCSV)
    self.hapus_button.clicked.connect(self.deleteEntry)

  def initDB(self):
    self.conn = sqlite3.connect(DB_NAME)
    self.cursor = self.conn.cursor()
    self.cursor.execute('''CREATE TABLE IF NOT EXISTS mahasiswa (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nama TEXT,
                        nim TEXT,
                        tanggal_lahir TEXT)''')
    self.conn.commit()

  def searchInputFocus(self):
    self.search_input.setFocus()

  def loadData(self):
    self.table.setRowCount(0)
    self.cursor.execute("SELECT * FROM mahasiswa")
    for row_idx, row_data in enumerate(self.cursor.fetchall()):
      self.table.insertRow(row_idx)
      for col_idx, item in enumerate(row_data):
        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
    if self.table.rowCount() == 0:
      QMessageBox.information(self, "No Data", "Tidak ada data mahasiswa yang ditemukan.")

  def addEntry(self):
    nama = self.name_input.text()
    nim = self.nim_input.text()
    tanggal_lahir = self.tl_input.text()
    if nama and nim and tanggal_lahir:
      self.cursor.execute("INSERT INTO mahasiswa (nama, nim, tanggal_lahir) VALUES (?, ?, ?)", (nama, nim, tanggal_lahir))
      self.conn.commit()
      self.loadData()
      self.clearInputs()
    else:
      QMessageBox.warning(self, "Input error", "Tolong isi semua form.")

  def deleteEntry(self):
    selected = self.table.currentRow()
    if selected >= 0:
      id_item = self.table.item(selected, 0)
      if id_item:
        self.cursor.execute("DELETE FROM mahasiswa WHERE id = ?", (id_item.text(),))
        self.conn.commit()
        self.loadData()
        self.clearInputs()
    else:
      QMessageBox.warning(self, "Selection error", "Tolong pilih baris yang ingin dihapus.")

  def exportCSV(self):
    with open('mahasiswa_export.csv', 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(['ID', 'Nama', 'NIM', 'Tanggal Lahir'])
      self.cursor.execute("SELECT * FROM mahasiswa")
      writer.writerows(self.cursor.fetchall())
    QMessageBox.information(self, "Ekspor Selesai", "Data berhasil diekspor ke mahasiswa_export.csv")

  def filterData(self):
    keyword = self.search_input.text()
    self.table.setRowCount(0)
    self.cursor.execute("SELECT * FROM mahasiswa WHERE nama LIKE ?", ('%' + keyword + '%',))
    for row_idx, row_data in enumerate(self.cursor.fetchall()):
      self.table.insertRow(row_idx)
      for col_idx, item in enumerate(row_data):
        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

  def onCellClicked(self, row, column):
    if self.table.item(row, 1) and self.table.item(row, 2) and self.table.item(row, 3):
      self.name_input.setText(self.table.item(row, 1).text())
      self.nim_input.setText(self.table.item(row, 2).text())
      self.tl_input.setText(self.table.item(row, 3).text())
    else:
      self.clearInputs()

  def onCellDoubleClicked(self, row, column):
    id_value = int(self.table.item(row, 0).text())
    nama = self.table.item(row, 1).text()
    nim = self.table.item(row, 2).text()
    tanggal_lahir = self.table.item(row, 3).text()

    dialog = EditDataWindow(self, id_value, nama, nim, tanggal_lahir)

    if dialog.exec_():
        self.loadData()

  def clearInputs(self):
    self.name_input.clear()
    self.nim_input.clear()
    self.tl_input.clear() 

  def closeEvent(self, event):  
    self.conn.commit()
    self.conn.close()
    event.accept()

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = DataManager()
  window.show()
  sys.exit(app.exec_())