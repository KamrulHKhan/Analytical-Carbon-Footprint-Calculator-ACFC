import pandas as pd
# import plotly.express as px
import streamlit as st

def names(x):return sorted(i['name'] for i in x)
# def editor(items,key,qcol='Quantity',default=0,label='Item'):
#     return st.data_editor(
#         pd.DataFrame({
#             'Name':names(items),
#             qcol:default
#         }),
        
#         hide_index=True,
#         use_container_width=True,
#         key=key,
        
#         column_config={
#             'Name':st.column_config.TextColumn(
#                 label,
#                 disabled=True
#             ),
            
#             qcol:st.column_config.NumberColumn(
#                 qcol,
#                 min_value=0,
#                 # step=1 if qcol=='Quantity' else 1e-14,
#                 format='%d' if qcol=='Quantity' else '%.15g'
#             )
#         }
#     )

def editor(items, key, qcol='Quantity', default=0, label='Item'):

    item_names = names(items)
    values_key = f"{key}_values"

    # Initialize storage
    if values_key not in st.session_state:
        st.session_state[values_key] = {}

    # Remove stored values for items that are no longer present
    st.session_state[values_key] = {
        name: value
        for name, value in st.session_state[values_key].items()
        if name in item_names
    }

    # Initialize newly added items with the default value
    for name in item_names:
        if name not in st.session_state[values_key]:
            st.session_state[values_key][name] = default

    # Build dataframe using saved values
    df = pd.DataFrame({
        'Name': item_names,
        qcol: [
            st.session_state[values_key][name]
            for name in item_names
        ]
    })

    # Create editable table
    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        key=key,
        column_config={
            'Name': st.column_config.TextColumn(
                label,
                disabled=True
            ),

            qcol: st.column_config.NumberColumn(
                qcol,
                min_value=0,
                format='%d' if qcol == 'Quantity' else '%.15g'
            )
        }
    )

    # Save edited values using item names
    for _, row in edited.iterrows():
        st.session_state[values_key][row['Name']] = row[qcol]

    return edited

def standardize_quantity(df):
    if "Quantity (mL or mg)" in df.columns:
        df["Quantity (mL or mg)"] = df["Quantity (mL or mg)"] / 1000
        df.rename(columns={"Quantity (mL or mg)": "Quantity"}, inplace=True)

    if "Quantity (mL)" in df.columns:
        df["Quantity (mL)"] = df["Quantity (mL)"] / 1000
        df.rename(columns={"Quantity (mL)": "Quantity"}, inplace=True)

    return df
