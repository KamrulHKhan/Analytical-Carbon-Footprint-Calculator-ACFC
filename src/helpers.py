import pandas as pd
# import plotly.express as px
import streamlit as st

def names(x):return sorted(i['name'] for i in x)
def editor(items,key,qcol='Quantity',default=0,label='Item'):
    return st.data_editor(pd.DataFrame({'Name':names(items),qcol:default}),hide_index=True,use_container_width=True,key=key,column_config={'Name':st.column_config.TextColumn(label,disabled=True),qcol:st.column_config.NumberColumn(qcol,min_value=0,step=1 if qcol=='Quantity' else .00001,format='%d' if qcol=='Quantity' else '%.4f')})

def standardize_quantity(df):
    if "Quantity (mL)" in df.columns:
        df["Quantity (mL)"] = df["Quantity (mL)"] / 1000
        df.rename(columns={"Quantity (mL)": "Quantity"}, inplace=True)

    return df
