#!/usr/bin/python
# -*- coding: windows-1251 -*-

import fdb, codecs, os, os.path, sys

def Float(s):
  return float(s.replace(",", "."))

def executeSQL(SQL):
  cur = con.cursor()
  cur.execute(SQL)
  return cur.fetchall()

def insertSQL(tableName, entry):
  questions = "?, " * len(entry)
  keys = ", ".join(entry.keys())
  values = [tuple(entry.values()),]

  SQL =  "insert into "+tableName+" ("
  SQL += keys
  SQL += ") values ("+questions[:-2]+")"
  cur = con.cursor()
  cur.executemany(SQL, values)
  con.commit()
  

def getNextID(sequence):
  SQL = "select next value for "+sequence+" from RDB$DATABASE"
  return executeSQL(SQL)[0][0]

def getNextNum(table):
  SQL = "select max(number) from "+table+" where iddoctype=1"
  return executeSQL(SQL)[0][0] + 1

def findContrIDByName(name):
  searchName = name[1:-3]
  searchName = searchName.replace('""', '"')

  SQL = "select id from contragent where nameshort='"+searchName+"'"
  result = executeSQL(SQL)
  if result == []:
    return -1
  #print(result)
  return result[0][0]

def createFirm(name):
  entry = {
    "ID": getNextID("DIRFIRMS_ID"),
    "FULLNAME": name,
  }
  insertSQL("DIRFIRMS", entry)
  return entry["ID"]

def getFirmCodeByName(firmName):
  SQL = "select ID from DIRFIRMS where FULLNAME='"+firmName+"'"
  result = executeSQL(SQL)
  if result == []:
    result = createFirm(firmName)
  else:
    result = result[0][0]
  return result



class Vars:

  def getPriceCoeffitients(self):
    SQL = "select coeffr, coeffmo, coeffo, coeffs from options where idcontragent = "+str(self.weID)
    result = executeSQL(SQL)
    return result[0]

  def createPart(self, rawEntry):
    coeffr, coeffmo, coeffo, coeffs = self.getPriceCoeffitients()
    entry = {
      "ID":         getNextID("PART_ID"),
      "IDPARTTREE": 51, # TODO - create special folder
      "NAME":       rawEntry[4],
      "NAMESHORT":  rawEntry[4][:40],
      "FIRM": getFirmCodeByName(rawEntry[0]),
      "NUMBER": rawEntry[1],

    
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
    insertSQL("part", entry)
    return entry["ID"]

  def getPartIDFromArticul(self, rawEntry):
    articul = rawEntry[1]
    #print(articul)
    result = executeSQL("select id from part where NUMBER='"+articul+"'")
    if result == []:
      result = self.createPart(rawEntry)
    else:
      result = result[0][0]
    return result

  def getEntryForDocLine(self, rawEntry):
    result = {
      "ID":            getNextID("DOCPARTS_ID"),
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

  def __init__(self, lines):
    line = lines[0].split(";")
    contrName = line[-1]
    contrID = findContrIDByName(contrName)
    if contrID == -1:
      raise("Cannot find contr by name: \""+contrName+"\"")

    self.ContrID = contrID
    self.ContrName = contrName
    self.data = "18-MAR-2013"
    self.weID = 1
    self.Number = getNextNum("docnumber")
    self.DocType = 1
    
    self.contragentmoney_ID = getNextID("CONTRAGENTMONEY_ID")
    self.direxchange_ID = getNextID("DIREXCHANGE_ID")
    self.docheader_ID = getNextID("DOCHEADER_ID")
    self.docnumber_ID = getNextID("DOCNUMBER_ID")

    self.doclines = []
    totalSum = float(0)
    for line in lines:
      rawEntry = line.split(";")
      self.doclines.append(self.getEntryForDocLine(rawEntry))
      value = Float(rawEntry[2])
      price = Float(rawEntry[3])
      
      totalSum += value * price

    self.money = totalSum

def read_file():
  f = codecs.open('louis.csv', 'r', 'cp1251')
  lines = f.readlines()
  f.close()

  return Vars(lines[1:])

def open_connection():
  return fdb.connect(dsn = "localhost:"+os.path.join(os.getcwd(), "..", "Base", 'aenter.gdb'), user = 'SYSDBA', password = 'masterkey', charset='WIN1251')
  

def update_contragentmoney():
  entry = {
    "ID": v.contragentmoney_ID,
    "IDCONTRAGENTIN": v.weID,
    "IDCONTRAGENTOUT": v.ContrID,
    "IDCONTRAGENT": v.ContrID,
    "NAMECONTRAGENT": v.ContrName,
    "IDDOC": v.docheader_ID,
    "DATA": v.data,
    "MONEY": v.money,
    "DIRECTION": 1,
    "TYPEDOC": -1,
  }
  insertSQL("contragentmoney", entry)

def update_direxchange():
  entry = {
    "IN_ID":         1,
    "OUT_ID":        1,
    "DATEEXCHANGE":  v.data,
    "ID":            v.direxchange_ID,
    "EXCHANGE":      1,
  }
  insertSQL("direxchange", entry)

def update_docheader():
  entry = {
    "ID":               v.docheader_ID,
    "IDCONTRAGENTOUT":  v.ContrID,
    "IDCONTRAGENTIN":   v.weID, 
    "NUMBER":           v.Number,
    "IDDOCTYPE":        v.DocType,
    "SUMM":             v.money,
    "BALANCE":          v.money,
    "SUMMPART":         v.money,
    "DIRECTION":        1, # TODO MAGIC VALUE
    "IDFOULDER":        3, # TODO MAGIC VALUE
    "STATUSDOC":        "F",
  }
  insertSQL("docheader", entry)
  #return entry["ID"]

def update_docnumber():
  entry = {
    "ID":             v.docnumber_ID, 
    "IDOPTIONS":      1, 
    "NUMBER":         v.Number, 
    "IDDOCTYPE":      1, 
    "DATENUMERATION": v.data,
  }
  insertSQL("docnumber", entry)

def update_docparts():
  for docline in v.doclines:
    insertSQL("docparts", docline)

con = open_connection()
v = read_file()

update_contragentmoney()
#update_direxchange()
update_docheader()
update_docnumber()
update_docparts()
print("Document number "+str(v.Number)+" created")
con.close()
