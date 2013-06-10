#!/usr/bin/python
# -*- coding: windows-1251 -*-

import wx
import wx.lib.filebrowsebutton as filebrowse

import fdb, os, os.path, codecs
import model

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

class ChooseFieldCtrl():
    def __init__(self, parent, textText, ctrlValue, btnCallBack, btnText = "..."):
        self.parent = parent

        self.StaticTxt = wx.StaticText(self.parent, -1, textText)
        self.Button = wx.Button(self.parent, -1, btnText)
        parent.Bind(wx.EVT_BUTTON, btnCallBack, self.Button)
        self.txtCtrl = wx.TextCtrl(self.parent, 1, ctrlValue, style = wx.TE_READONLY)

    def doLayout(self, vSizer):
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.Add(self.StaticTxt, 0, wx.ALL|wx.ALIGN_CENTER, 3)
        hSizer.Add(self.txtCtrl, 1, wx.ALL|wx.ALIGN_CENTER, 2)
        hSizer.Add(self.Button, 0, wx.ALL|wx.ALIGN_CENTER, 3)
        vSizer.Add(hSizer, 0, wx.EXPAND)

    def SetLabel(self, label):
        self.txtCtrl.SetLabel(label)


class MainFrame(wx.Frame):
    def __init__(self, v):
        self.v = v
        wx.Frame.__init__(self, None, -1, "Загрузка приходов", (10, 10))

        self.DocTypeList = ["Приход", "Расход"]
        self.SelDocType = self.DocTypeList[0]

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.panel = wx.Panel(self, -1)

        self.txt_Header = wx.StaticText(self.panel, -1, "Загрузка документов в АвтоСервис", style = wx.ALIGN_CENTER)
        self.txt_Header.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

        self.ChooseDocType = wx.RadioBox(self.panel, -1, "Тип документа", choices = self.DocTypeList)

        self.cvsFBB = filebrowse.FileBrowseButton(self.panel, -1, changeCallback = self.setPathCSV,
                                                  labelText = 'Файл с данными:', buttonText = '...', fileMask = '*.csv')

        self.txt_DBPath = wx.StaticText(self.panel, -1, "Путь к базе данных: "+self.v.getPathDB())

        self.FolderCtrl = ChooseFieldCtrl(self.panel, "Папка в каталоге товаров:", self.v.getPartFolder().getName(), self.ChoosePartFolder)
        self.SupplCtrl = ChooseFieldCtrl(self.panel, "Поставщик:", self.v.getPostav().getName(), self.ChoosePostav)

        self.btn_Run = wx.Button(self.panel, -1, "Загрузить")
        self.Bind(wx.EVT_BUTTON, self.Run, self.btn_Run)

        #self.StoreCtrl = ChooseFieldCtrl(self.panel, "Склад:", self.v.getStore().getName(), self.ChooseStore)

    def __layout_ctrl(self, ctrl, sizer, expand = 1):
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add(ctrl, expand, wx.ALL, 5)
        sizer.Add(h_sizer, 0, wx.EXPAND)

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.SetMinSize((500, 5))

        #title = wx.BoxSizer(wx.HORIZONTAL)
        #title.Add(self.txt_Header, 1, wx.ALL, 5)
        #sizer.Add(title, 0, wx.EXPAND)
        self.__layout_ctrl(self.txt_Header, sizer)

        #rb = wx.BoxSizer(wx.HORIZONTAL)
        #rb.Add(self.ChooseDocType, 0, wx.ALL, 5)
        #sizer.Add(rb, 0, wx.EXPAND)
        self.__layout_ctrl(self.ChooseDocType, sizer, 0)

        csv = wx.BoxSizer(wx.HORIZONTAL)
        csv.Add(self.cvsFBB, 1)
        sizer.Add(csv, 0, wx.EXPAND)

        self.FolderCtrl.doLayout(sizer)
        self.SupplCtrl.doLayout(sizer)

        #self.StoreCtrl.doLayout(sizer)

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

    # !!! TODO устранить дублирование в методах выбора значения из дерева !!!
    def ChoosePostav(self, evt):
        PostList = self.v.getAllPostav()
        pDlg = ChooseFromTreeDlg(PostList, "Выберите поставщика")
        if pDlg.ShowModal() == wx.ID_OK:
            self.v.setPostav(pDlg.getResult())
            self.SupplCtrl.SetLabel(self.v.getPostav().getName())
        pDlg.Destroy()
        
    def ChoosePartFolder(self, evt):
        FoldersTree = self.v.getAllPartFolders()
        ptDlg = ChooseFromTreeDlg(FoldersTree, "Выберите папку")
        if ptDlg.ShowModal() == wx.ID_OK:
            self.v.setPartFolder(ptDlg.getResult())
            self.FolderCtrl.SetLabel(self.v.getPartFolder().getName())
        ptDlg.Destroy()

    def ChooseStore(self, evt):
        StoreTree = self.v.getAllStores()
        stDlg = ChooseFromTreeDlg(StoreTree, "Выберите склад")
        if stDlg.ShowModal() == wx.ID_OK:
            self.v.setStore(stDlg.getResult())
            self.ctrl_Store.SetLabel(self.v.getStore().getName())
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
        myModel = model.appData()
        view = MainFrame(myModel)
        view.Show(True)
        self.SetTopWindow(view)
        return True

def main():
    app = myApp()
    #app.RedirectStdio('err.log')
    print("==Last start begins here==")
    app.MainLoop()


if __name__ == '__main__':
    main()
