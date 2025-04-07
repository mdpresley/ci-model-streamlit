
import streamlit as st

def calculate_ci_model(capacity_mgy, solar_pct, dryer_pct, chp_pct, chp_fuel, ccs_scope, sequestration_type,
                       capex_solar, capex_dryers, capex_chp, capex_ccs, opex_pct, lcfs_credit, q45_credit):
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

    lcfs_revenue = tons_co2_avoided * lcfs_credit
    q45_revenue = tons_co2_avoided * q45_credit

    total_revenue = lcfs_revenue + q45_revenue
    total_capex = capex_solar + capex_dryers + capex_chp + capex_ccs
    total_opex = total_capex * (opex_pct / 100)
    total_cost = total_capex + total_opex

    payback_years = total_cost / total_revenue if total_revenue > 0 else float('inf')
    cost_per_ton = total_cost / tons_co2_avoided if tons_co2_avoided > 0 else float('inf')

    return final_ci, tons_co2_avoided, lcfs_revenue, q45_revenue, total_capex, total_opex, total_cost, payback_years, cost_per_ton

st.title("CI Model for Ethanol Plants – v2 with Cost & Payback")

plant = st.selectbox("Select Plant", ["Arkalon (110 MGY)", "Bonanza (65 MGY)"])
capacity = 110 if "Arkalon" in plant else 65

st.header("CI Reduction Inputs")
solar_pct = st.slider("Solar Contribution (%)", 0, 100, 60)
dryer_pct = st.slider("Dryer Electrification (%)", 0, 100, 100)
chp_pct = st.slider("CHP Contribution (%)", 0, 100, 85)
chp_fuel = st.selectbox("CHP Fuel Type", ["RNG", "Biogas", "Biomass", "NG"])
ccs_scope = st.selectbox("Carbon Capture Scope", ["Full-Plant", "Fermentation Only"])
sequestration_type = st.selectbox("Sequestration Type", ["Class VI Onsite", "45Q Partner", "Offsite"])

st.header("Credit Prices")
lcfs_credit = st.number_input("LCFS Credit ($/ton)", value=125)
q45_credit = st.number_input("45Q Credit ($/ton)", value=85)

st.header("Capital Costs ($)")
capex_solar = st.number_input("Solar CapEx", value=5000000)
capex_dryers = st.number_input("Dryer Electrification CapEx", value=3000000)
capex_chp = st.number_input("CHP CapEx", value=12000000)
capex_ccs = st.number_input("Carbon Capture CapEx", value=20000000)

opex_pct = st.number_input("Annual O&M (% of CapEx)", value=3.0)

if st.button("Run CI Model"):
    results = calculate_ci_model(capacity, solar_pct, dryer_pct, chp_pct, chp_fuel, ccs_scope, sequestration_type,
                                 capex_solar, capex_dryers, capex_chp, capex_ccs, opex_pct, lcfs_credit, q45_credit)
    
    ci, tons, lcfs, q45, capex, opex, total_cost, payback, abatement_cost = results

    st.subheader("Results")
    st.metric("Final CI Score", f"{ci:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{tons:,.0f}")
    st.metric("LCFS Revenue ($/yr)", f"${lcfs:,.0f}")
    st.metric("45Q Revenue ($/yr)", f"${q45:,.0f}")
    st.metric("Total CapEx", f"${capex:,.0f}")
    st.metric("Total OpEx (Annual)", f"${opex:,.0f}")
    st.metric("Total Cost (CapEx + OpEx)", f"${total_cost:,.0f}")
    st.metric("Payback Period (yrs)", f"{payback:.2f}")
    st.metric("Cost per Ton CO₂ Avoided", f"${abatement_cost:,.2f}")
