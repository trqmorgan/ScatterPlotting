# -*- coding: utf-8 -*-
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
import os
import PCA as pca
import data_cleanser as dc
import wx
import wx.lib.agw.advancedsplash as AS
import wx.grid as gridlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import tkinter
from tkinter import filedialog
import numpy as np
from tkinter import messagebox
import appdirs
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements
import pandas as pd
import seaborn as sns

###########################################################################
#                                  GUI                                    #
###########################################################################

class RedirectText(object):
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl
    def write(self, string):
        self.out.WriteText(string)


class MainFrame(wx.Frame):

    def __init__(self):
        """
        :return: the GUI
        """
        wx.Frame.__init__(self, None, title='Chemostrat: Sample Classifier', size=(1500, 950))

        panel = wx.Panel(self, style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        panel.SetBackgroundColour("white")

        self.Bind(wx.EVT_CLOSE, self.on_exit)

        self.sp_home = wx.SplitterWindow(panel)
        self.content = wx.Panel(self.sp_home, style=wx.SUNKEN_BORDER)
        self.console_bar = wx.Panel(self.sp_home, style=wx.SUNKEN_BORDER)
        self.content.SetBackgroundColour("White")
        self.console_bar.SetBackgroundColour("White")
        self.sp_home.SplitHorizontally(self.content, self.console_bar, 845)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.sp_home, 1, wx.EXPAND)
        panel.SetSizerAndFit(sizer1)

        notebook = wx.Notebook(self.content)
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        self.content.SetSizer(content_sizer)

        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL
        self.log = wx.TextCtrl(self.console_bar, wx.ID_ANY, pos=(0, 0), size=(1480, 50), style=style)
        print ("Welcome to Chemostrat: Sample Classifier. Please Load a database to begin analysis.")
        log_sizer = wx.BoxSizer()
        log_sizer.Add(self.log, 1, wx.EXPAND)
        self.console_bar.SetSizerAndFit(log_sizer)

        # --------------------------------------------------------------------------------------------------------------

        tab_one = TabPanel(notebook)
        tab_one.SetBackgroundColour("White")
        notebook.AddPage(tab_one, "Data Import")
        self.sp1 = wx.SplitterWindow(tab_one)
        self.selections1 = wx.Panel(self.sp1, style=wx.SUNKEN_BORDER)
        self.graphing1 = wx.Panel(self.sp1, style=wx.SUNKEN_BORDER)
        self.selections1.SetBackgroundColour("White")
        self.graphing1.SetBackgroundColour("White")
        self.sp1.SplitVertically(self.selections1, self.graphing1, 250)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.sp1, 1, wx.EXPAND)
        tab_one.SetSizerAndFit(sizer1)

        load_button = wx.Button(self.selections1, label='Load Data', pos=(10, 10), size=(225, 60))
        load_button.Bind(wx.EVT_BUTTON, self.on_open)

        wx.StaticText(self.selections1, label="Filter 1:", pos=(12, 85))
        wx.StaticText(self.selections1, label="Select Choices:", pos=(12, 140))
        self.filter_combo1 = wx.ComboBox(self.selections1, -1, choices=['No Data Loaded'], pos=(12, 110), size=(220, 20))
        self.filter_check1 = wx.CheckListBox(self.selections1, -1, pos=(12, 160), size=(220, 120))
        self.filter_combo1.Bind(wx.EVT_COMBOBOX, self.on_combo1)

        wx.StaticText(self.selections1, label="Filter 2:", pos=(12, 295))
        wx.StaticText(self.selections1, label="Select Choices:", pos=(12, 350))
        self.filter_combo2 = wx.ComboBox(self.selections1, -1, choices=['No Data Loaded'], pos=(12, 320), size=(220, 20))
        self.filter_check2 = wx.CheckListBox(self.selections1, -1, pos=(12, 370), size=(220, 120))
        self.filter_combo2.Bind(wx.EVT_COMBOBOX, self.on_combo2)

        wx.StaticText(self.selections1, label="Filter 3:", pos=(12, 505))
        wx.StaticText(self.selections1, label="Select Choices:", pos=(12, 560))
        self.filter_combo3 = wx.ComboBox(self.selections1, -1, choices=['No Data Loaded'], pos=(12, 530), size=(220, 20))
        self.filter_check3 = wx.CheckListBox(self.selections1, -1, pos=(12, 580), size=(220, 120))
        self.filter_combo3.Bind(wx.EVT_COMBOBOX, self.on_combo3)

        self.combo_boxes = [self.filter_combo1, self.filter_combo2, self.filter_combo3]
        self.check_boxes = [self.filter_check1, self.filter_check2, self.filter_check3]
        self.data_been_filtered = False

        filter_button = wx.Button(self.selections1, label='Filter Data', pos=(10, 715), size=(225, 70))
        filter_button.Bind(wx.EVT_BUTTON, self.on_filter)

        self.grid = gridlib.Grid(self.graphing1)
        self.grid.CreateGrid(0, 0)
        grid_sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer.Add(self.grid, 1, wx.EXPAND)
        self.graphing1.SetSizerAndFit(grid_sizer)

        # --------------------------------------------------------------------------------------------------------------

        tab_two = TabPanel(notebook)
        tab_two.SetBackgroundColour("White")
        notebook.AddPage(tab_two, "Principal Component Analysis")
        self.sp2 = wx.SplitterWindow(tab_two)
        self.selections2 = wx.Panel(self.sp2, style=wx.SUNKEN_BORDER)
        self.graphing2 = wx.Panel(self.sp2, style=wx.SUNKEN_BORDER)
        self.selections2.SetBackgroundColour("White")
        self.graphing2.SetBackgroundColour("White")
        self.sp2.SplitVertically(self.selections2, self.graphing2, 250)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(self.sp2, 1, wx.EXPAND)
        tab_two.SetSizerAndFit(sizer2)

        wx.StaticText(self.selections2, label="Select Data Labels:", pos=(70, 10))
        wx.StaticText(self.selections2, label="Colour:", pos=(10, 37))
        wx.StaticText(self.selections2, label="Shape", pos=(10, 62))
        wx.StaticText(self.selections2, label="x:", pos=(10, 87))
        wx.StaticText(self.selections2, label="y:", pos=(10, 110))

        self.color_on_pca = wx.ComboBox(self.selections2, choices=['No '
                                                                     'Data Loaded'], pos=(80, 35), size=(152, 20))
        self.shape_on_pca = wx.ComboBox(self.selections2, choices=['No '
                                                                      'Data Loaded'], pos=(80, 60), size=(152, 20))
        self.color_on_pca.Bind(wx.EVT_TEXT, lambda event: self.pop_shape_frm_plots(event, 'pca_color'))
        self.shape_on_pca.Bind(wx.EVT_TEXT, lambda event:self.pop_shape_frm_plots(event, 'pca_shape'))
        self.x_axis_selection = wx.ComboBox(self.selections2, choices=[
            'PC1', 'PC2', 'PC3'], value='PC1', pos=(80, 85), size=(152, 20))
        self.y_axis_selection = wx.ComboBox(self.selections2, choices=[
            'PC1', 'PC2', 'PC3'], value='PC2', pos=(80, 110), size=(152, 20))

        self.confirm_btn_PCA = wx.Button(self.selections2, label="Generate "
                                                               "Graph", pos=(10, 642), size=(225, 65))
        self.confirm_btn_PCA.Bind(wx.EVT_BUTTON, self.confirm_PCA)
        self.CLR_check = wx.CheckBox(self.selections2, label="Center "
                                                                    "Log "
                                                                    "Ratio?",
                                            pos=(10, 135))
        self.CLR_check.SetValue(True)
        self.PCA_button = wx.Button(self.selections2, label='Generate PDF',
                                     pos=(10, 720), size=(225, 65))
        self.PCA_button.Bind(wx.EVT_BUTTON, self.on_PCA)
        self.PCA_button.Enable(False)

        self.PCA_selection = wx.CheckListBox(self.selections2, -1, pos=(12,
                                                                        175),
                                             size=(220, 270))
        self.PCA_selection.Bind(wx.EVT_COMBOBOX, self.on_combo3)
        wx.StaticText(self.selections2, label="Size:", pos=(10, 480))
        self.size_slider_PCA = wx.Slider(self.selections2, 1, 25, 0, 100,
                                          pos=(10, 500),
                    size=(200, -1),
                    style=wx.SL_HORIZONTAL|wx.SL_VALUE_LABEL)
        self.arrows_check = wx.CheckBox(self.selections2, label="Plot arrows?",
                                     pos=(10, 530))
        self.arrows_check.SetValue(True)
        self.samples_check = wx.CheckBox(self.selections2, label="Plot samples?",
                                     pos=(10, 560))
        self.samples_check.SetValue(True)

        wx.StaticText(self.selections2, label="Label Points", pos=(10, 592))
        self.label_points_pca = wx.ComboBox(self.selections2, choices=['No '
                                                                   'Data Loaded'], pos=(80, 590), size=(152, 20))

        # --------------------------------------------------------------------------------------------------------------

        tab_three = TabPanel(notebook)
        tab_three.SetBackgroundColour("White")
        notebook.AddPage(tab_three, "Scatter")
        self.sp3 = wx.SplitterWindow(tab_three)
        self.selections3 = wx.Panel(self.sp3, style=wx.SUNKEN_BORDER)
        self.graphing3 = wx.Panel(self.sp3, style=wx.SUNKEN_BORDER)
        self.selections3.SetBackgroundColour("White")
        self.graphing3.SetBackgroundColour("White")
        self.sp3.SplitVertically(self.selections3, self.graphing3, 250)
        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(self.sp3, 1, wx.EXPAND)
        tab_three.SetSizerAndFit(sizer3)

        wx.StaticText(self.selections3, label="Select Data Labels:", pos=(70, 10))
        wx.StaticText(self.selections3, label="Colour:", pos=(10, 37))
        wx.StaticText(self.selections3, label="Shape:", pos=(10, 62))
        wx.StaticText(self.selections3, label="x:", pos=(10, 87))
        wx.StaticText(self.selections3, label="y:", pos=(10, 112))
        wx.StaticText(self.selections3, label="z:", pos=(10, 137))
        self.color_on_scatter = wx.ComboBox(self.selections3, choices=['No Data Loaded'], pos=(80, 35), size=(152, 20))
        self.shape_on_scatter = wx.ComboBox(self.selections3, choices=['No Data Loaded'], pos=(80, 60), size=(152, 20))
        self.color_on_scatter.Bind(wx.EVT_TEXT, lambda event: self.pop_shape_frm_plots(event, 'scatter_color'))
        self.shape_on_scatter.Bind(wx.EVT_TEXT, lambda event: self.pop_shape_frm_plots(event, 'scatter_shape'))


        self.x_name_scatter = wx.ComboBox(self.selections3, choices=['No '
                                                                       'Data Loaded'], pos=(80, 85), size=(65, 20))
        self.y_name_scatter = wx.ComboBox(self.selections3, choices=['No '
                                                                       'Data Loaded'], pos=(80, 110), size=(65, 20))
        self.z_name_scatter = wx.ComboBox(self.selections3, choices=['No '
                                                                       'Data Loaded'], pos=(80, 135), size=(65, 20))

        self.x1_name_scatter = wx.ComboBox(self.selections3, choices=['No '
                                                                       'Data Loaded'], pos=(160, 85), size=(65, 20))
        self.y1_name_scatter = wx.ComboBox(self.selections3, choices=['No '
                                                                       'Data Loaded'], pos=(160, 110), size=(65, 20))
        self.z1_name_scatter = wx.ComboBox(self.selections3, choices=['No '
                                                                       'Data Loaded'], pos=(160, 135), size=(65, 20))

        self.x_name_scatter.Bind(wx.EVT_TEXT, self.confirm_scatter)
        self.y_name_scatter.Bind(wx.EVT_TEXT, self.confirm_scatter)
        self.z_name_scatter.Bind(wx.EVT_TEXT, self.confirm_scatter)
        self.x1_name_scatter.Bind(wx.EVT_TEXT, self.confirm_scatter)
        self.y1_name_scatter.Bind(wx.EVT_TEXT, self.confirm_scatter)
        self.z1_name_scatter.Bind(wx.EVT_TEXT, self.confirm_scatter)


        wx.StaticText(self.selections3, label="Size:", pos=(10, 160))
        self.size_slider_scatter = wx.Slider(self.selections3, 1, 25, 0, 100,
                                          pos=(10, 180),
                    size=(200, -1),
                    style=wx.SL_HORIZONTAL|wx.SL_VALUE_LABEL)


        wx.StaticText(self.selections3, label="x limit", pos=(10,264))
        wx.StaticText(self.selections3, label="y limit", pos=(10,287))
        wx.StaticText(self.selections3, label="upper", pos=(109,240))
        wx.StaticText(self.selections3, label="lower", pos=(54,240))

        self.xLowLim = wx.TextCtrl(self.selections3, pos=(50, 260), size=(50,20))
        self.xUpLim = wx.TextCtrl(self.selections3, pos=(105, 260), size=(50,20))
        self.yLowLim = wx.TextCtrl(self.selections3, pos=(50, 285), size=(50,20))
        self.yUpLim = wx.TextCtrl(self.selections3, pos=(105, 285), size=(50,20))


        self.scatter_log_x = wx.CheckBox(self.selections3, label="log x",
                                            pos=(10, 320))
        self.scatter_log_x.SetValue(False)

        self.scatter_log_y = wx.CheckBox(self.selections3, label="log y",
                                            pos=(10, 350))
        self.scatter_log_y.SetValue(False)

        wx.StaticText(self.selections3, label="Label Points", pos=(10, 592))
        self.label_points_scatter = wx.ComboBox(self.selections3, choices=['No '
                                                                       'Data Loaded'], pos=(80, 590), size=(152, 20))



        self.confirm_btn_scatter = wx.Button(self.selections3,
                                             label="Generate "
                                                               "Graph", pos=(10, 642), size=(225, 65))
        self.confirm_btn_scatter.Bind(wx.EVT_BUTTON, self.confirm_scatter)
        self.scatter_button = wx.Button(self.selections3, label='Generate PDF', pos=(10, 720), size=(225, 65))
        self.scatter_button.Bind(wx.EVT_BUTTON, self.on_scatter)
        self.scatter_button.Enable(False)

        # --------------------------------------------------------------------------------------------------------------

        tab_five = TabPanel(notebook)
        tab_five.SetBackgroundColour("White")
        notebook.AddPage(tab_five, "Ternary")
        self.sp5 = wx.SplitterWindow(tab_five)
        self.selections5 = wx.Panel(self.sp5, style=wx.SUNKEN_BORDER)
        self.graphing5 = wx.Panel(self.sp5, style=wx.SUNKEN_BORDER)
        self.selections5.SetBackgroundColour("White")
        self.graphing5.SetBackgroundColour("White")
        self.sp5.SplitVertically(self.selections5, self.graphing5, 250)
        sizer5 = wx.BoxSizer(wx.VERTICAL)
        sizer5.Add(self.sp5, 1, wx.EXPAND)
        tab_five.SetSizerAndFit(sizer5)

        wx.StaticText(self.selections5, label="Select Data Labels:", pos=(70,
                                                                         10))
        wx.StaticText(self.selections5, label="Colour:", pos=(10, 37))
        wx.StaticText(self.selections5, label="Shape:", pos=(10, 62))
        wx.StaticText(self.selections5, label="top:", pos=(10, 87))
        wx.StaticText(self.selections5, label="left:", pos=(10, 112))
        wx.StaticText(self.selections5, label="right", pos=(10, 137))
        self.color_on_tern = wx.ComboBox(self.selections5, choices=['No Data Loaded'], pos=(80, 35), size=(152, 20))
        self.shape_on_tern = wx.ComboBox(self.selections5, choices=['No Data Loaded'], pos=(80, 60), size=(152, 20))
        self.color_on_tern.Bind(wx.EVT_TEXT, lambda event: self.pop_shape_frm_plots(event, 'tern_color'))
        self.shape_on_tern.Bind(wx.EVT_TEXT, lambda event: self.pop_shape_frm_plots(event, 'tern_shape'))


        self.x_name_tern = wx.ComboBox(self.selections5, choices=['No '
                                                                       'Data Loaded'], pos=(80, 85), size=(65, 20))
        self.y_name_tern = wx.ComboBox(self.selections5, choices=['No '
                                                                       'Data Loaded'], pos=(80, 110), size=(65, 20))
        self.z_name_tern = wx.ComboBox(self.selections5, choices=['No '
                                                                       'Data Loaded'], pos=(80, 135), size=(65, 20))

        self.x1_name_tern = wx.ComboBox(self.selections5, choices=['No '
                                                                       'Data Loaded'], pos=(160, 85), size=(65, 20))
        self.y1_name_tern = wx.ComboBox(self.selections5, choices=['No '
                                                                       'Data Loaded'], pos=(160, 110), size=(65, 20))
        self.z1_name_tern = wx.ComboBox(self.selections5, choices=['No '
                                                                       'Data Loaded'], pos=(160, 135), size=(65, 20))

        wx.StaticText(self.selections5, label="size:", pos=(10, 162))

        self.size_name_tern = wx.ComboBox(self.selections5, choices=['No '
                                                                       'Data Loaded'], pos=(80, 160), size=(65, 20))

        self.size_name_tern.Bind(wx.EVT_TEXT, self.confirm_scatter)
        self.x_name_tern.Bind(wx.EVT_TEXT, self.confirm_tern)
        self.y_name_tern.Bind(wx.EVT_TEXT, self.confirm_tern)
        self.z_name_tern.Bind(wx.EVT_TEXT, self.confirm_tern)
        self.x1_name_tern.Bind(wx.EVT_TEXT, self.confirm_tern)
        self.y1_name_tern.Bind(wx.EVT_TEXT, self.confirm_tern)
        self.z1_name_tern.Bind(wx.EVT_TEXT, self.confirm_tern)

        wx.StaticText(self.selections5, label="multiply left", pos=(10,297))
        wx.StaticText(self.selections5, label="multiply right", pos=(10,320))
        wx.StaticText(self.selections5, label="multiply top", pos=(10,274))
        self.multiply_left = wx.TextCtrl(self.selections5, pos=(100, 295),
                                         size=(50, 20))
        self.multiply_right = wx.TextCtrl(self.selections5, pos=(100, 320),
                                          size=(50, 20))
        self.multiply_top = wx.TextCtrl(self.selections5, pos=(100, 270),
                                        size=(50, 20))

        wx.StaticText(self.selections5, label="Size:", pos=(10, 190))
        self.size_slider_tern = wx.Slider(self.selections5, 1, 25, 0, 100,
                                          pos=(10, 210),
                    size=(200, -1),
                    style=wx.SL_HORIZONTAL|wx.SL_VALUE_LABEL)


        self.confirm_btn_tern = wx.Button(self.selections5,
                                             label="Generate "
                                                               "Graph", pos=(10, 642), size=(225, 65))
        self.confirm_btn_tern.Bind(wx.EVT_BUTTON, self.confirm_tern)
        self.tern_button = wx.Button(self.selections5, label='Generate '
                                                                'PDF', pos=(10, 720), size=(225, 65))
        self.tern_button.Bind(wx.EVT_BUTTON, self.on_tern)
        self.tern_button.Enable(False)
        #------------------------------------- Tab 6 -------------------
        tab_six = TabPanel(notebook)
        tab_six.SetBackgroundColour("White")
        notebook.AddPage(tab_six, "Colors && Shapes")
        self.sp6 = wx.SplitterWindow(tab_six)
        self.selections6 = wx.Panel(self.sp6, style=wx.SUNKEN_BORDER)
        self.graphing6 = wx.Panel(self.sp6, style=wx.SUNKEN_BORDER)
        self.selections6.SetBackgroundColour("White")
        self.graphing6.SetBackgroundColour("White")
        self.sp6.SplitVertically(self.selections6, self.graphing6, 250)
        sizer6 = wx.BoxSizer(wx.VERTICAL)
        sizer6.Add(self.sp6, 1, wx.EXPAND)
        tab_six.SetSizerAndFit(sizer6)
        wx.StaticText(self.selections6, label="Select column", pos=(10, 12))


        self.colorcombo = wx.ComboBox(self.selections6, -1, pos=(110, 10),
                                          size=(110, 20),
                                          style=wx.TE_PROCESS_ENTER)
        self.colorcombo.Bind(wx.EVT_TEXT, self.pop_colorbox)


        self.list_ctrl = wx.ListCtrl(self.selections6, size=(200, 200),  pos=(10,40), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, 'Item')
        self.list_ctrl.InsertColumn(1, 'Shape')
        wx.StaticText(self.selections6, label="Select color", pos=(10, 253))
        self.pallet = wx.ColourPickerCtrl(self.selections6, colour='blue', pos=(140, 250), size=(100, 25))
        self.pallet.Bind(wx.EVT_COLOURPICKER_CHANGED, self.select_color)

        wx.StaticText(self.selections6, label="Select shape", pos=(10, 287))
        self.shapecombo = wx.ComboBox(self.selections6, -1, pos=(140, 285),
                                      size=(100, 25), value='Circle', choices=['Circle', 'Triangle', 'Octagon', 'Square',
                                                                               'Pentagon', 'Plus', 'Star', 'Diamond'],
                                      style=wx.TE_PROCESS_ENTER)
        self.shapecombo.Bind(wx.EVT_TEXT, self.select_shape)

        #--------------------------------------------------------------------------------------------------------
        self.fig_PCA = plt.figure(figsize=(12, 8))
        self.fig_scatter = plt.figure(figsize=(12, 8))
        self.fig_tern = plt.figure(figsize=(12, 8))

        self.canvas2 = FigCanvas(self.graphing2, -1, self.fig_PCA)
        self.canvas3 = FigCanvas(self.graphing3, -1, self.fig_scatter)
        self.canvas5 = FigCanvas(self.graphing5, -1, self.fig_tern)
        # initialse dictionarys to hold colours and shapes
        self.colordict = {'All': 'b'}
        self.shapedict = {'All': ('Circle', 'o')}
        self.mplshapedict = {'Circle': 'o', 'Triangle': '^', 'Octagon': '8', 'Square': 's', 'Pentagon': 'p', 'Plus': 'P',
                             'Star': '*', 'Diamond': 'D'}

        # --------------------------------------------------------------------------------------------------------------


    def on_combo1(self, event):
        try:
            selections1 = self.data[str(self.filter_combo1.GetValue())].unique()
            selections1 = sorted(selections1.tolist())
            self.filter_check1.Clear()
            for item in range(len(selections1)):
                self.filter_check1.AppendItems(selections1[item])
                self.filter_check1.Check(item, True)
        except AttributeError:
            print("INFO: No Data has been imported")
        except TypeError:
            print("INFO: Cannot set this column as a filter")

    def on_combo2(self, event):
        try:
            selections2 = self.data[str(self.filter_combo2.GetValue())].unique()
            selections2 = sorted(selections2.tolist())
            self.filter_check2.Clear()
            for item in range(len(selections2)):
                self.filter_check2.AppendItems(selections2[item])
                self.filter_check2.Check(item, True)
        except AttributeError:
            print("INFO: No Data has been imported")
        except TypeError:
            print("INFO: Cannot set this column as a filter")

    def on_combo3(self, event):
        try:
            selections3 = self.data[str(self.filter_combo3.GetValue())].unique()
            selections3 = sorted(selections3.tolist())
            self.filter_check3.Clear()
            for item in range(len(selections3)):
                self.filter_check3.AppendItems(selections3[item])
                self.filter_check3.Check(item, True)
        except AttributeError:
            print("INFO: No Data has been imported")
        except TypeError:
            print("INFO: Cannot set this column as a filter")

    def on_filter(self, event):
        self.data_been_filtered = True
        self.dataFiltered = self.data
        for b in range(len((self.combo_boxes))):
            for h, box in enumerate(self.check_boxes):
                if len(box.GetCheckedItems()) != 0:
                    self.dataFiltered = self.dataFiltered[self.dataFiltered[self.combo_boxes[h].GetValue()].isin(box.GetCheckedStrings())]
                    self.dataFiltered = self.dataFiltered.reset_index(drop=True)
                    self.update_grid(self.dataFiltered, self.column_headers)
                    self.dataFiltered = self.dataFiltered.convert_objects()
                    self.column_headers = list(self.dataFiltered.columns.values)
                    is_number = np.vectorize(lambda x: np.issubdtype(x, np.number))
                    is_number = is_number(self.dataFiltered.dtypes)
                    self.non_numeric_cols = [d for (d, remove) in zip(self.column_headers,
                                                                   is_number)
                                          if not remove]
                    self.numeric_cols = [d for (d, remove) in zip(self.column_headers,
                                                                   is_number)
                                      if remove]

                    self.update_combos(False)


    def save_graph(self, filepath, headers, object, type):
        try:
            object.savefig(filepath+"/"+type+"_"+headers[0]+".pdf",
                        bbox_inches='tight')
            print("INFO: " + type + " Export Complete")
        except:
            print("Error encountered when saving plot.")
    def pop_colorbox(self, event):

        if self.data_been_filtered:
            items = pd.unique(self.dataFiltered[self.colorcombo.GetValue()])
        else:
            items = pd.unique(self.data[self.colorcombo.GetValue()])

        shapes = ["Circle"]*len(items)
        shape_code_list = []
        for s in shapes:
            code = self.mplshapedict.get(s)
            shape_code_list.append(code)

        for item in items:
            if item not in self.shapedict:
                shape_tup = list(zip(shapes, shape_code_list))
                self.shapedict.update(dict(zip(items, shape_tup)))

        for item in items:
            if item not in self.colordict:
                colors = sns.color_palette("hls", len(items))
                self.colordict.update(dict(zip(items, colors)))

        self.list_ctrl.DeleteAllItems()


        for i, item in enumerate(items):
            self.list_ctrl.InsertItem(i, item)
            s = self.shapedict.get(item)
            self.list_ctrl.SetItem(i, 1,s[0])
            c = self.colordict.get(item)
            try:
                self.list_ctrl.SetItemBackgroundColour(i, tuple(255*x for x in c))
            except TypeError:
                pass
    def pop_shape_frm_plots(self, event, plottype):
        print(plottype)
        if plottype == 'pca_shape':
            if len(self.shape_on_pca.GetValue()) > 0:
                self.colorcombo.SetValue(self.shape_on_pca.GetValue())
        if plottype == 'scatter_shape':
            if len(self.shape_on_scatter.GetValue()) > 0:
                self.colorcombo.SetValue(self.shape_on_scatter.GetValue())
        if plottype == 'tern_shape':
            if len(self.shape_on_tern.GetValue()) > 0:
                self.colorcombo.SetValue(self.shape_on_tern.GetValue())

        if plottype == 'pca_color':
            if len(self.color_on_pca.GetValue()) > 0:
                self.colorcombo.SetValue(self.color_on_pca.GetValue())
        if plottype == 'scatter_color':
            if len(self.color_on_scatter.GetValue()) > 0:
                self.colorcombo.SetValue(self.color_on_scatter.GetValue())
        if plottype == 'tern_color':
            if len(self.color_on_tern.GetValue()) > 0:
                self.colorcombo.SetValue(self.color_on_tern.GetValue())


    def select_color(self, event):

        color = self.pallet.GetColour()
        self.list_ctrl.SetItemBackgroundColour(self.list_ctrl.GetFirstSelected(),color)
        item = self.list_ctrl.GetItemText(self.list_ctrl.GetFirstSelected(), 0)
        updated_color = dict(zip([item],[tuple(x/255 for x in color)]))
        self.colordict.update(updated_color)

    def select_shape(self, event):
        shape = self.shapecombo.GetValue()

        item = self.list_ctrl.GetItemText(self.list_ctrl.GetFirstSelected(), 0)
        self.list_ctrl.SetItem(self.list_ctrl.GetFirstSelected(), 1, shape)
        code = self.mplshapedict.get(shape)
        shape_tup = list(zip((shape,), code))
        updated_shape = dict(zip((item,), shape_tup))
        self.shapedict.update(updated_shape)

    def confirm_PCA(self, event):

        self.fig_PCA.clear()
        self.checkedPCAStrings = self.PCA_selection.GetCheckedStrings()
        self.pca_color = self.color_on_pca.GetValue()
        self.pca_shape = self.shape_on_pca.GetValue()


        self.key_headers_PCA = [self.x_axis_selection.GetValue(),
                                self.y_axis_selection.GetValue(),
                                self.checkedPCAStrings,
                                self.pca_color,
                                self.size_slider_PCA.GetValue(), self.pca_shape, self.label_points_pca.GetValue()]
        if self.data_been_filtered:
            self.fig_PCA = pca.pca_(self.dataFiltered,
                                            self.key_headers_PCA,
                                          self.fig_PCA, self.CLR_check.GetValue(), self.arrows_check.GetValue(),  self.samples_check.GetValue(), self.colordict, self.shapedict)
        else:

            self.fig_PCA = pca.pca_(self.data,
                                          self.key_headers_PCA, self.fig_PCA, self.CLR_check.GetValue(), self.arrows_check.GetValue(),  self.samples_check.GetValue(), self.colordict, self.shapedict)
        self.PCA_plot = self.fig_PCA
        self.canvas2.draw()
        self.confirm_btn_PCA.SetLabelText("Update Graph")
        self.PCA_button.Enable(True)

    def confirm_scatter(self, event):
        self.fig_scatter.clear()
        self.scatter_color = self.color_on_scatter.GetValue()
        self.scatter_shape = self.shape_on_scatter.GetValue()

        size = self.size_slider_scatter.GetValue()
        self.key_headers_scatter = [self.scatter_color,
                                    self.x_name_scatter.GetValue(),
                                    self.y_name_scatter.GetValue(),
                                    self.z_name_scatter.GetValue(),
                                    self.x1_name_scatter.GetValue(),
                                    self.y1_name_scatter.GetValue(),
                                    self.z1_name_scatter.GetValue(), size, self.scatter_shape, self.label_points_scatter.GetValue()]
        limits = [self.xLowLim.GetValue(), self.xUpLim.GetValue(),
                  self.yLowLim.GetValue(), self.yUpLim.GetValue()]
        log_scales = [self.scatter_log_x.GetValue(),
                      self.scatter_log_y.GetValue()]
        if self.data_been_filtered:
            if not len(self.x_name_scatter.GetValue()) == 0 and not len(
                    self.y_name_scatter.GetValue()) == 0:
                self.fig_scatter = pca.blank_scatter_plot(self.dataFiltered,
                                                          self.key_headers_scatter, limits, self.fig_scatter, log_scales, self.colordict, self.shapedict)
        else:
            if not len(self.x_name_scatter.GetValue()) == 0 and not len(
                    self.y_name_scatter.GetValue()) ==0:
                self.fig_scatter = pca.blank_scatter_plot(self.data,
                                                  self.key_headers_scatter,
                                                          limits,
                                                          self.fig_scatter, log_scales,  self.colordict, self.shapedict)
        self.scatter_plot = self.fig_scatter
        self.canvas3.draw()
        self.confirm_btn_scatter.SetLabelText("Update Graph")
        self.scatter_button.Enable(True)

    def confirm_tern(self, event):

        self.fig_tern.clear()
        self.tern_color = self.color_on_tern.GetValue()
        self.tern_shape = self.shape_on_tern.GetValue()

        x =self.x_name_tern.GetValue()
        y = self.y_name_tern.GetValue()
        z = self.z_name_tern.GetValue()
        x1 = self.x1_name_tern.GetValue()
        y1 = self.y1_name_tern.GetValue()
        z1 = self.z1_name_tern.GetValue()
        self.key_headers_tern = [self.tern_color, x, y, z, x1,
                                    y1, z1, self.size_name_tern.GetValue(), self.tern_shape]
        self.scalers = [self.multiply_left.GetValue(), self.multiply_right.GetValue(),
                        self.multiply_top.GetValue()]

        if self.data_been_filtered:
            if len(x) > 0 and len(y) > 0 and len(z) > 0:
                self.fig_tern = pca.ternary_(self.dataFiltered,
                                                          self.key_headers_tern, self.fig_tern, self.scalers, self.size_slider_tern.GetValue(),self.colordict, self.shapedict)
        else:
            if len(x) > 0 and len(y) > 0 and len(z) > 0:
                self.fig_tern = pca.ternary_(self.data,
                                                  self.key_headers_tern,
                                                          self.fig_tern,
                                             self.scalers,
                                             self.size_slider_tern.GetValue(), self.colordict, self.shapedict)
        self.tern = self.fig_tern
        self.canvas5.Destroy()
        self.canvas5 = FigCanvas(self.graphing5, -1, self.tern)
        self.confirm_btn_tern.SetLabelText("Update Graph")
        self.tern_button.Enable(True)

    def update_grid(self, data, col_headers):
        try:
            self.grid.ClearGrid()
            current_row, new_row = (self.grid.GetNumberRows(), len(data))
            current_col, new_col = (self.grid.GetNumberCols(), len(col_headers))
            if current_row > new_row:
                self.grid.DeleteRows(0, current_row - new_row, True)
            elif current_row < new_row:
                self.grid.AppendRows(new_row - current_row)
            if current_col > new_col:
                self.grid.DeleteCols(0, current_col - new_col, True)
            elif current_col < new_col:
                self.grid.AppendCols(new_col - current_col)
            for c in range(len(col_headers)):
                self.grid.SetColLabelValue(c, col_headers[c])
            for row in range(len(data)):
                for col in range(len(col_headers)):
                    self.grid.SetCellValue(row, col, str(data.iloc[row, col]))
            self.grid = self.grid
        except:
            print("INFO: Error encountered when updating grid.")

    def on_open(self, event):
        dlg = wx.FileDialog(self, message="Load Database",
                            defaultDir=os.getcwd(),
                            defaultFile="")
        if dlg.ShowModal() == wx.ID_OK:
            self.filepath = dlg.GetPath()
            self.currentdir = os.path.dirname(dlg.GetPath()) + '\\'
            print("INFO: Database Selected: " + self.filepath)
            self.data_source = str(self.filepath)
       #try:
        self.data = dc.standard_cleanse(self.filepath, None)
        self.data = self.data.reset_index(drop=True)
        self.dataFiltered = []
        self.column_headers = list(self.data.columns.values)
        is_number = np.vectorize(lambda x: np.issubdtype(x, np.number))
        is_number = is_number(self.data.dtypes)
        self.non_numeric_cols = [d for (d, remove) in zip(self.column_headers,
                                                       is_number)
                              if not remove]
        self.numeric_cols = [d for (d, remove) in zip(self.column_headers,
                                                       is_number)
                              if remove]

        self.update_grid(self.data, self.column_headers)
        self.update_combos(True)
        print("INFO: Data Imported Successfully")

    def update_combos(self, updatefilters):
        selected_PCA_items = self.PCA_selection.GetCheckedStrings()
        color_on_pca = self.color_on_pca.GetValue()
        shape_on_pca = self.shape_on_pca.GetValue()
        color_on_scatter = self.color_on_scatter.GetValue()
        label_points_pca = self.label_points_pca.GetValue()
        label_points_scatter =self.label_points_scatter.GetValue()
        shape_on_scatter = self.shape_on_scatter.GetValue()
        color_on_tern = self.color_on_tern.GetValue()
        shape_on_tern = self.shape_on_tern.GetValue()
        x_name_scatter = self.x_name_scatter.GetValue()
        y_name_scatter  = self.y_name_scatter.GetValue()
        z_name_scatter = self.z_name_scatter.GetValue()
        x1_name_scatter = self.x1_name_scatter.GetValue()
        y1_name_scatter = self.y1_name_scatter.GetValue()
        z1_name_scatter =  self.z1_name_scatter.GetValue()
        x_name_tern = self.x_name_tern.GetValue()
        y_name_tern = self.y_name_tern.GetValue()
        z_name_tern = self.z_name_tern.GetValue()
        x1_name_tern = self.x1_name_tern.GetValue()
        y1_name_tern = self.y1_name_tern.GetValue()
        z1_name_tern = self.z1_name_tern.GetValue()
        filter_combo1 = self.filter_combo1.GetValue()
        filter_combo2 = self.filter_combo2.GetValue()
        filter_combo3 = self.filter_combo3.GetValue()

        self.PCA_selection.Clear()
        self.PCA_selection.SetItems(self.numeric_cols)
        items = self.PCA_selection.GetItems()

        if updatefilters:
            self.filter_combo1.Clear()
            self.filter_combo2.Clear()
            self.filter_combo3.Clear()
            self.filter_check1.Clear()
            self.filter_check2.Clear()
            self.filter_check3.Clear()

        self.color_on_pca.Clear()
        self.shape_on_pca.Clear()
        self.color_on_scatter.Clear()
        self.label_points_pca.Clear()
        self.label_points_scatter.Clear()
        self.shape_on_scatter.Clear()
        self.color_on_tern.Clear()
        self.shape_on_tern.Clear()

        self.x_name_scatter.Clear()
        self.y_name_scatter.Clear()
        self.z_name_scatter.Clear()
        self.x1_name_scatter.Clear()
        self.y1_name_scatter.Clear()
        self.z1_name_scatter.Clear()

        self.x_name_tern.Clear()
        self.y_name_tern.Clear()
        self.z_name_tern.Clear()
        self.x1_name_tern.Clear()
        self.y1_name_tern.Clear()
        self.z1_name_tern.Clear()
        self.size_name_tern.Clear()

        self.color_on_pca.AppendItems(self.non_numeric_cols)
        self.shape_on_pca.AppendItems(self.non_numeric_cols)
        self.color_on_scatter.AppendItems(self.non_numeric_cols)
        self.label_points_pca.AppendItems(self.column_headers)
        self.label_points_scatter.AppendItems(self.column_headers)
        self.shape_on_scatter.AppendItems(self.non_numeric_cols)
        self.color_on_tern.AppendItems(self.non_numeric_cols)
        self.shape_on_tern.AppendItems(self.non_numeric_cols)
        self.x_name_scatter.AppendItems(self.numeric_cols)
        self.y_name_scatter.AppendItems(self.numeric_cols)
        self.z_name_scatter.AppendItems(self.numeric_cols)
        self.x1_name_scatter.AppendItems(self.numeric_cols)
        self.y1_name_scatter.AppendItems(self.numeric_cols)
        self.z1_name_scatter.AppendItems(self.numeric_cols)
        self.x_name_tern.AppendItems(self.numeric_cols)
        self.y_name_tern.AppendItems(self.numeric_cols)
        self.z_name_tern.AppendItems(self.numeric_cols)
        self.x1_name_tern.AppendItems(self.numeric_cols)
        self.y1_name_tern.AppendItems(self.numeric_cols)
        self.z1_name_tern.AppendItems(self.numeric_cols)
        self.size_name_tern.AppendItems(self.numeric_cols)
        self.filter_combo1.AppendItems(self.non_numeric_cols)
        self.filter_combo2.AppendItems(self.non_numeric_cols)
        self.filter_combo3.AppendItems(self.non_numeric_cols)
        self.colorcombo.AppendItems(self.non_numeric_cols)
        if len(selected_PCA_items) > 0:
            self.PCA_selection.SetCheckedStrings(selected_PCA_items)
        else:
            self.PCA_selection.SetCheckedStrings(items)

        self.color_on_pca.SetValue(color_on_pca)
        self.shape_on_pca.SetValue(shape_on_pca)
        self.color_on_scatter.SetValue(color_on_scatter)
        self.label_points_pca.SetValue(label_points_pca)
        self.label_points_scatter.SetValue(label_points_scatter)
        self.shape_on_scatter.SetValue(shape_on_scatter)
        self.color_on_tern.SetValue(color_on_tern)
        self.shape_on_tern.SetValue(shape_on_tern)
        self.x_name_scatter.SetValue(x_name_scatter)
        self.y_name_scatter.SetValue(y_name_scatter)
        self.z_name_scatter.SetValue(z_name_scatter)
        self.x1_name_scatter.SetValue(x1_name_scatter)
        self.y1_name_scatter.SetValue(y1_name_scatter)
        self.z1_name_scatter.SetValue(z1_name_scatter)
        self.x_name_tern.SetValue(x_name_tern)
        self.y_name_tern.SetValue(y_name_tern)
        self.z_name_tern.SetValue(z_name_tern)
        self.x1_name_tern.SetValue(x1_name_tern)
        self.y1_name_tern.SetValue(y1_name_tern)
        self.z1_name_tern.SetValue(z1_name_tern)
        self.filter_combo1.SetValue(filter_combo1)
        self.filter_combo2.SetValue(filter_combo2)
        self.filter_combo3.SetValue(filter_combo3)


    def on_PCA(self, event):
        print("INFO: Exporting SandClass")
        self.save_graph(self.currentdir, self.key_headers_PCA, self.PCA_plot, "PCA")

    def on_scatter(self, event):
        print("INFO: Exporting Pettijohn")
        self.save_graph(self.currentdir, self.key_headers_scatter,
                        self.scatter_plot, "Scatter")

    def on_tern(self, event):
        print("INFO: Exporting Ternary")
        self.save_graph(self.currentdir, self.key_headers_tern,
                        self.tern, "Ternary")

    def on_exit(self, event):
        print('INFO: Closing')
        self.Destroy()

class TabPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)


class SplashScreen(AS.AdvancedSplash):

    def __init__(self, parent=None):

        imagePath = "simple_plotter.png"
        bitmap = wx.Bitmap(imagePath, wx.BITMAP_TYPE_PNG)
        AS.AdvancedSplash.__init__(self, None, bitmap=bitmap, timeout=5000,
                                   agwStyle=AS.AS_TIMEOUT |
                                            AS.AS_CENTER_ON_PARENT)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()

    def OnExit(self, evt):
        self.Hide()
        MyFrame = MainFrame()
        app.SetTopWindow(MyFrame)
        MyFrame.Show(True)
        evt.Skip()


class MyApp(wx.App):

    def OnInit(self):
        MySplash = SplashScreen()
        MySplash.Show()
        return True

app = MyApp()
app.MainLoop()