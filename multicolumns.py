#	custom listbox class with multiple columns
#
#

from tkinter import *
from tkinter.ttk import *
from tkinter.font import Font
import pandas as pd


class MultiTwo(Frame, Treeview):
    SortDir = True     # descending

    def __init__(self, parent=None, index_list=[], dataframe=pd.DataFrame()):
        Frame.__init__(self, parent)
        self.parent = parent
        self.dataframe = dataframe
        self.index_list = index_list
        self.grid(sticky=N + S)
        self.dataCols = ('ID', 'Name', 'Tags', 'Type', 'Device', 'Group', 'Probe')
        self.tree = Treeview(parent, columns=self.dataCols, show='headings')
        self.ysb = Scrollbar(parent, orient=VERTICAL, command=self.tree.yview)
        self.xsb = Scrollbar(parent, orient=HORIZONTAL, command=self.tree.xview)
        self.tree['yscroll'] = self.ysb.set
        self.tree['xscroll'] = self.xsb.set
        self.tree.grid(in_=parent, row=0, column=0, sticky=NSEW)
        self.ysb.grid(in_=parent, row=0, column=1, sticky=NS)
        self.xsb.grid(in_=parent, row=1, column=0, sticky=EW)
        self.data = []

        for x in self.index_list:
            self.data.append((self.dataframe['ID'][x], self.dataframe['Object'][x], self.dataframe['Tags'][x], self.dataframe['Type'][x], self.dataframe['Device'][x], self.dataframe['Group'][x], self.dataframe['Probe'][x]))

        for c in self.dataCols:
            self.tree.heading(c, text=c.title(), command=lambda c=c: self._column_sort(c, MultiTwo.SortDir))
            self.tree.column(c, width=Font().measure(c.title()))

        for item in self.data:
            self.tree.insert('', 'end', values=item)
            #   set column width
            #   tree.column("column", minwidth=x, width=X, stretch=NO)
            #   Columns:
            #   'ID', 'Name', 'Tags', 'Type', 'Device', 'Group', 'Probe'
            for idx, val in enumerate(item):
                iwidth = Font().measure(val)
                if self.tree.column(self.dataCols[idx], 'width') < iwidth:
                    self.tree.column(self.dataCols[idx], width=iwidth)

    def _column_sort(self, col, descending=False):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            self.tree.move(item[1], '', indx)

        MultiTwo.SortDir = not descending

    def update(self, idxl, df):
        return MultiTwo(self.parent, idxl, df)

    def clear(self):
        self.tree.delete(*self.tree.get_children())

    def getsel(self, *args):
        return self.tree.selection()

    def getsel2(self, *args):
        return self.tree.get_children()