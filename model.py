#!/usr/bin/python
# -*- coding: windows-1251 -*-

import os, os.path, fdb, codecs

def Float(s):
    return float(s.replace(",", "."))

class NameWithID():
    def __init__(self):
        self.ID = 0
        self.Name = u"<Не выбрано>"
    def getID(self):
        return self.ID
    def getName(self):
        return self.Name
    def setAll(self, raw):
        self.ID = raw[0]
        self.Name = raw[1]

class PartFolder(NameWithID):
    def __init__(self):
        NameWithID.__init__(self)
        self.Name = u"<Не выбрана>"
    def setFolder(self, raw):
        self.setAll(raw)
        
class Postav(NameWithID):
    def __init__(self):
        NameWithID.__init__(self)
        self.Name = u"<Не выбран>"
    def setPostav(self, raw):
        self.setAll(raw)

class Store(NameWithID):
    def __init__(self):
        NameWithID.__init__(self)
        self.Name = u"<Не выбран>"
    def setStore(self, raw):
        self.setAll(raw)

class appData():
    def __init__(self):
        self.__pathDB = os.path.abspath(os.path.join(os.getcwd(), "..", "Base", "AEnter.gdb"))
        self.__pathCSV = ""
        self.__Postav = Postav()
        self.__Sklad = Store()
        self.__PartFolder = PartFolder()
        self.__Author = None

        self.weID = 1
        self.DocType = 1

        self.__db = fdb.connect(dsn="localhost:"+self.__pathDB, user='SYSDBA', password='masterkey', charset='WIN1251')

    def getPathDB(self):
        return self.__pathDB
    def getPathCSV(self):
        return self.__pathCSV
    def setPathCSV(self, path):
        self.__pathCSV = path
    def getPostav(self):
        return self.__Postav
    def setPostav(self, postData):
        self.__Postav.setPostav(postData)
    def getStore(self):
        return self.__Sklad
    def setStore(self, data):
        self.__Sklad.setStore(data)
    def getPartFolder(self):
        return self.__PartFolder
    def setPartFolder(self, pfData):
        self.__PartFolder.setFolder(pfData)
    def getAuthor(self):
        return self.__Author
    def setSklad(self, authorID):
        self.__Author = authorID

    def getAllPartFolders(self):
        cur = self.__db.cursor()
        cur.execute("select id,name,parent from parttree order by treelevel, parent, codegroup")
        result = cur.fetchall()
        return result
    def getAllPostav(self):
        cur = self.__db.cursor()
        cur.execute("select id, nameshort, 0 from contragent") # TODO добавить фильтр только на поставщиков
        result = cur.fetchall()
        return result

    def executeSQL(self, SQL):
        cur = self.__db.cursor()
        cur.execute(SQL)
        return cur.fetchall()

    def insertSQL(self, tableName, entry):
        questions = "?, " * len(entry)
        keys = ", ".join(entry.keys())
        values = [tuple(entry.values()),]

        SQL =  "insert into "+tableName+" ("
        SQL += keys
        SQL += ") values ("+questions[:-2]+")"
        cur = self.__db.cursor()
        cur.executemany(SQL, values)
        self.__db.commit()

    def getNextID(self, sequence):
        SQL = "select next value for "+sequence+" from RDB$DATABASE"
        return self.executeSQL(SQL)[0][0]

    def getNextNum(self, table):
        SQL = "select max(number) from "+table+" where iddoctype=1"
        return self.executeSQL(SQL)[0][0] + 1

    def getPriceCoeffitients(self):
        SQL = "select coeffr, coeffmo, coeffo, coeffs from options where idcontragent = "+str(self.weID)
        result = self.executeSQL(SQL)
        return result[0]

    def createPart(self, rawEntry):
        coeffr, coeffmo, coeffo, coeffs = self.getPriceCoeffitients()
        entry = {
            "ID":         self.getNextID("PART_ID"),
            "IDPARTTREE": self.getPartFolder().getID(),
            "NAME":       rawEntry[4],
            "NAMESHORT":  rawEntry[4][:40],
            "FIRM":       self.getPostav().getID(),
            "NUMBER":     rawEntry[1],

    
            "COEFFR":  coeffr,
            "COEFFMO": coeffmo,
            "COEFFO":  coeffo,
            "COEFFS":  coeffs,

            "PRICER":  Float(rawEntry[3]) * coeffr,
            "PRICEMO": Float(rawEntry[3]) * coeffmo,
            "PRICEO":  Float(rawEntry[3]) * coeffo,
            "PRICES":  Float(rawEntry[3]) * coeffs,

            # TODO MAGIC VALUES
            "IDCOUNTRY": 3,
            "UNITDIMENSION": 1,
            "SETHANDS": "F",
    
            "NDS": 0,
            "NFS": 0,
            "INDEXNAME": "-",
            "WEIGTH": 0,
            "VOLUME": 0,
            "MATERIAL": 2,
            "WORKPERIOD": 0,
            "QUANTITYPERCAR": 0,

            "AMOUNTINPACKAGE":                 0,
            "KINDOFPACKING":                   1,
            "AMOUNTINCONTAINER":               0,
            "KINDOFCONTAINER":                 5,

            "MINSTOCK":                        0,
            "MAXSTOCK":                        0,
            "INSURANCESTOCK":                  0,
            "DELIVERYDATE":                    0,
    
            "MINQUANTITYORDE":                 0,
            "OPTIMUMQUANTITYORDE":             0,

            "BACKLOGDEMAND":                   0,
            "GROUPOFDEMAND":                   -1,

            "BARCODETYPE":                     -1,
            "BARCODE":                         0,

            "CURRENCY":                        "РУБ",
            "UNIT":                            "шт.",
            #"CODEUIN":                         35000021,
            #"CODEGROUP":                       21,

            "IDMARK":                          0,
            "PRICESOURCE":                     0,
    

        }
        self.insertSQL("part", entry)
        return entry["ID"]


    def getPartIDFromArticul(self, rawEntry):
        articul = rawEntry[1]
        #print(articul)
        result = self.executeSQL("select id from part where NUMBER='"+articul+"'")
        if result == []:
            result = self.createPart(rawEntry)
        else:
            result = result[0][0]
        return result


    def getEntryForDocLine(self, rawEntry):
        result = {
            "ID":            self.getNextID("DOCPARTS_ID"),
            "IDCONTRAGENT":  self.weID,
            "IDPART":        self.getPartIDFromArticul(rawEntry),
            "IDDOCHEAD":     self.docheader_ID,
            "SUMMCURRENCY":  Float(rawEntry[3]),
            "COUNTS":        Float(rawEntry[2]),

            "TYPECURRENCY":  1,
            "CURRENCYSHORT": "РУБ", # TODO MAGIC VALUES
            "DIRECTION":     0,
            "SDISCOUNT":     0,
            "SNDS":          0,
            "SNFS":          0,

            "SKLAD":         "A", # TODO MAGIC VALUE
            "INDEXNAME":     "A01", # TODO MAGIC VALUE
        }
        return result


    def read_file(self):
        f = codecs.open(self.__pathCSV, 'r', 'cp1251')
        lines = f.readlines()
        f.close()

        self.Number = self.getNextNum("docnumber")
        self.contragentmoney_ID = self.getNextID("CONTRAGENTMONEY_ID")
        self.direxchange_ID = self.getNextID("DIREXCHANGE_ID")
        self.docheader_ID = self.getNextID("DOCHEADER_ID")
        self.docnumber_ID = self.getNextID("DOCNUMBER_ID")

        self.doclines = []
        totalSum = float(0)
        for line in lines[1:]:
            rawEntry = line.split(";")
            self.doclines.append(self.getEntryForDocLine(rawEntry))
            value = Float(rawEntry[2])
            price = Float(rawEntry[3])
                
            totalSum += value * price

        self.money = totalSum

    def update_contragentmoney(self):
        entry = {
            "ID": self.contragentmoney_ID,
            "IDCONTRAGENTIN": self.weID,
            "IDCONTRAGENTOUT": self.getPostav().getID(),
            "IDCONTRAGENT": self.getPostav().getID(),
            "NAMECONTRAGENT": self.getPostav().getName(),
            "IDDOC": self.docheader_ID,
            "MONEY": self.money,
            "DIRECTION": 1,
            "TYPEDOC": -1,
        }
        self.insertSQL("contragentmoney", entry)

    def update_docheader(self):
        entry = {
            "ID":               self.docheader_ID,
            "IDCONTRAGENTOUT":  self.getPostav().getID(),
            "IDCONTRAGENTIN":   self.weID, 
            "NUMBER":           self.Number,
            "IDDOCTYPE":        self.DocType,
            "SUMM":             self.money,
            "BALANCE":          self.money,
            "SUMMPART":         self.money,
            "DIRECTION":        1, # TODO MAGIC VALUE
            "IDFOULDER":        3, # TODO MAGIC VALUE
            "STATUSDOC":        "F",
        }
        self.insertSQL("docheader", entry)


    def update_docnumber(self):
        entry = {
            "ID":             self.docnumber_ID, 
            "IDOPTIONS":      1, 
            "NUMBER":         self.Number, 
            "IDDOCTYPE":      1, 
        }
        self.insertSQL("docnumber", entry)

    def update_docparts(self):
        for docline in self.doclines:
            self.insertSQL("docparts", docline)


    def AllOk(self):
        return True # TODO
    def LoadIncome(self):
        #pass
        self.read_file()
        
        self.update_contragentmoney()
        self.update_docheader()
        self.update_docnumber()
        self.update_docparts()

        return self.Number
    def LoadOutcome(self):
        print("TODO")
