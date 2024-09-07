import pandas as pd
import streamlit as st
import zipfile
from pathlib import Path
import altair as alt
import re
import os


def unzipper(path: str):
    r = re.compile('\d[.]csv')
    with zipfile.ZipFile(path, 'r') as zipper:
        filenames = zipper.namelist()
        data_file = list(filter(r.search, filenames))[0]
        df = zipper.open(data_file)
        df = pd.read_csv(df)
    return df

def convert_date(df):
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
    return df
def rename_df(df, mapping):
    df.rename(mapper = mapping,axis = 1, inplace = True)
    return df

class DashDf:
    def __init__(self, adjusted = False):
        self.df = {}
        self.adjusted = adjusted
        self.df_names = []
        self.df_group = {}
    def add_df(self):
        path = Path('data')
        if self.adjusted:
            path_z = path/'adjusted'
        else:
            path_z = path/'unadjusted'
        zipfiles = os.listdir(path_z)
        file_paths = list(map(lambda f: path_z / f, zipfiles))
        zipnames = list(map(lambda f: re.sub('-eng[.]zip', '', f), zipfiles))
        self.df = dict(zip(zipnames, map(unzipper,file_paths )))
        self.df_names = self.df.keys()

    def get_df(self, df_name: str):
        return self.df[df_name]
    def preprocess(self):
        # datetime
        self.df = dict(map(lambda item: (item[0], convert_date(item[1])),self.df.items()))

        # renaming columns
        name_mapping = {
            'North American Industry Classification System (NAICS)': 'NAICS'
        }
        self.df = dict(map(lambda item: (item[0], rename_df(item[1],name_mapping)), self.df.items()))
    def describe(self):
        if not self.adjusted:
            # unadjusted
            desc = {
                '14100371':'by province, monthly',
                '14100372':'by industry sector, monthly',
                '14100441':'by economic region, quarterly',
                '14100443':'by occupation, characteristics, quarterly'
            }
        else:
            # adjusted
            desc = {
                '14100432': 'by province, monthly',
                '14100406': 'by industry sector, monthly',
                '14100398': 'by economic region, quarterly',
                '14100442':'by industry sub-sector, quarterly',
                '14100443': 'by occupation, characteristics, quarterly'
            }
        return desc

class Filtered:
    def __init__(self, df):
        self.df = df

    def pivot(self, index, column, value):
        self.df = self.df.pivot(index = index,columns=column, values = value).reset_index()

    def date(self, start, end):
        self.df = self.df[(self.df['REF_DATE'] >= start) & (self.df['REF_DATE'] <= end)]

    def region(self, province_list):
        self.df = self.df[self.df['REF_DATE'].isin(province_list)]

@st.cache_data
def filter_choices(df, column, choices):
    output = df[df[column].isin(list(choices))]
    return output
def filter_choice(df, column, value):
    output = df[df[column]==value]
    return output

def rectangle(x1 = '2020-03-01', x2 = '2022-10-01' , y1 = [0], y2 = [10], dx = 140,dy = alt.value(10), color = 'orange', opacity =0.1, label = ['COVID restrictions']):
    x1 = pd.to_datetime(x1)
    x2 = pd.to_datetime(x2)
    box = pd.DataFrame(
        {'x1': x1, 'x2':x2, 'y1': y1, 'y2': y2})  # Base chart


    # Highlighted area
    highlight = alt.Chart(box).mark_rect(opacity=opacity, color=color, stroke='white').encode(
        alt.X('x1'),
        alt.Y('y1', title = ""),
        x2='x2',
        y2='y2'
    )

    # Text label for the highlighted area
    text = alt.Chart(pd.DataFrame({'x': x1, 'label': label})).mark_text(
        align='left',
        baseline='middle',
        dx=dx,  # Shift text a little to the right of the starting point
        fontSize=15,
        color='white'
    ).encode(
        x=alt.X('x:T'),
        y=dy,  # Adjust this to position the text vertically within the rectangle
        text='label:N'
    )

    return text, highlight