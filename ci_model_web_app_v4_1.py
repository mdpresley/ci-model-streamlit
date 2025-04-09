
import streamlit as st

st.set_page_config(page_title="CI Model v4.1", layout="wide")

st.title("🌽 CI Model for Ethanol Plants – v4.1")

# Assumptions Section
st.sidebar.header("📌 Assumptions")
tax_rate = st.sidebar.number_input("Tax Rate (%)", value=21.0)
mj_per_gal = st.sidebar.number_input("MJ per gallon", value=3780.0)
rng_ci = st.sidebar.number_input("RNG CI (gCO₂e/MJ)", value=15.0)
ng_ci = st.sidebar.number_input("Natural Gas CI (gCO₂e/MJ)", value=78.4)
solar_itc = st.sidebar.checkbox("Apply 30% Solar ITC", value=True)

# Strategy Inputs
st.header("🛠️ Strategy Configuration")
rng_toggle = st.checkbox("Use RNG for electricity?")
rng_pct = st.slider("RNG % of Electric Load", 0, 100, 50) if rng_toggle else 0

ng_toggle = st.checkbox("Use Natural Gas in Boilers/Dryers?")
ng_pct = st.slider("NG % of Thermal Load", 0, 100, 50) if ng_toggle else 0

solar_ci = st.number_input("CI Reduction from Solar (gCO₂e/MJ)", value=25.0)
dryer_ci = st.number_input("CI Reduction from Dryers (gCO₂e/MJ)", value=10.0)
chp_ci = st.number_input("CI Reduction from CHP (gCO₂e/MJ)", value=15.0)
boiler_ci = st.number_input("CI Reduction from Electrified Boilers (gCO₂e/MJ)", value=12.0)
ccs_ci = st.number_input("CI Reduction from CCS (gCO₂e/MJ)", value=25.0)

solar_capex = st.number_input("Solar CapEx ($)", value=5000000)
dryer_capex = st.number_input("Dryer CapEx ($)", value=3000000)
chp_capex = st.number_input("CHP CapEx ($)", value=10000000)
boiler_capex = st.number_input("Boiler CapEx ($)", value=5000000)
ccs_capex = st.number_input("CCS CapEx ($)", value=20000000)

# Calculations
baseline_ci = 65
ci_reduction_total = sum([solar_ci, dryer_ci, chp_ci, boiler_ci, ccs_ci])
ng_penalty = ng_pct * ng_ci / 100 if ng_toggle else 0
rng_benefit = rng_pct * (baseline_ci - rng_ci) / 100 if rng_toggle else 0

final_ci = baseline_ci - ci_reduction_total + ng_penalty - rng_benefit
tons_co2_avoided = (baseline_ci - final_ci) * 110 * mj_per_gal / 1000

lcfs_credit = st.number_input("LCFS Credit $/ton", value=125)
q45_credit = st.number_input("45Q Credit $/ton", value=85)
lcfs_rev = tons_co2_avoided * lcfs_credit
q45_rev = tons_co2_avoided * q45_credit
revenue_total = lcfs_rev + q45_rev

capex_total = sum([solar_capex * 0.7 if solar_itc else solar_capex, dryer_capex, chp_capex, boiler_capex, ccs_capex])
opex_total = capex_total * 0.03
net_cost = capex_total + opex_total
payback = net_cost / revenue_total if revenue_total else float("inf")
cost_per_ton = net_cost / tons_co2_avoided if tons_co2_avoided else float("inf")

# Outputs
st.header("📊 Results")
st.metric("Final CI Score", f"{final_ci:.2f} gCO₂e/MJ")
st.metric("Tons CO₂ Avoided", f"{tons_co2_avoided:,.0f}")
st.metric("LCFS Revenue", f"${lcfs_rev:,.0f}")
st.metric("45Q Revenue", f"${q45_rev:,.0f}")
st.metric("Total Revenue", f"${revenue_total:,.0f}")
st.metric("Total CapEx", f"${capex_total:,.0f}")
st.metric("Total OpEx", f"${opex_total:,.0f}")
st.metric("Net Cost", f"${net_cost:,.0f}")
st.metric("Payback Period", f"{payback:.2f} yrs")
st.metric("Cost per Ton CO₂ Avoided", f"${cost_per_ton:.2f}")
