#!/usr/bin/python
# -*- coding: windows-1251 -*-

import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.grid as gridlib

import fdb, os, os.path, codecs

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Выбор колонок в файле", (10, 10))
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.panel = wx.Panel(self, -1)

        self.cvsFBB = filebrowse.FileBrowseButton(self.panel, -1, labelText = 'Файл с данными:',
                                                  buttonText = '...', fileMask = '*.csv')

        self.GoBtn = wx.Button(self.panel, -1, "Go")
        self.Bind(wx.EVT_BUTTON, self.Run, self.GoBtn)

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.SetMinSize((500, 5))

        csv = wx.BoxSizer(wx.HORIZONTAL)
        csv.Add(self.cvsFBB, 1)
        sizer.Add(csv, 0, wx.EXPAND)

        btn = wx.BoxSizer(wx.HORIZONTAL)
        btn.Add(wx.StaticText(self.panel, -1, ""), 1) # грубый хак, чтобы кнопка была выровнена по правому краю
        btn.Add(self.GoBtn, 0, wx.ALL, 3)
        sizer.Add(btn, 0, wx.EXPAND)


        self.panel.SetSizer(sizer)
        self.Layout()
        sizer.Fit(self)

    def Run(self, evt):
        grDlg = GridDialog(self.cvsFBB.GetValue())
        grDlg.Show()
        #grDlg.ShowModal()
        #grDlg.Destroy()

        """
        f = open(self.cvsFBB.GetValue(), 'r')
        lines = f.readlines()
        f.close()

        print(self.cvsFBB.GetValue())
        """

class GridDialog(wx.Frame):
    def __init__(self, fName):
        wx.Frame.__init__(self, None)
        #self.fName = fName

        p = wx.Panel(self, -1)
        grid = FileGrid(p, fName)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(grid, 1, wx.GROW|wx.ALL, 5)

        p.SetSizer(s)

class FileGrid(gridlib.Grid):
    def __init__(self, parent, fName):
        gridlib.Grid.__init__(self, parent)
        #self.fName = fName

        table = FileGridTable(fName)

        self.SetTable(table, True)

        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.AutoSizeColumns(False)

class FileGridTable(gridlib.PyGridTableBase):
    def __init__(self, fName):
        gridlib.PyGridTableBase.__init__(self)
        self.fName = fName

        f = open(fName, 'r')
        lines = f.readlines()
        f.close()

        self.colLabels = self.Split(lines[0])
        self.data = map(self.Split, lines[1:])

    def Split(self, String):
        return String.split(";")

    #--------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data) + 1

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        def innerSetValue(row, col, value):
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                innerSetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,            # The table
                        gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                        1                                       # how many
                        )

                self.GetView().ProcessTableMessage(msg)
        innerSetValue(row, col, value) 

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]


class myApp(wx.App):
    def OnInit(self):
        view = MainFrame()
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
