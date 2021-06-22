# -*- coding: utf-8 -*-

import psycopg2
from psycopg2 import sql
import sys
import csv
import random
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QTableWidgetItem, QMessageBox
from DataBaseGUI import Ui_MainWindow
import Connection
import Create
import Cortege
import Attribute
import Change
import Select
import Select_Table


class DB_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(DB_GUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.sql_command  = {}
        self.table        = []
        self.table_header = []
        self.table_name   = "" 
        self.flag = True
       
        self.sql_command["create"]    = "CREATE TABLE {} ({});"
        self.sql_command["select"]    = "SELECT {} FROM {};"
        self.sql_command["selwhe"]    = "SELECT {} FROM {} WHERE {};"
        self.sql_command["insert"]    = "INSERT INTO {} VALUES ({});"
        self.sql_command["addcol"]    = "ALTER TABLE {} ADD COLUMN {} {};"
        self.sql_command["dropcol"]   = "ALTER TABLE {} DROP {};" 
        self.sql_command["delete"]    = "DELETE FROM {} WHERE {};"
        self.sql_command["drop"]      = "DROP TABLE IF EXISTS {};" 
        self.sql_command["sample"]    = "SELECT {} FROM {} WHERE {};"
        self.sql_command["right"]     = "select a.attname  FROM pg_catalog.pg_attribute a inner join pg_catalog.pg_class c on a.attrelid = c.oid where c.relname = '{}'  and a.attnum > 0 and a.attisdropped=false and pg_catalog.pg_table_is_visible(c.oid) order by a.attnum;"
        self.sql_command["change"]    = "UPDATE {} SET {} = {} WHERE {};"
        self.sql_command["copy"]      = "COPY {} FROM {!r} DELIMITER ';' ENCODING 'WIN1251' CSV HEADER";

        self.ui.action_3.triggered.connect(self.save_as)
        self.ui.action_4.triggered.connect(self.close_app)
        self.ui.action_5.triggered.connect(self.showDlgCreateDB)
        self.ui.action_10.triggered.connect(self.showDlgCortegeAdd)
        self.ui.action_11.triggered.connect(self.delete_cortege_db)
        self.ui.action_6.triggered.connect(self.delete_db)
        self.ui.action_9.triggered.connect(self.showDlgConnectionDB)
        self.ui.actionAttribute.triggered.connect(self.showDlgAttributeAdd)
        self.ui.actionAttribute_2.triggered.connect(self.delete_attribute_db)
        self.ui.pushButton.clicked.connect(self.change_cortege)
        self.ui.pushButton2.clicked.connect(self.selects)
     
    def showDlgConnectionDB(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Connection.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)
        self.dlg.show()

        self.dlg_ui.buttonBox.accepted.connect(self.connect_db)
        self.dlg_ui.buttonBox.rejected.connect(self.dlg.close)


    def change_cortege(self):
        self.dlgc = QtWidgets.QDialog()
        self.dlgc_ui = Change.Ui_Dialog()
        self.dlgc_ui.setupUi(self.dlgc)
        self.dlgc.show()
        
        self.dlgc_ui.buttonBox.accepted.connect(self.changeok)
        self.dlgc_ui.buttonBox.rejected.connect(self.dlgc.close)


    def changeok(self):
        try:
            changes_attr=self.dlgc_ui.lineEdit.text()
            usl=self.dlgc_ui.lineEdit_2.text()
            value=self.dlgc_ui.lineEdit_3.text()
            if changes_attr:
                insert = sql.SQL(self.sql_command["change"].format(self.table_name, changes_attr,value,usl))
                self.cursor.execute(insert)	
                self.get_table()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")

    def selects(self):
        self.dlgc = QtWidgets.QDialog()
        self.dlgc_ui = Select.Ui_Dialog()
        self.dlgc_ui.setupUi(self.dlgc)
        self.dlgc.show()
        
        self.dlgc_ui.buttonBox.accepted.connect(self.selectw)
        self.dlgc_ui.buttonBox.rejected.connect(self.dlgc.close)

    attr='req'
    def selectw(self):
        try:
            attr=self.dlgc_ui.lineEdit_2.text()
            usl=self.dlgc_ui.lineEdit.text()
            if attr:
                self.sel_table()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")

    def sel_table(self):
        self.dlgcs = QtWidgets.QDialog()
        self.dlgcs_ui = Select_Table.Ui_Dialog()
        self.dlgcs_ui.setupUi(self.dlgcs)
        s=self.dlgc_ui.lineEdit_2.text()
        u=self.dlgc_ui.lineEdit.text()
        if self.table_name:
            self.cursor.execute(self.sql_command["selwhe"].format(s, self.table_name,u))
            self.table = []
            i=0
            a=s.split(',')
            print(a)
            k=0
            t=0
            l=len(self.table_header)
            while i < l:
                while t < len(a):
                    if self.table_header[i]==a[t]:
                        k=1
                    t=t+1
                t=0
                if k==1:
                    for j in self.cursor:
                            self.table.append(j)
                else:
                    self.table_header.pop(i)
                    l=len(self.table_header)
                    continue;
                i=i+1
                k=0
            
        self.dlgcs_ui.tableWidget.setRowCount(len(self.table))
        self.dlgcs_ui.tableWidget.setColumnCount(len(self.table_header))
        self.dlgcs_ui.tableWidget.setHorizontalHeaderLabels(self.table_header)

        row = 0
        for tup in self.table:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(str(item))
                cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.dlgcs_ui.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1 
        self.dlgcs.show()
        self.attribute_list()
        self.dlgcs_ui.buttonBox.accepted.connect(self.selectw)
        self.dlgcs_ui.buttonBox.rejected.connect(self.dlgcs.close)
        
    def connect_db(self):
        self.dlg.close()
        try:
            self.conn = psycopg2.connect(dbname=self.dlg_ui.lineEdit.text(),
                                            user=self.dlg_ui.lineEdit_2.text(),
                                            password=self.dlg_ui.lineEdit_3.text(),
                                            host=self.dlg_ui.lineEdit_4.text())
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()

            self.cursor.execute("select table_name from information_schema.tables where table_schema \
                                        not in ('information_schema','pg_catalog');")
            self.init_comboBox()
            self.ui.label_3.setText(self.dlg_ui.lineEdit.text())
        except:
            QMessageBox.critical(self, "Error", "Unknown error")

    def update_table_name(self, name):
        self.table_name = name
        self.get_table()

    def attribute_list(self):
        self.cursor.execute(self.sql_command["right"].format(self.table_name))
        self.table_header = []
        for i in self.cursor:
            print(self.table_header)
            self.table_header.append(i[0])

    def update_table(self):
        self.attribute_list()
        self.ui.tableWidget.setRowCount(len(self.table))
        self.ui.tableWidget.setColumnCount(len(self.table_header))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.table_header)

        row = 0
        for tup in self.table:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(str(item))
                cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1 

    def get_table(self):
        if self.table_name:
            self.cursor.execute(self.sql_command["select"].format('*', self.table_name))

            self.table = []
            for i in self.cursor:
                self.table.append(i)

            self.attribute_list()
            self.update_table()


    def showDlgCreateDB(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Create.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)

        self.dlg_ui.buttonBox.accepted.connect(self.create_db)
        self.dlg_ui.buttonBox.rejected.connect(self.dlg.close)
        self.dlg_ui.tableWidget.setHorizontalHeaderLabels(('Name atribute', 'Type'))

        for row in range(self.dlg_ui.tableWidget.rowCount()):
            combo = QtWidgets.QComboBox(self.dlg)
            combo.addItem("INT")
            combo.addItem("REAL")
            combo.addItem("TEXT")
            combo.addItem("TIME")
            combo.addItem("DATE")
            self.dlg_ui.tableWidget.setCellWidget(row, 1, combo)
        self.dlg.show()

    def create_db(self):
        self.dlg.close()
        try:
            data = "" 

            for i in range(self.dlg_ui.tableWidget.rowCount()):
                if self.dlg_ui.tableWidget.item(i, 0):
                    data += "{} {},".format(self.dlg_ui.tableWidget.takeItem(i, 0).text(),
                                            self.dlg_ui.tableWidget.cellWidget(i, 1).currentText())

            self.table_name = self.dlg_ui.lineEdit.text() 
            self.cursor.execute(self.sql_command["create"].format(self.table_name, data[:-1]))
            self.table_names.append(self.table_name)
            self.update_comboBox()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")

    def showDlgCortegeAdd(self):
        self.dlg = QtWidgets.QDialog()
        self.dlg_ui = Cortege.Ui_Dialog()
        self.dlg_ui.setupUi(self.dlg)

        self.dlg_ui.tableWidget.setColumnCount(len(self.table_header))
        self.dlg_ui.tableWidget.setHorizontalHeaderLabels(self.table_header)
        self.dlg.show()

        self.dlg_ui.buttonBox.accepted.connect(self.insert_cortege_db)
        self.dlg_ui.buttonBox.rejected.connect(self.dlg.close)

    def insert_cortege_db(self):
        try:
            text = ""
            for row in range(self.dlg_ui.tableWidget.rowCount()):
                for col in range(len(self.table_header)):
                    if self.dlg_ui.tableWidget.item(row, col):
                        text += self.dlg_ui.tableWidget.item(row, col).text() + ','
                    else:
                        text += "NULL" + ','
            if text:
                insert = sql.SQL(self.sql_command["insert"].format(self.table_name, text[:-1]))
                self.cursor.execute(insert)	
                self.get_table()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")


    def delete_cortege_db(self):
        try:
            text, ok = QInputDialog.getText(self, "Drop", "Which cortege to drop: ")
            if text and ok:
                insert = sql.SQL(self.sql_command["delete"].format(self.table_name, text))
                self.cursor.execute(insert)	
                self.get_table()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")

    def showDlgAttributeAdd(self):
        self.dlga = QtWidgets.QDialog()
        self.dlga_ui = Attribute.Ui_Dialog()
        self.dlga_ui.setupUi(self.dlga)

        self.dlg_ui.tableWidget.setColumnCount(len(self.table_header))
        self.dlg_ui.tableWidget.setHorizontalHeaderLabels(self.table_header)
        self.dlga.show()

        self.dlga_ui.buttonBox.accepted.connect(self.insert_attribute_db)
        self.dlga_ui.buttonBox.rejected.connect(self.dlga.close)

    def insert_attribute_db(self):
        try:
            text = self.dlga_ui.lineEdit.text()
            type1 = self.dlga_ui.comboBox.currentText()
            if text:
                insert = sql.SQL(self.sql_command["addcol"].format(self.table_name, text,type1))
                self.cursor.execute(insert)	
                self.get_table()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")


    def delete_attribute_db(self):
        try:
            text, ok = QInputDialog.getText(self, "Drop", "Which attribute to drop: ")
            if text and ok:
                insert = sql.SQL(self.sql_command["dropcol"].format(self.table_name, text))
                self.cursor.execute(insert)	
                self.get_table()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")


    def delete_db(self):
        try:
            if self.table_names:
                self.table_name, ok = QInputDialog.getItem(self, "Select table",
                                                            "Name table:", self.table_names, 0, False)
            if ok and self.table_name:
                self.cursor.execute(self.sql_command["drop"].format(self.table_name))
                self.table_names.remove(self.table_name)
                self.update_comboBox()
        except:
            QMessageBox.critical(self, "Error", "Unknown error")


    def init_comboBox(self):
        self.table_names = []
        for name in self.cursor:
            self.table_names.append(name[0])
        self.update_comboBox()
        if self.table_names:
            self.table_name = self.table_names[0]
        self.get_table()

    def update_comboBox(self):
        self.ui.comboBox.clear()
        for name in self.table_names:
            self.ui.comboBox.addItem(name)

        self.ui.comboBox.currentTextChanged.connect(self.update_table_name)

    def save(self):
        try:
            with open(self.fname, "w", errors='ignore', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(self.table_header)
                for row in self.table: 
                    writer.writerow(row)
        except IOError:
            QMessageBox.critical(self, "Error", "File not save")
    
    def save_as(self):
        self.fname = QFileDialog.getSaveFileName(self, 'Save as...', '/BD')[0]
        try:
            with open(self.fname, "w", errors='ignore', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(self.table_header)
                for row in self.table: 
                    writer.writerow(row)
        except IOError:
            QMessageBox.critical(self, "Error", "File not save")

    def close_app(self):
        self.conn.close()
        self.close()


def main():
    app = QtWidgets.QApplication([])
    application = DB_GUI()
    application.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
