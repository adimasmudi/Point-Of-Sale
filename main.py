import sys, os, csv
from PySide6.QtWidgets import *
import time
from PySide6.QtCore import *
from PySide6.QtGui import *

import datetime

import matplotlib.pyplot as plt

import mysql.connector

# db
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="POS"
)
if db.is_connected():
    print("Berhasil terhubung ke database")


class Apps(QTabWidget):
    def __init__(self, parent=None):
        super(Apps, self).__init__(parent)
        self.setGeometry(100,100,400,400)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")
        self.addTab(self.tab3, "Tab 3")
        self.tabBarang()
        self.tabTransaksi()
        self.tabPelanggan()
        self.setWindowTitle("Point of Sale (POS)")


    def tabBarang(self):
        # komponen
        judul = QLabel()
        hbox = QHBoxLayout()
        tambahBarang = QPushButton("Tambah Barang")
        editBarang = QPushButton("Edit Barang")
        hapusBarang = QPushButton("Hapus Barang")

        hbox.addWidget(tambahBarang)
        hbox.addWidget(editBarang)
        hbox.addWidget(hapusBarang)

        judul.setText("Daftar Barang")

        tambahBarang.clicked.connect(self.tambahBarangAppear)
        editBarang.clicked.connect(self.editBarangAppear)
        hapusBarang.clicked.connect(self.hapusBarangAppear)


        # tabel
        global tableBarang
        tableBarang = QTableWidget()
        # get data from database
        cursor = db.cursor()
        sql = "SELECT * FROM barang"
        cursor.execute(sql)

        results = cursor.fetchall()

        tableBarang.setRowCount(len(results))
        tableBarang.setColumnCount(len(results[0]))

        for n, data in enumerate(results):
            for m, item in enumerate(data):
                newitem = QTableWidgetItem(str(item))
                tableBarang.setItem(n, m, newitem)

        tableBarang.verticalHeader().hide()
        tableBarang.setHorizontalHeaderLabels(['id', 'Nama Barang', 'harga', 'ketersediaan'])


        # layout
        layout = QVBoxLayout()
        layout.addWidget(judul)
        layout.addLayout(hbox)
        layout.addWidget(tableBarang)

        self.setTabText(0, "Barang")
        self.tab1.setLayout(layout)

    def tambahBarangAppear(self):
        self.new = TambahBarangDialog()
        self.new.show()

    def editBarangAppear(self):
        self.edit = UpdateId()
        self.edit.show()

    def hapusBarangAppear(self):
        self.hapus = DeleteId()
        self.hapus.show()


    def tabTransaksi(self):
        # komponen
        judul = QLabel()

        addTransaksi= QPushButton("Tambah")
        exportBtn = QPushButton("Export as CSV")
        grafik = QPushButton("Grafik")

        hbox = QHBoxLayout()
        hbox.addWidget(addTransaksi)
        hbox.addWidget(exportBtn)
        hbox.addWidget(grafik)

        global tableTransaksi
        tableTransaksi = QTableWidget()

        # get data from database
        cursorTrans = db.cursor()
        sql = "SELECT tanggal, nama_pelanggan, nama_barang, kontak, barang.harga, qty FROM detail_transaksi INNER JOIN transaksi ON detail_transaksi.id_transaksi = transaksi.id INNER JOIN barang ON detail_transaksi.id_barang = barang.id;"
        cursorTrans.execute(sql)

        resultsTrans = cursorTrans.fetchall()

        judul.setText("Daftar Penjualan")

        addTransaksi.clicked.connect(self.addTransaksiAppear)
        exportBtn.clicked.connect(self.handleSave)
        grafik.clicked.connect(self.showGrafik)

        tableTransaksi.setRowCount(len(resultsTrans))
        tableTransaksi.setColumnCount(len(resultsTrans[0]))

        print(resultsTrans)

        for i, data in enumerate(resultsTrans):
            for j, item in enumerate(data):
                tableTransaksi.setItem(i, j, QTableWidgetItem(str(item)))
        tableTransaksi.verticalHeader().hide()
        tableTransaksi.setHorizontalHeaderLabels([ 'Tanggal', 'Nama Pelanggan', 'barang','kontak','harga','qty'])

        # layout
        layout = QVBoxLayout()
        layout.addWidget(judul)
        layout.addLayout(hbox)
        layout.addWidget(tableTransaksi)

        self.setTabText(1, "Transaksi")
        self.tab2.setLayout(layout)

    def addTransaksiAppear(self):
        self.new_transaksi_window = TambahTransaksiDialog()
        self.new_transaksi_window.show()

    def handleSave(self):
        path, ok = QFileDialog.getSaveFileName(
            self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
        if ok:
            columns = range(tableTransaksi.columnCount())
            header = [tableTransaksi.horizontalHeaderItem(column).text()
                      for column in columns]
            with open(path, 'w') as csvfile:
                writer = csv.writer(
                    csvfile, dialect='excel', lineterminator='\n')
                writer.writerow(header)
                for row in range(tableTransaksi.rowCount()):
                    writer.writerow(
                        tableTransaksi.item(row, column).text()
                        for column in columns)

    def showGrafik(self):
        print('show grafik')
        # get data from database
        cursorGrafik = db.cursor()
        sql = "SELECT nama_barang, SUM(detail_transaksi.qty) as qty FROM detail_transaksi LEFT JOIN barang ON detail_transaksi.id_barang = barang.id GROUP BY barang.nama_barang;"
        cursorGrafik.execute(sql)

        resultsGrafik = cursorGrafik.fetchall()

        x_axis = []
        y_axis = []

        for data in resultsGrafik:
            x_axis.append(data[0])
            y_axis.append(int(data[1]))

        for l in range(len(y_axis)):
            for m in range(l + 1, len(y_axis)):
                if l < m:
                    if y_axis[l] > y_axis[m]:
                        temp = y_axis[l]
                        temp2 = x_axis[l]
                        y_axis[l] = y_axis[m]
                        x_axis[l] = x_axis[m]
                        y_axis[m] = temp
                        x_axis[m] = temp2

        for x in range(len(y_axis)):
            plt.barh(x_axis, y_axis, color='blue')
            plt.text(y_axis[x], x, str(y_axis[x]))
        plt.title('Barang paling banyak terjual')
        plt.xlabel('nama barang')
        plt.ylabel('kuantitas barang terjual')
        plt.show()

    def tabPelanggan(self):
        layout = QVBoxLayout()
        judul = QLabel('Data Pelanggan')

        # get data from database
        cursorPelanggan = db.cursor()
        sql = "SELECT nama_pelanggan, kontak, SUM(total) as total_pembayaran, COUNT(nama_pelanggan) as frekuensi_pembelian FROM detail_transaksi INNER JOIN transaksi ON detail_transaksi.id_transaksi = transaksi.id GROUP BY nama_pelanggan;"
        cursorPelanggan.execute(sql)

        resultsPelanggan = cursorPelanggan.fetchall()

        # tabel
        table = QTableWidget()
        table.setRowCount(len(resultsPelanggan))
        table.setColumnCount(len(resultsPelanggan[0]))

        for n, data in enumerate(resultsPelanggan):
            for m, item in enumerate(data):
                newitem = QTableWidgetItem(str(item))
                table.setItem(n, m, newitem)

        table.verticalHeader().hide()
        table.setHorizontalHeaderLabels(['nama pelanggan','kontak','total pembayaran','frekuensi'])

        layout.addWidget(judul)
        layout.addWidget(table)
        self.setTabText(2, "Pelanggan")
        self.tab3.setLayout(layout)



# dialog tambah barang
class TambahBarangDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Tambah Data Barang')
        self.setGeometry(100, 110, 300, 300)

        self.input_add()

    def input_add(self):
        layout = QVBoxLayout()
        form = QFormLayout(self)
        submit = QPushButton("Submit")
        cancel = QPushButton("Cancel")

        submit.clicked.connect(self.processInput)
        cancel.clicked.connect(self.removeInput)

        self.inputNamaBarang = QLineEdit()
        self.inputHarga = QLineEdit()
        self.inputKuantitas = QLineEdit()

        form.addRow("Nama Barang",self.inputNamaBarang)
        form.addRow("Harga",self.inputHarga)
        form.addRow("Kuantitas", self.inputKuantitas)
        form.addRow(submit,cancel)
        layout.addLayout(form)

    def processInput(self):
        cursor = db.cursor()
        sql = "INSERT INTO barang (nama_barang,harga, ketersediaan) VALUES (%s, %s, %s)"
        val = (self.inputNamaBarang.text(), self.inputHarga.text(), self.inputKuantitas.text())
        cursor.execute(sql, val)

        db.commit()

        print("{} data ditambahkan".format(cursor.rowcount))


        self.inputNamaBarang.setText('')
        self.inputHarga.setText('')
        self.inputKuantitas.setText('')

        self.close()

        # get data from database
        cursor = db.cursor()
        sql = "SELECT * FROM barang"
        cursor.execute(sql)

        results = cursor.fetchall()

        time.sleep(1)
        row = len(results)-1
        tableBarang.insertRow(row)
        for n, item in enumerate(results[row]):
            tableBarang.setItem(row,n,QTableWidgetItem(str(item)))


    def removeInput(self):
        self.inputNamaBarang.setText('')
        self.inputHarga.setText('')
        self.inputKuantitas.setText('')

class UpdateId(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Id barang yang akan diupdate")
        self.setGeometry(100,100,200,200)

        self.input()

    def input(self):
        form = QFormLayout()
        global updateId
        updateId = QLineEdit()
        submit = QPushButton("Submit")

        submit.clicked.connect(self.appearFormEdit)
        form.addRow("Masukkan id barang yang ingin diupdate",updateId)
        form.addRow(submit)


        self.setLayout(form)

    def appearFormEdit(self):
        self.editForm = EditBarangDialog()
        self.editForm.show()

        self.close()

# dialog tambah barang
class EditBarangDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Edit Data Barang')
        self.setGeometry(100, 110, 300, 300)

        self.input_edit()

    def input_edit(self):
        layout = QVBoxLayout()
        form = QFormLayout(self)
        submit = QPushButton("Submit")
        cancel = QPushButton("Kosongkan")

        submit.clicked.connect(self.processInput)
        cancel.clicked.connect(self.removeInput)

        # get data from database
        cursor = db.cursor()
        sql = "SELECT * FROM barang WHERE id='{}'".format(updateId.text())

        cursor.execute(sql)

        results = cursor.fetchall()
        print('id to update',updateId.text())
        print("results",results)

        self.inputNamaBarangUpdate = QLineEdit(results[0][1])
        self.inputHargaUpdate = QLineEdit(str(results[0][2]))
        self.inputKuantitasUpdate = QLineEdit(str(results[0][3]))

        form.addRow("Nama Barang",self.inputNamaBarangUpdate)
        form.addRow("Harga",self.inputHargaUpdate)
        form.addRow("Kuantitas", self.inputKuantitasUpdate)
        form.addRow(submit,cancel)
        layout.addLayout(form)


    def processInput(self):
        cursor = db.cursor()
        sql = "UPDATE barang SET nama_barang =%s ,harga = %s, ketersediaan = %s WHERE id=%s"
        val = (self.inputNamaBarangUpdate.text(), self.inputHargaUpdate.text(), self.inputKuantitasUpdate.text(),updateId.text())
        cursor.execute(sql, val)

        db.commit()

        print("{} data diupdate".format(cursor.rowcount))


        self.inputNamaBarangUpdate.setText('')
        self.inputHargaUpdate.setText('')
        self.inputKuantitasUpdate.setText('')

        self.close()

        # get data from database
        cursor = db.cursor()
        sql = "SELECT * FROM barang"
        cursor.execute(sql)

        results = cursor.fetchall()


        time.sleep(1)
        allRow = len(results)
        tableBarang.clear()

        for j in range(allRow):
            tableBarang.insertRow(j)

        for m, data in enumerate(results):
            for n, item in enumerate(data):
                tableBarang.setItem(m,n,QTableWidgetItem(str(item)))

        tableBarang.verticalHeader().hide()
        tableBarang.setHorizontalHeaderLabels(['id', 'Nama Barang', 'harga', 'ketersediaan'])

    def removeInput(self):
        self.inputNamaBarangUpdate.setText('')
        self.inputHargaUpdate.setText('')
        self.inputKuantitasUpdate.setText('')

# delete dialog
class DeleteId(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Id barang yang akan dihapus")
        self.setGeometry(100,100,200,200)

        self.input()

    def input(self):
        form = QFormLayout()

        self.deleteId = QLineEdit()
        submit = QPushButton("Hapus")

        submit.clicked.connect(self.deleteBarang)
        form.addRow("Masukkan id barang yang ingin diupdate",self.deleteId)
        form.addRow(submit)


        self.setLayout(form)

    def deleteBarang(self):
        cursorDelete = db.cursor()

        sqlHapus = "DELETE FROM barang WHERE id = {}".format(self.deleteId.text())

        cursorDelete.execute(sqlHapus)

        db.commit()

        # get data from database
        cursor = db.cursor()
        sql = "SELECT * FROM barang"
        cursor.execute(sql)

        results = cursor.fetchall()

        time.sleep(1)
        allRow = len(results)
        tableBarang.clear()

        for j in range(allRow):
            tableBarang.insertRow(j)

        for m, data in enumerate(results):
            for n, item in enumerate(data):
                tableBarang.setItem(m, n, QTableWidgetItem(str(item)))

        tableBarang.verticalHeader().hide()
        tableBarang.setHorizontalHeaderLabels(['id', 'Nama Barang', 'harga', 'ketersediaan'])

        self.close()


class TambahTransaksiDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Tambah Data Transaksi')
        self.setGeometry(100, 110, 500, 500)

        self.addTransaksi()


    def addTransaksi(self):
        self.total = 0
        layout = QVBoxLayout()

        judul = QLabel()
        judul.setText("Tambah Transaksi")

        gridForm = QGridLayout()

        self.dataPembelian = []

        # form date
        self.addDate = QDateEdit()

        # nama barang
        # get data from database
        cursorBarang = db.cursor()
        sql = "SELECT * FROM barang"
        cursorBarang.execute(sql)

        resultsBarang = cursorBarang.fetchall()
        self.combo = QComboBox()
        self.daftarBarang = [barang[1] for barang in resultsBarang]
        self.hargaBarang = [barang[2] for barang in resultsBarang]

        for i in self.daftarBarang:
            self.combo.addItem(i)

        # form nama pelanggan
        self.addNamaPelanggan = QLineEdit()

        # form quantity
        self.qty = QLineEdit()

        # input kontak
        self.kontak = QLineEdit()

        # push button - tambah
        tambahData = QPushButton('tambah')
        tambahData.clicked.connect(self.prosesPembelian)

        gridForm.addWidget(QLabel("date"),0,0)
        gridForm.addWidget(self.addDate,0,1)
        gridForm.addWidget(QLabel('nama barang'),0,2)
        gridForm.addWidget(self.combo,0,3)
        gridForm.addWidget(QLabel('nama pelanggan'),1,0)
        gridForm.addWidget(self.addNamaPelanggan, 1, 1)
        gridForm.addWidget(QLabel("Quantity"),1,2)
        gridForm.addWidget(self.qty,1,3)
        gridForm.addWidget(QLabel('kontak'),2,0)
        gridForm.addWidget(self.kontak,2,1)
        gridForm.addWidget(tambahData,2,3)

        # tabel
        self.tablePembelian = QTableWidget()
        self.tablePembelian .setRowCount(0)
        self.tablePembelian .setColumnCount(6)


        for i in range(len(self.dataPembelian)):
            for j in range(7):
                if j == 6:
                    id = 1
                    deleteButton = QPushButton("Hapus")
                    deleteButton.setStyleSheet("background-color : red;color : white")
                    deleteButton.clicked.connect(lambda : self.deletePembelian(id))
                    self.tablePembelian.setCellWidget(i,j,deleteButton)
                else:
                    self.tablePembelian.setItem(i, j, QTableWidgetItem("saya"))
        self.tablePembelian.setHorizontalHeaderLabels(["Tanggal","Nama Barang","Harga","Qty","Subtotal","Action"])
        self.tablePembelian.verticalHeader().hide()
                
        # hbox
        layoutBawah = QHBoxLayout()

        
        self.totalLabel = QLabel()
        self.totalLabel.setText('Total : {}'.format(self.total))
        
        proses = QPushButton('Proses')
        
        keluar = QPushButton('keluar')

        proses.clicked.connect(self.submitPembelian)
        keluar.clicked.connect(self.close)
        
        layoutBawah.addWidget(self.totalLabel)
        layoutBawah.addWidget(proses)
        layoutBawah.addWidget(keluar)
        

        layout.addWidget(judul)
        layout.addLayout(gridForm)
        layout.addWidget(self.tablePembelian)
        layout.addLayout(layoutBawah)


        self.setLayout(layout)

    def prosesPembelian(self):

        # ambil nilainya
        tanggal = self.addDate.date().toString()
        namaBarang = self.combo.currentText()
        hargaBarang = self.hargaBarang[self.daftarBarang.index(namaBarang)]
        qty = self.qty.text()
        subTotal = str(int(hargaBarang)*int(qty))
        self.total+=int(subTotal)
        self.dataPembelian.append((tanggal,namaBarang,hargaBarang,qty,subTotal))

        self.loadTable()

        self.totalLabel.setText('Total : {}'.format(self.total))


        # kosongkan
        self.qty.setText('')

    def deletePembelian(self,id):
        print('id yang akan didelete',id)
        self.dataPembelian.pop(id)
        self.loadTable()

    def submitPembelian(self):
        print('daftar pembelian',self.dataPembelian)

        # masukkan data ke transaksi
        namaPelanggan = self.addNamaPelanggan.text()
        kontakPelanggan = self.kontak.text()
        tanggalPembelian = self.addDate.date().toString()
        totalPembelian = self.total


        cursorPembelian = db.cursor()
        sql = "INSERT INTO transaksi (nama_pelanggan,kontak, tanggal, total) VALUES (%s, %s, %s, %s)"
        val = (namaPelanggan, kontakPelanggan, tanggalPembelian, str(totalPembelian))
        cursorPembelian.execute(sql, val)

        db.commit()

        print("{} data ditambahkan".format(cursorPembelian.rowcount))

        # get data barang
        # get data from database
        cursor = db.cursor()
        sql = "SELECT * FROM barang"
        cursor.execute(sql)

        results = cursor.fetchall()

        # get inserted transaksi
        cursorGetTransaksi = db.cursor()
        sqlget = "SELECT * FROM transaksi"
        cursorGetTransaksi.execute(sqlget)

        resultsTransaksi = cursorGetTransaksi.fetchall()


        # loopoing berdasarkan data pembelian untuk ambil id nya
        cursorTransaksi = db.cursor()

        sql = """
        INSERT INTO detail_transaksi (id_barang,id_transaksi, harga, qty) VALUES (%s, %s, %s, %s)
        """
        valTransaksi = []

        for data in self.dataPembelian:
            for barang in results:
                if data[1] == barang[1]:
                    valTransaksi.append((str(barang[0]), str(resultsTransaksi[len(resultsTransaksi)-1][0]), str(data[2]), str(data[3])))

                    cursorUpdateBarang = db.cursor()
                    sqlUpdateQty = "UPDATE barang SET ketersediaan = %s WHERE id=%s"
                    val = (str(int(barang[3])-int(data[3])), str(barang[0]))
                    cursorUpdateBarang.execute(sqlUpdateQty, val)

                    db.commit()

                    print("{} data qty barang diupdate".format(cursorUpdateBarang.rowcount))

        cursorTransaksi.executemany(sql, valTransaksi)

        db.commit()
        print("{} data ditambahkan".format(cursorTransaksi.rowcount))

        # reset total setelah submit Pembelian
        self.total = 0
        self.close()

        # get data from database
        cursorTrans = db.cursor()
        sql = "SELECT tanggal, nama_pelanggan, nama_barang, kontak, barang.harga, qty FROM detail_transaksi INNER JOIN transaksi ON detail_transaksi.id_transaksi = transaksi.id INNER JOIN barang ON detail_transaksi.id_barang = barang.id;"
        cursorTrans.execute(sql)

        resultsTrans = cursorTrans.fetchall()


        tableTransaksi.setRowCount(len(resultsTrans))
        tableTransaksi.setColumnCount(len(resultsTrans[0]))

        print(resultsTrans)

        for i, data in enumerate(resultsTrans):
            for j, item in enumerate(data):
                tableTransaksi.setItem(i, j, QTableWidgetItem(str(item)))
        tableTransaksi.verticalHeader().hide()
        tableTransaksi.setHorizontalHeaderLabels(['Tanggal', 'Nama Pelanggan', 'kontak', 'barang', 'harga', 'qty'])

    def loadTable(self):
        # remove row
        for m in range(len(self.dataPembelian)):
            self.tablePembelian.removeRow(m)
        self.tablePembelian.clear()

        print(len(self.dataPembelian))
        for n in range(len(self.dataPembelian)):
            self.tablePembelian.insertRow(n)
        print(self.dataPembelian)
        for i, data in enumerate(self.dataPembelian):
            for j in range(len(data)+1):
                if j == 5:
                    id = i
                    deleteButton = QPushButton("Hapus")
                    deleteButton.setStyleSheet("background-color : red;color : white")
                    deleteButton.clicked.connect(lambda: self.deletePembelian(id))
                    self.tablePembelian.setCellWidget(i, j, deleteButton)
                elif j == 0:
                    date_str = str(data[j])
                    self.tablePembelian.setItem(i, j, QTableWidgetItem(date_str))
                else:
                    new_item = QTableWidgetItem(str(data[j]))
                    self.tablePembelian.setItem(i,j,new_item)
        self.tablePembelian.setHorizontalHeaderLabels(["Tanggal", "Nama Barang", "Harga", "Qty", "Subtotal", "Action"])

def main():
    app = QApplication(sys.argv)
    ex = Apps()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()


# catatan
# terdapat bug yaitu:
# ketika pada halaman pembelian barang yang mau dibeli dihapus, bagian 'total' tidak berubah.