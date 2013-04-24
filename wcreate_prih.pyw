#!/usr/bin/python
# -*- coding: windows-1251 -*-

import wx
import wx.lib.filebrowsebutton as filebrowse

import fdb, os, os.path, codecs

def Float(s):
    return float(s.replace(",", "."))

def ThreePointBMP():
    # make a custom bitmap showing "..."
    bw, bh = 14, 16
    bmp = wx.EmptyBitmap(bw,bh)
    dc = wx.MemoryDC(bmp)

    # clear to a specific background colour
    bgcolor = wx.Colour(255,254,255)
    dc.SetBackground(wx.Brush(bgcolor))
    dc.Clear()

    # draw the label onto the bitmap
    label = "..."
    font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    dc.SetFont(font)
    tw,th = dc.GetTextExtent(label)
    dc.DrawText(label, (bw-tw)/2, (bw-tw)/2)
    del dc

    # now apply a mask using the bgcolor
    bmp.SetMaskColour(bgcolor)

    return bmp


class ChooseFromTree(wx.TreeCtrl):
    def __init__(self, parent, rawTree):
        wx.TreeCtrl.__init__(self, parent, -1, (0, 180), (490, 290))
        
        rootID = self.AddRoot("", data = wx.TreeItemData(rawTree[0]))
        ids = {0: rootID}
        for raw in rawTree[1:]:
            item = self.AppendItem(ids[raw[2]], raw[1], data = wx.TreeItemData(raw))
            ids[raw[0]] = item
        self.Expand(rootID)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.TreeSelChanged)

    def TreeSelChanged(self, evt):
        rawData = self.GetPyData(evt.GetItem())
        parent = self.GetParent()
        parent.selectedData = rawData
    
