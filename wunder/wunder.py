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
def makeBackUp():
  src = os.path.join(os.getcwd(), "..", "Base", 'aenter.gdb')
  dst = os.path.join(os.getcwd(), 'aenter.wunder.gdb')
  shutil.copy(src, dst)

makeBackUp()
con = open_connection()
artList = []
artNews = []
SELECT = "select id, number from part where"

i = open('wunder.csv', 'r')
for line in i:
  splLine = line.split(';')
  oldArt = splLine[0].replace('"', '')
  newArt = splLine[1].replace('"', '')
  if oldArt == "":
    continue
  if newArt == "":
    continue
  if oldArt in artList:
    continue
  artList.append(oldArt)
  artNews.append(newArt)
  SELECT += " number='"+oldArt+"' or"

SELECT = SELECT[:-3]
  
cur = con.cursor()
cur.execute(SELECT)
result = cur.fetchall()

newData = []
for raw in result:
  partID = raw[0]
  oldArt = raw[1]
  pos = artList.index(oldArt)
  newArt = artNews[pos]
  newData.append((newArt, oldArt, partID))

cur.executemany("update part set number = ?, manufacturecode = ? where id = ?", newData)
con.commit()

