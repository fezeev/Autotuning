#!/usr/bin/python
# -*- coding: windows-1251 -*-

import wx
import fdb, os, os.path, codecs

def Float(s):
    return float(s.replace(",", "."))

class ChooseFromTree(wx.TreeCtrl):
    def __init__(self, parent, rawTree):
        wx.TreeCtrl.__init__(self, parent, -1, (0, 180), (490, 290))
        
        rootID = self.AddRoot("", data = wx.TreeItemData(rawPartTree[0]))
        ids = {0: rootID}
        for raw in rawPartTree[1:]:
            item = self.AppendItem(ids[raw[2]], raw[1], data = wx.TreeItemData(raw))
            ids[raw[0]] = item
        self.Expand(rootID)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.TreeSelChanged, self)

    def TreeSelChanged(self, evt):
        rawData = self.GetPyData(evt.GetItem())
        parent = self.GetParent()
        parent.selectedData = rawData
    
class PostList(wx.TreeCtrl):
    def __init__(self, parent, rawPostList):
        wx.TreeCtrl.__init__(self, parent, -1, (0, 180), (490, 290))
        
        rootID = self.AddRoot("", data = wx.TreeItemData(rawPostList[0]))
        for raw in rawPostList[1:]:
            item = self.AppendItem(rootID, raw[1], data = wx.TreeItemData(raw))
        self.Expand(rootID)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.TreeSelChanged, self)

    def TreeSelChanged(self, evt):
        rawData = self.GetPyData(evt.GetItem())
        parent = self.GetParent()
        parent.selectedPost = rawData
    
class FolderTree(wx.TreeCtrl):
    def __init__(self, parent, rawPartTree):
        wx.TreeCtrl.__init__(self, parent, -1, (0, 180), (490, 290))
        
        rootID = self.AddRoot("", data = wx.TreeItemData(rawPartTree[0]))
        ids = {0: rootID}
        for raw in rawPartTree[1:]:
            item = self.AppendItem(ids[raw[2]], raw[1], data = wx.TreeItemData(raw))
            ids[raw[0]] = item
        self.Expand(rootID)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.TreeSelChanged, self)

    def TreeSelChanged(self, evt):
        rawData = self.GetPyData(evt.GetItem())
        parent = self.GetParent()
        parent.selectedFolder = rawData
        
class PostListDlg(wx.Dialog):
    def __init__(self, rawPostList):
        wx.Dialog.__init__(self, None, -1, "Выберите поставщика")
        self.selectedPost = "jhgkjhfvkhv"
        sizer = wx.BoxSizer(wx.VERTICAL)

        tree = PostList(self, rawPostList)
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
        return self.selectedPost

class PartTreeDlg(wx.Dialog):
    def __init__(self, rawPartTree):
        wx.Dialog.__init__(self, None, -1, "Выберите папку")
        self.selectedFolder = u"<Не выбрана>"

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        tree = FolderTree(self, rawPartTree)
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
        return self.selectedFolder
    
        
class MainFrame(wx.Frame):
    def __init__(self, v):
        self.v = v
        
        wx.Frame.__init__(self, None, -1, "This is a test", (10, 10), (500, 500))
        self.Show(True)

        csvText = wx.StaticText(self, -1, "Выберите файл с данными", (0,0))
        b = wx.Button(self, -1, "csv", (200, 0))
        self.Bind(wx.EVT_BUTTON, self.ChooseCSV, b)

        csvFilePathText = wx.StaticText(self, -1, "Выбран файл с данными: ", (0, 30))
        self.csvFilePath = wx.StaticText(self, -1, self.v.getPathCSV(), (0, 60))

        txt = wx.StaticText(self, -1, "Путь к базе данных: "+self.v.getPathDB(), (0, 90))

        txt = wx.StaticText(self, -1, "Папка в каталоге товаров:", (0, 120))
        bp = wx.Button(self, -1, "fld", (200, 120))
        self.Bind(wx.EVT_BUTTON, self.ChoosePartFolder, bp)
        self.textPartFolder = wx.StaticText(self, 1, self.v.getPartFolder().getName(), (0, 150))

        txt = wx.StaticText(self, -1, "Поставщик:", (0, 180))
        bs = wx.Button(self, -1, "post", (200, 180))
        self.Bind(wx.EVT_BUTTON, self.ChoosePostav, bs)
        self.textPostav = wx.StaticText(self, -1, self.v.getPostav().getName(), (0, 210))

        bm = wx.Button(self, -1, "Загрузить", (200, 240))
        self.Bind(wx.EVT_BUTTON, self.Run, bm)

    def ChoosePostav(self, evt):
        #print("choose postav")
        PostList = self.v.getAllPostav()
        pDlg = PostListDlg(PostList)
        if pDlg.ShowModal() == wx.ID_OK:
            self.v.setPostav(pDlg.getResult())
            self.textPostav.SetLabel(self.v.getPostav().getName())
        pDlg.Destroy()
        

    def ChoosePartFolder(self, evt):
        FoldersTree = self.v.getAllPartFolders()
        ptDlg = PartTreeDlg(FoldersTree)
        if ptDlg.ShowModal() == wx.ID_OK:
            self.v.setPartFolder(ptDlg.getResult())
            self.textPartFolder.SetLabel(self.v.getPartFolder().getName())
        ptDlg.Destroy()
 
    def ChooseCSV(self, evt):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard="Comma separated value file (*.csv)|*.csv",
            style=wx.OPEN
            )

        if dlg.ShowModal() == wx.ID_OK:
            self.v.setPathCSV(dlg.GetPaths()[0])
            self.csvFilePath.SetLabel(self.v.getPathCSV())
        dlg.Destroy()

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
        self.SetTopWindow(view)
        return True

# TODO delete codedupe
class PartFolder():
    def __init__(self):
        self.ID = 0
        self.Name = u"<Не выбрана>"
    def getID(self):
        return self.ID
    def getName(self):
        return self.Name
    def setFolder(self, raw):
        self.ID = raw[0]
        self.Name = raw[1]
class Postav():
    def __init__(self):
        self.ID = 0
        self.Name = u"<Не выбран>"
    def getID(self):
        return self.ID
    def getName(self):
        return self.Name
    def setPostav(self, raw):
        self.ID = raw[0]
        self.Name = raw[1]

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
        cur.execute("select id,name,parent,treelevel,codegroup from parttree order by treelevel, parent, codegroup")
        result = cur.fetchall()
        return result
    def getAllPostav(self):
        cur = self.__db.cursor()
        cur.execute("select id, nameshort from contragent")
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
            "IDPARTTREE": self.getPartFolder().getID(), #51, # TODO - create special folder
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
    app.RedirectStdio('err.log')
    print("==Last start begins here==")
    app.MainLoop()


if __name__ == '__main__':
    main()
