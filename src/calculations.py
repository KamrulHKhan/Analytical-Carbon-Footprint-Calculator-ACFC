import pandas as pd

def calculate_solvent_transportation_waste_quantity(
    df,
    exclude_solvent_packaging_names,
    gas_transport_names,
    exclude_solvent_waste_names
    ):
    if df.empty:return 0.0
    
    solvent_packaging_quantity = df.loc[(df["Category"] == "Chemical") & (~df["Name"].isin(exclude_solvent_packaging_names))]['Total Mass (kg)'].sum() if not df.empty else 0.0
    
    consumable_transportation_quantity = df.loc[(df["Category"] == "Consumable")]['Total Mass (kg)'].sum() if not df.empty else 0.0
    
    gas_transportation_quantity = df.loc[df["Name"].isin(gas_transport_names)]['Total Mass (kg)'].sum() if 'Mass (kg)' in df.columns else 0.0
    
    solvent_trasportation_quantity = solvent_packaging_quantity * 1.4686
    
    solvent_waste_quantity = df.loc[(df["Category"] == "Chemical") & (~df["Name"].isin(exclude_solvent_waste_names))]['Total Mass (kg)'].sum() if not df.empty else 0.0
    
    solid_waste_quantity = consumable_transportation_quantity
        
    output = pd.DataFrame({
        "Name": [
            "Solvent Packaging",
            "Consumable Transportation",
            "Gas Transportation",
            "Solvent Transportation",
            "Solvent Waste",
            "Solid Waste"
        ],
        "Quantity": [
            solvent_packaging_quantity,
            consumable_transportation_quantity,
            gas_transportation_quantity,
            solvent_trasportation_quantity,
            solvent_waste_quantity,
            solid_waste_quantity
        ]
    })
    return output

def add_cip_chemicals(user_inputs_with_factors, all_factors):
    """
    Add CIP 100 and CIP 200 rows when a Glassware Washer is present.

    CIP Quantity =
        0.43 * Density / Split Resource Factor
    """

    glassware_washer_qty = user_inputs_with_factors.loc[
        user_inputs_with_factors["Name"] == "Glassware Washer",
        "Quantity"
    ].squeeze()

    if glassware_washer_qty <= 0:
        return user_inputs_with_factors

    cip_df = pd.DataFrame({
        "Name": [
            "CIP 100 (mainly Potassium Hydroxide)",
            "CIP 200 (mainly Phosphoric Acid)"
        ],
        "Quantity": [0.0, 0.0]
    })

    cip_df = cip_df.merge(
        all_factors,
        on="Name",
        how="left"
    )

    cip_df["Quantity"] = (
        0.43
        * cip_df["Density"]
        / cip_df["Split Resource Factor"]
    )

    return pd.concat(
        [user_inputs_with_factors, cip_df],
        ignore_index=True
    )

def calculate_energy_use(equipment, power, runtime, injections):
    # 1. Calculate run time in hours
    run = runtime * injections / 60
    
    # 2. Safely copy power dataframe and calculate Energy Use
    power_df = power.copy()
    power_df["Energy Use"] = (
        (24 - run) * power_df["idle"] 
        + run * power_df["run"]
    ) / 1000
    
    # 3. Create the lookup dictionary directly from the Name and calculated Energy Use
    # (Removed the .map(key) unless you absolutely need string normalization)
    energy_lookup = dict(zip(power_df["Name"], power_df["Energy Use"]))
    
    # 4. Safely copy equipment dataframe
    equipment_df = equipment.copy()
    
    # 5. Map the energy values directly using 'Name' and fallback to original values if no match is found
    equipment_df["Energy Use"] = (
        equipment_df["Name"]
        .map(energy_lookup)
        .fillna(equipment_df["Energy Use"])
    )
    
    return equipment_df


def calculate_co2_emissions(df, grid_electricity_factor):
    """
    Calculate GWP20 and GWP100 emissions for reusable equipment.

    GWP20 =
        Quantity * Density * GWP20 Emission Factor
        / (Lifetime Uses * Split Resource Factor)
        + Energy Use * Grid Electricity Factor

    GWP100 =
        Quantity * Density * GWP100 Emission Factor
        / (Lifetime Uses * Split Resource Factor)
        + Energy Use * Grid Electricity Factor
    """

    df = df.copy()

    df["GWP20 (kg CO2e)"] = (
        df["Quantity"]
        * df["Density"]
        * df["GWP20 Emission Factor"]
        / (df["Lifetime Uses"] * df["Split Resource Factor"])
        + df["Energy Use"] * grid_electricity_factor / df["Split Resource Factor"]
    ) * 1.01

    df["GWP100 (kg CO2e)"] = (
        df["Quantity"]
        * df["Density"]
        * df["GWP100 Emission Factor"]
        / (df["Lifetime Uses"] * df["Split Resource Factor"])
        + df["Energy Use"] * grid_electricity_factor / df["Split Resource Factor"]
    ) * 1.01

    return df