class ChooseFromTreeDlg(wx.Dialog):
    def __init__(self, rawTree, title):
        wx.Dialog.__init__(self, None, -1, title)

        sizer = wx.BoxSizer(wx.VERTICAL)
        tree = ChooseFromTree(self, rawTree)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(tree, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def getResult(self):
        return self.selectedData
        
class MainFrame(wx.Frame):
    def __init__(self, v):
        self.v = v
        wx.Frame.__init__(self, None, -1, "Загрузка приходов", (10, 10))

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.panel = wx.Panel(self, -1)

        self.txt_Header = wx.StaticText(self.panel, -1, "Загрузка приходов в АвтоСервис", style = wx.ALIGN_CENTER)
        self.txt_Header.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

        self.cvsFBB = filebrowse.FileBrowseButton(self.panel, -1, changeCallback = self.setPathCSV,
                                                  labelText = 'Файл с данными:', buttonText = '...', fileMask = '*.csv')

        self.txt_DBPath = wx.StaticText(self.panel, -1, "Путь к базе данных: "+self.v.getPathDB())

        self.txt_Folder = wx.StaticText(self.panel, -1, "Папка в каталоге товаров:")
        self.btn_Folder = wx.Button(self.panel, -1, "...")
        self.Bind(wx.EVT_BUTTON, self.ChoosePartFolder, self.btn_Folder)
        self.textPartFolder = wx.TextCtrl(self.panel, 1, self.v.getPartFolder().getName(), style= wx.TE_READONLY)

        self.txt_Suppl = wx.StaticText(self.panel, -1, "Поставщик:")
        self.btn_Suppl = wx.Button(self.panel, -1, "...")
        self.Bind(wx.EVT_BUTTON, self.ChoosePostav, self.btn_Suppl)
        self.textPostav = wx.TextCtrl(self.panel, -1, self.v.getPostav().getName(), style = wx.TE_READONLY)

        self.btn_Run = wx.Button(self.panel, -1, "Загрузить")
        self.Bind(wx.EVT_BUTTON, self.Run, self.btn_Run)

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.BoxSizer(wx.HORIZONTAL)
        title.Add(self.txt_Header, 1, wx.ALL, 5)
        sizer.Add(title, 0, wx.EXPAND)

        csv = wx.BoxSizer(wx.HORIZONTAL)
        csv.Add(self.cvsFBB, 1)
        sizer.Add(csv, 0, wx.EXPAND)

        pFolder = wx.BoxSizer(wx.HORIZONTAL)
        pFolder.Add(self.txt_Folder, 0, wx.ALL|wx.ALIGN_CENTER, 3)
        pFolder.Add(self.textPartFolder, 1, wx.ALL|wx.ALIGN_CENTER, 2)
        pFolder.Add(self.btn_Folder, 0, wx.ALL|wx.ALIGN_CENTER, 3)
        sizer.Add(pFolder, 0, wx.EXPAND)

        suppl = wx.BoxSizer(wx.HORIZONTAL)
        suppl.Add(self.txt_Suppl, 0, wx.ALL|wx.ALIGN_CENTER, 3)
        suppl.Add(self.textPostav, 1, wx.ALL|wx.ALIGN_CENTER, 2)
        suppl.Add(self.btn_Suppl, 0, wx.ALL|wx.ALIGN_CENTER, 3)
        sizer.Add(suppl, 0, wx.EXPAND)

        dbPath = wx.BoxSizer(wx.HORIZONTAL)
        dbPath.Add(self.txt_DBPath, 1, wx.ALL, 3)
        sizer.Add(dbPath, 0, wx.EXPAND)

        btn = wx.BoxSizer(wx.HORIZONTAL)
        btn.Add(wx.StaticText(self.panel, -1, ""), 1) # грубый хак, чтобы кнопка была выровнена по правому краю
        btn.Add(self.btn_Run, 0, wx.ALL, 3)
        sizer.Add(btn, 0, wx.EXPAND)

        self.panel.SetSizer(sizer)
        self.Layout()
        sizer.Fit(self)

    def ChoosePostav(self, evt):
        PostList = self.v.getAllPostav()
        pDlg = ChooseFromTreeDlg(PostList, "Выберите поставщика")
        if pDlg.ShowModal() == wx.ID_OK:
            self.v.setPostav(pDlg.getResult())
            self.textPostav.SetLabel(self.v.getPostav().getName())
        pDlg.Destroy()
        

    def ChoosePartFolder(self, evt):
        FoldersTree = self.v.getAllPartFolders()
        ptDlg = ChooseFromTreeDlg(FoldersTree, "Выберите папку")
        if ptDlg.ShowModal() == wx.ID_OK:
            self.v.setPartFolder(ptDlg.getResult())
            self.textPartFolder.SetLabel(self.v.getPartFolder().getName())
        ptDlg.Destroy()

    def setPathCSV(self, evt):
        self.v.setPathCSV(evt.GetString())
        
    def Run(self, evt):
        if self.v.AllOk():
            num = self.v.Run()

            dlg = wx.MessageDialog(self, 'Загружена накладная номер '+str(num), 'All done!', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
class myApp(wx.App):
    def OnInit(self):
        model = appData()
        view = MainFrame(model)
        view.Show(True)
        self.SetTopWindow(view)
        return True

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

class appData():
    def __init__(self):
        self.__pathDB = os.path.join(os.getcwd(), "..", "Base", "AEnter.gdb")
        self.__pathCSV = ""
        self.__Postav = Postav()
        self.__Sklad = ""
        self.__PartFolder = PartFolder()
        self.__Author = None

        self.weID = 1
        self.data = "18-MAR-2013" # TODO
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
    def getSklad(self):
        return self.__Sklad
    def setSklad(self, skladID):
        self.__Sklad = skladID
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
            "IDPARTTREE": self.getPartFolder().getID(), # TODO - create special folder
            "NAME":       rawEntry[4],
            "NAMESHORT":  rawEntry[4][:40],
            "FIRM":       self.getPostav().getID(),   ##########
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
            self.doclines.append(self.getEntryForDocLine(rawEntry)) # TODO
            value = Float(rawEntry[2])
            price = Float(rawEntry[3])
                
            totalSum += value * price

        self.money = totalSum

    def update_contragentmoney(self):
        entry = {
            "ID": self.contragentmoney_ID,
            "IDCONTRAGENTIN": self.weID,
            "IDCONTRAGENTOUT": self.getPostav().getID(), #ContrID,
            "IDCONTRAGENT": self.getPostav().getID(), #self.ContrID,
            "NAMECONTRAGENT": self.getPostav().getName(), #self.ContrName,
            "IDDOC": self.docheader_ID,
            "DATA": self.data,
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
            "DATENUMERATION": self.data,
        }
        self.insertSQL("docnumber", entry)

    def update_docparts(self):
        for docline in self.doclines:
            self.insertSQL("docparts", docline)


    def AllOk(self):
        return True # TODO
    def Run(self):
        #pass
        self.read_file()
        
        self.update_contragentmoney()
        self.update_docheader()
        self.update_docnumber()
        self.update_docparts()

        return self.Number


def main():
    app = myApp()
    #app.RedirectStdio('err.log')
    print("==Last start begins here==")
    app.MainLoop()


if __name__ == '__main__':
    main()
