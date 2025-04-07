
import streamlit as st

def calculate_ci_model(capacity_mgy, solar_pct, dryer_pct, chp_pct, chp_fuel, ccs_scope, sequestration_type):
    baseline_ci = 65
    ci_solar = -0.25 * solar_pct
    ci_dryers = -0.10 * dryer_pct
    ci_chp = -0.15 * chp_pct

    fuel_impact = {"RNG": -10, "Biogas": -7, "Biomass": -6, "NG": -3}
    ci_fuel = fuel_impact.get(chp_fuel, 0)

    scope_impact = {"Full-Plant": -20, "Fermentation Only": -10}
    ci_ccs_scope = scope_impact.get(ccs_scope, 0)

    sequestration_impact = {"Class VI Onsite": -5, "45Q Partner": -3, "Offsite": -2}
    ci_sequestration = sequestration_impact.get(sequestration_type, 0)

    final_ci = baseline_ci + ci_solar + ci_dryers + ci_chp + ci_fuel + ci_ccs_scope + ci_sequestration

    tons_co2_avoided = (baseline_ci - final_ci) * capacity_mgy * 3780 / 1000
    lcfs_credit_per_ton = 125
    q45_credit_per_ton = 85

    lcfs_revenue = tons_co2_avoided * lcfs_credit_per_ton
    q45_revenue = tons_co2_avoided * q45_credit_per_ton

    return final_ci, tons_co2_avoided, lcfs_revenue, q45_revenue

st.title("CI Model for Ethanol Plants")

plant = st.selectbox("Select Plant", ["Arkalon (110 MGY)", "Bonanza (65 MGY)"])
capacity = 110 if "Arkalon" in plant else 65

solar_pct = st.slider("Solar Contribution (%)", 0, 100, 60 if capacity == 110 else 55)
dryer_pct = st.slider("Dryer Electrification (%)", 0, 100, 100 if capacity == 110 else 80)
chp_pct = st.slider("CHP Contribution (%)", 0, 100, 85 if capacity == 110 else 70)
chp_fuel = st.selectbox("CHP Fuel Type", ["RNG", "Biogas", "Biomass", "NG"])
ccs_scope = st.selectbox("Carbon Capture Scope", ["Full-Plant", "Fermentation Only"])
sequestration_type = st.selectbox("Sequestration Type", ["Class VI Onsite", "45Q Partner", "Offsite"])

if st.button("Calculate CI & Revenue"):
    ci, tons_co2, lcfs, q45 = calculate_ci_model(capacity, solar_pct, dryer_pct, chp_pct, chp_fuel, ccs_scope, sequestration_type)
    st.success(f"Final CI Score: {ci:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{tons_co2:,.0f}")
    st.metric("LCFS Revenue ($/yr)", f"${lcfs:,.0f}")
    st.metric("45Q Revenue ($/yr)", f"${q45:,.0f}")
