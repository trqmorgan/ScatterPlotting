import os
import ctypes
import openpyxl
import pandas as pd
import numpy as np


def read_file(filepath):

    filetype = os.path.basename(filepath)

    if filetype.endswith(('.xlsx', '.XLSX')):
        # uses openpyxl to get active sheet otherwise pandas takes
        # first sheet
        workbook = openpyxl.load_workbook(filepath)
        active_sheet = workbook.active.title
        df_original = pd.read_excel(filepath, active_sheet)
    elif filetype.endswith(('.csv', ' .CSV')):
        df_original = pd.read_csv(filepath, sep=',')
    elif filetype.endswith(('.txt', ' .TXT')):
        df_original = pd.read_table(filepath, sep='\t')
    else:
        print("Please Select .xlsx, .csv or .txt file")
    return df_original

def drop_blank_RC(dataframe, axis, how):
    """
    :param dataframe: input data frame.
    :param axis: 0 or 1, 0 = row, 1 = column
    :param how: all or any
    :return: returns df_clean frame with any col/row that contain some or all
    blank cells dropped
    """
    df_clean = dataframe.dropna(axis=axis, how=how)
    return df_clean

def fill_blanks(dataframe, fill_with):
    # used to replace blank cells in catagorical data so that they can be
    # listed in wxpython chcecklistbox, empty cells not permitted for this
    df_clean = dataframe.replace(np.nan, fill_with, regex=True)
    return df_clean

def replace_with_nan(dataframe, find_what, replace_with):
    """
    :param dataframe: input data frame.
    :param replace_what: the number/string to replace with NaN. Typically
    -999.25, lod, [np.inf, -np.inf] etc
    :return: df_clean with all of a certain number replaced with -999.25
    """
    find_what = str(find_what)
    items = find_what.split(',')

    items = [x.strip(' ') for x in items]

    for i, x in enumerate(items):
        try:
            items[i] = float(x)
        except ValueError:
            pass

    df_clean = dataframe.replace(items, replace_with, regex=True)
    return df_clean

def drop_rows_cont_certain_string(dataframe, col_name, string_to_search):
    try:
        # if the fil loading was produced by tz plotter it will have
        #  p values under column header variable. This is removed by
        #  this. ~ reverses boolean values from true to false i.e
        # does ot contain. If no column is named variable keyerror
        # is thrown.

        df_clean = dataframe[~dataframe[col_name].str.contains(string_to_search)]
        return df_clean
    except KeyError:
        print (KeyError)
        df_clean = dataframe
        return df_clean

def drop_rows_on_percent_nan(dataframe, drop_percent_threshold):
     # maps data as true / false for numeric / non numeric
     boolen_df = dataframe.applymap(np.isreal)
     # adds values of true = 1 and false = 0 for ech row
     numeric_col_count = boolen_df.sum(axis=1)
     # total colmumns
     total_col_count = len(dataframe.columns)
     # add column giving percentage numeric data in each row
     dataframe['Percent_Numeric'] = numeric_col_count/total_col_count*100
     # removes rows containing less than 70% numeric data
     df_clean = dataframe[dataframe.Percent_Numeric > drop_percent_threshold]
     df_clean = df_clean.drop('Percent_Numeric', axis=1)
     return df_clean

def drop_all_nan_cols(dataframe):
     # coerce = invalid parsing will be set as NaN
     df_clean = dataframe.apply(pd.to_numeric, errors='coerce')
     # drops any columns where all data is NaN i.e all non numeric
     df_clean = df_clean.dropna(axis=1, how='all')
     return df_clean

def standard_cleanse(filepath, save_loc):
    df_original = read_file(filepath)
    df_clean = drop_blank_RC(df_original, 0, 'all')
    df_clean = drop_blank_RC(df_clean, 1, 'all')
    df_clean = fill_blanks(df_clean, 'Blank Cell')
    df_clean = replace_with_nan(df_clean, -999.25, np.nan)
    df_clean = drop_rows_cont_certain_string(df_clean,'Variable', 'p_value')
    #df_clean = drop_rows_on_percent_nan(df_clean, 70)
    if not save_loc == None:
        if not os.path.exists(save_loc):
            os.makedirs(save_loc)
            df_clean.to_csv(save_loc)
    return df_clean

def las_cleanse(filepath, save_loc):
    df_original = read_file(filepath)
    df_clean = drop_blank_RC(df_original, 0, 'all')
    df_clean = drop_blank_RC(df_clean, 1, 'all')
    df_clean = drop_rows_on_percent_nan(df_clean, 70)
    return df_clean



