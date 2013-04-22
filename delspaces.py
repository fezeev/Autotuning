#!/usr/bin/python
# -*- coding: windows-1251 -*-

import fdb, os, os.path
import shutil

def open_connection():
  return fdb.connect(dsn = "localhost:"+os.path.join(os.getcwd(), "..", "Base", 'aenter.gdb'), user = 'SYSDBA', password = 'masterkey', charset='WIN1251')
def executeSQL(SQL):
  cur = con.cursor()
  cur.execute(SQL)
  return cur.fetchall()

def isBMW(articul):
  if len(articul) != 15:
    return False
  if not articul[0:2].isdigit():
    return False
  if articul[2] != " ":
    return False
  if not articul[3:5].isdigit():
    return False
  if articul[5] != " ":
    return False
  if not articul[6].isdigit():
    return False
  if articul[7] != " ":
    return False
  if not articul[8:11].isdigit():
    return False
  if articul[11] != " ":
    return False
  if not articul[12:15].isdigit():
    return False

  return True

def delSpaces(articul):
  result = articul.replace(' ', '')
  return result

def writeResult(newData):
  #print(newData[:10])

  SQL = "update PART set MANUFACTURECODE = ? where ID = ?"

  cur = con.cursor()
  cur.executemany(SQL, newData)
  con.commit()
  print("Wrote "+str(len(newData))+" partnumbers")
  

def makeBackUp():
  src = os.path.join(os.getcwd(), "..", "Base", 'aenter.gdb')
  dst = os.path.join(os.getcwd(), 'aenter.delspaces.gdb')
  shutil.copy(src, dst)


makeBackUp()

con = open_connection()

allBMW = executeSQL("select ID, NUMBER from PART where NUMBER is not NULL and MANUFACTURECODE is NULL")
#print(len(allBMW))
#print(allBMW[:10])

result = []
for raw in allBMW:
  partID=raw[0]
  partNum=raw[1]

  if isBMW(partNum):
    result.append((delSpaces(partNum), partID))

writeResult(result)
