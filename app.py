import pandas as pd
import plotly.express as px
import streamlit as st
# import base64
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from src.factors import (
    GRID_DEFAULT, MOBILE_PHASES, OTHER_CHEMICALS, CONSUMABLES, ANALYTICAL_INSTRUMENTS, GAS_GENERATORS, GENERAL_LAB_EQUIPMENT,
    SOLVENT_PACKAGING_ITEM_NAMES_EXCLUDED, SOLVENT_WASTE_ITEM_NAMES_EXCLUDED, GAS_TRANSPORTATION_ITEM_NAMES, 
    INSTRUMENT_POWER,
)
from src.helpers import (
    names, editor, standardize_quantity
)

from src.calculations import (
    calculate_solvent_transportation_waste_quantity,
    add_cip_chemicals,
    calculate_energy_use,
    calculate_co2_emissions,
)

st.set_page_config(page_title='Analytical Carbon Footprint Calculator (ACFC)',page_icon='🌍',layout='wide')

st.markdown(
    """
    <style>
    .st-key-reset_control {
        position: fixed;
        top: 65px;
        right: 20px;
        width: auto;
        z-index: 999;
    }

    .st-key-reset_control button {
        background-color: #0067B8;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
    }

    /* ADD THIS */
    .st-key-reset_control button p {
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    .st-key-reset_control button:hover {
        background-color: #005A9E;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container(key="reset_control"):
    if st.button("🔄 Reset Calculator", key="reset_calculator"):
        st.session_state.clear()
        st.rerun()

if "result" not in st.session_state:
    st.session_state.result = None

col_logo, col_text = st.columns([3, 7])

with col_logo:
    st.image("assets/logo.png", use_container_width=True)

with col_text:
    st.markdown(
        """
        <h1 style="margin-bottom:0px;">
        Analytical Carbon Footprint Calculator (ACFC)
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p style="font-size:18px; color:#555555;">
        Quantifying the life-cycle carbon footprint (kg CO₂e) of analytical methods over 20- and 100-year time horizons (GWP20 and GWP100).
        </p>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    **Developed by:** Md Kamrul Hasan Khan (MdKamrulHasan.Khan@pfizer.com), Md Sajjadur Rahman (MdSajjadur.Rahman@pfizer.com), William Hiers (William.Heirs@pfizer.com)
    """
)

user_input_factors = pd.read_csv('data/user_input_factors.csv')

default_inputs = pd.read_csv('data/background_input_factors.csv')

with st.sidebar:
    st.header('Method setup'); 
    method=st.text_input('Method name','New method'); 
    technique=st.selectbox('Technique',['UHPLC','HPLC','GC','SFC']); 
    runtime=st.number_input('Runtime per injection (min)',0.0,value=10.0,step=.5); 
    injections=st.number_input('Injection / vial count',0,value=1,step=1); 
    grid = float(GRID_DEFAULT); 
    hours=runtime*injections/60; 
    
st.header("1. Chemicals")

st.subheader('Mobile Phase / Diluent')
mobile = editor(
    MOBILE_PHASES.get(technique, []),
    'mobile',
    'Quantity (mL)',
    0.0,
    'Chemical'
)

st.subheader('Reagents and Other Chemicals')
selected = st.multiselect(
    'Select chemicals used',
    names(OTHER_CHEMICALS)
)

other = editor(
    [{'name': x} for x in selected],
    'other',
    'Quantity (mL or mg)',
    0.0,
    'Chemical'
)

st.header("2. Consumables")

cons = editor(
    CONSUMABLES['General'] + CONSUMABLES.get(technique, []),
    'cons',
    label='Consumable'
)

st.header("3. Lab Equipment")

l, r = st.columns(2)

with l:
    st.subheader('Analytical Instruments')

    inst = editor(
        ANALYTICAL_INSTRUMENTS.get(technique, []),
        'inst',
        label='Instrument'
    )

    gas = pd.DataFrame(columns=['Name', 'Quantity'])

    if technique == 'GC':
        st.subheader('Gas Generators')
        gas = editor(
            GAS_GENERATORS['GC'],
            'gas',
            label='Generator'
        )

with r:
    st.subheader('General Lab Equipment')
    general = editor(
        GENERAL_LAB_EQUIPMENT['General'] + 
            GENERAL_LAB_EQUIPMENT.get(technique, []),
        'general',
        label='Equipment'
    )

# =====================================================
# Calculate Button
# =====================================================

if st.button(
    # "Calculate emissions",
    "Click to Calculate Carbon Footprint",
    type="primary",
    use_container_width=True,
    disabled=hours > 24
):

    try:

        # =====================================================
        # combine all user inputs into a single DataFrame
        # =====================================================

        all_user_inputs = pd.concat([
                standardize_quantity(pd.DataFrame(mobile)), 
                standardize_quantity(pd.DataFrame(other)),
                standardize_quantity(pd.DataFrame(cons)),
                standardize_quantity(pd.DataFrame(inst)),
                standardize_quantity(pd.DataFrame(gas)),
                standardize_quantity(pd.DataFrame(general)),
            ],
            ignore_index=True)
        
        user_inputs_with_factors = all_user_inputs.merge(
            user_input_factors,
            on="Name",
            how="left"
        )
        
        user_and_default_inputs = pd.concat([
            user_inputs_with_factors, 
            default_inputs
            ], ignore_index=True)
        
        user_inputs_with_factors = add_cip_chemicals(
            user_and_default_inputs, 
            user_input_factors
            )

        user_inputs_with_factors['Total Mass (kg)'] = user_inputs_with_factors['Quantity']*user_inputs_with_factors['Density']*user_inputs_with_factors['Unit Mass']

        packaging_transportation_waste_quantity = calculate_solvent_transportation_waste_quantity(
            df=user_inputs_with_factors,
            exclude_solvent_packaging_names=SOLVENT_PACKAGING_ITEM_NAMES_EXCLUDED,
            gas_transport_names=GAS_TRANSPORTATION_ITEM_NAMES,
            exclude_solvent_waste_names=SOLVENT_WASTE_ITEM_NAMES_EXCLUDED
        )
    
       
        packaging_transportation_waste_quantity_with_factors = packaging_transportation_waste_quantity.merge(
            user_input_factors,
            on="Name",
            how="left"
        )

        all_inputs_with_factors = pd.concat(
            [
                user_inputs_with_factors, 
                packaging_transportation_waste_quantity_with_factors
            ],
            ignore_index=True
        )

        updated_energy_properties = calculate_energy_use(
            all_inputs_with_factors, 
            INSTRUMENT_POWER, 
            runtime, 
            injections
        )

        updated_energy_properties_filtered = updated_energy_properties[updated_energy_properties["Quantity"] > 0]

        results = calculate_co2_emissions(
            updated_energy_properties_filtered, 
            grid
            )
        
        st.session_state.result = {
            "detail": results,
            "method": method,
            "technique": technique
        }

    except (ValueError, KeyError, TypeError) as error:
        st.error(
            f"Calculation could not be completed: {error}"
        )

# =====================================================
# Results
# =====================================================

# if "result" in st.session_state:
if st.session_state.result is not None:
    result = st.session_state.result
    detail = result["detail"]

    st.header("Results")

    # =================================================
    # Summary Metrics
    # =================================================

    if detail.loc[
        detail["Name"].isin(user_input_factors["Name"][:69]),
        "Quantity"
    ].empty:
        total_gwp20 = 0.0
        total_gwp100 = 0.0
    else:
        total_gwp20 = detail["GWP20 (kg CO2e)"].sum()
        total_gwp100 = detail["GWP100 (kg CO2e)"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total GWP20",
        f"{total_gwp20:,.1f} kg CO₂e"
    )

    col2.metric(
        "Total GWP100",
        f"{total_gwp100:,.1f} kg CO₂e"
    )

    col3.metric(
        "Technique",
        result["technique"]
    )

    col4.metric(
        "Method",
        result["method"]
    )

    metrics_df = pd.DataFrame({
        "Technique": [result["technique"]],
        "Method": [result["method"]],
        "Total GWP20 (kg CO2e)": [total_gwp20],
        "Total GWP100 (kg CO2e)": [total_gwp100]
    })
    # st.dataframe(metrics_df, hide_index=True)

    st.download_button(
        "Download ACFC Summary Results (CSV)",
        metrics_df.to_csv(index=False).encode("utf-8-sig"),
        "ACFC_summary_results.csv",
        "text/csv",
        use_container_width=True
    )
    # =================================================
    # Charts and Detailed Results
    # =================================================
    # if detail.empty:
    if detail.loc[
            detail["Name"].isin(user_input_factors["Name"][:69]),
            "Quantity"
        ].empty:

        st.info(
            "Enter at least one quantity greater than zero."
        )

    else:

        emissions_by_category = (
            detail.groupby(
                "Category",
                as_index=False
            )[
                [
                    "GWP20 (kg CO2e)",
                    "GWP100 (kg CO2e)"
                ]
            ]
            .sum()
        )

        # chart1, chart2, chart3 = st.columns(3)

        # with chart1:

        #     fig_bar = px.bar(
        #             emissions_by_category,
        #             x="Category",
        #             y=[
        #                 "GWP20 (kg CO2e)",
        #                 "GWP100 (kg CO2e)"
        #             ],
        #             barmode="group",
        #             title="Emissions by Category",
        #             labels={
        #                 "value": "Emissions (kg CO₂e)"
        #             }
        #         )
        #     st.plotly_chart(
        #         # px.bar(
        #         #     emissions_by_category,
        #         #     x="Category",
        #         #     y=[
        #         #         "GWP20 (kg CO2e)",
        #         #         "GWP100 (kg CO2e)"
        #         #     ],
        #         #     barmode="group",
        #         #     title="Emissions by Category",
        #         #     labels={
        #         #         "value": "Emissions (kg CO₂e)"
        #         #     }
        #         # ),
        #         fig_bar,
        #         use_container_width=True
        #     )

        # with chart2:
        #     fig_pie20 = px.pie(
        #             emissions_by_category,
        #             names="Category",
        #             values="GWP20 (kg CO2e)",
        #             hole=0.45,
        #             title="GWP20 Contribution"
        #         )

        #     st.plotly_chart(
        #         # px.pie(
        #         #     emissions_by_category,
        #         #     names="Category",
        #         #     values="GWP20 (kg CO2e)",
        #         #     hole=0.45,
        #         #     title="GWP20 Contribution"
        #         # ),
        #         fig_pie20,
        #         use_container_width=True
        #     )

        # with chart3:

        #     fig_pie100 = px.pie(
        #         emissions_by_category,
        #         names="Category",
        #         values="GWP100 (kg CO2e)",
        #         hole=0.45,
        #         title="GWP100 Contribution"
        #     )

        #     st.plotly_chart(
        #         # px.pie(
        #         #     emissions_by_category,
        #         #     names="Category",
        #         #     values="GWP100 (kg CO2e)",
        #         #     hole=0.45,
        #         #     title="GWP100 Contribution"
        #         # ),
        #         fig_pie100,
        #         use_container_width=True
        #     )

        fig = make_subplots(
            rows=1,
            cols=3,
            specs=[
                [{"type": "xy"}, {"type": "domain"}, {"type": "domain"}]
            ],
            subplot_titles=[
                "Emissions by Category",
                "GWP20 Contribution",
                "GWP100 Contribution"
            ]
        )

        # -------------------------
        # Bar chart
        # -------------------------
        fig.add_trace(
            go.Bar(
                x=emissions_by_category["Category"],
                y=emissions_by_category["GWP20 (kg CO2e)"],
                name="GWP20 (kg CO2e)",
                legend="legend"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Bar(
                x=emissions_by_category["Category"],
                y=emissions_by_category["GWP100 (kg CO2e)"],
                name="GWP100 (kg CO2e)",
                legend="legend"
            ),
            row=1,
            col=1
        )

        # -------------------------
        # GWP20 donut
        # -------------------------
        fig.add_trace(
            go.Pie(
                labels=emissions_by_category["Category"],
                values=emissions_by_category["GWP20 (kg CO2e)"],
                hole=0.45,
                name="GWP20",
                legend="legend2"
            ),
            row=1,
            col=2
        )

        # -------------------------
        # GWP100 donut
        # -------------------------
        fig.add_trace(
            go.Pie(
                labels=emissions_by_category["Category"],
                values=emissions_by_category["GWP100 (kg CO2e)"],
                hole=0.45,
                name="GWP100",
                legend="legend2",
                showlegend=False   # don't repeat category legend
            ),
            row=1,
            col=3
        )

        # -------------------------
        # Layout
        # -------------------------
        fig.update_layout(
            barmode="group",
            height=450,

            # Bar plot legend
            legend=dict(
                x=0.20,
                y=1.0,
                xanchor="left",
                yanchor="top"
            ),

            # ONE shared category legend for both pie charts
            legend2=dict(
                x=1.02,
                y=1.0,
                xanchor="left",
                yanchor="top"
            ),

            # Space for pie-chart legend
            margin=dict(r=150)
        )

        fig.update_yaxes(
            title_text="Emissions (kg CO₂e)",
            row=1,
            col=1
        )

        # -------------------------
        # ONE Streamlit call
        # -------------------------
        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Download Detailed Results")

        # st.dataframe(
        #     detail,
        #     use_container_width=True,
        #     hide_index=True
        # )

    # =================================================
    # Export Results
    # =================================================
    export_df = detail.copy()

    export_df.insert(
        0,
        "Method Name",
        result["method"]
    )

    export_df.insert(
        1,
        "Technique",
        result["technique"]
    )

    if not detail.loc[
        detail["Name"].isin(user_input_factors["Name"][:69]),
        "Quantity"
    ].empty:

        total_row = pd.DataFrame([{
            "Method Name": "Total",
            "GWP20 (kg CO2e)": export_df["GWP20 (kg CO2e)"].sum().round(1),
            "GWP100 (kg CO2e)": export_df["GWP100 (kg CO2e)"].sum().round(1)
        }])

        export_df = pd.concat([export_df, total_row], ignore_index=True)
        st.download_button(
            "Download ACFC Detailed Results (CSV)",
            export_df.to_csv(index=False).encode("utf-8-sig"),
            "ACFC_detailed_results.csv",
            "text/csv",
            use_container_width=True
        )
