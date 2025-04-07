
import streamlit as st

st.set_page_config(page_title="CI Model v4", layout="wide")

def ci_reduction(ci_value, pct):
    return round(ci_value * (pct / 100), 2)

def format_ci(x): return f"-{x:.2f} gCO₂e/MJ"

st.title("🌽 CI Model for Ethanol Plants – v4 (Full)")

# Inputs
st.header("🎯 CI Target")
ci_goal = st.number_input("CI Goal (gCO₂e/MJ)", value=-3.0)
baseline_ci = 65

st.header("📉 Strategy Inputs & CI Reductions")

col1, col2 = st.columns(2)

with col1:
    solar_pct = st.slider("Solar Adoption (%)", 0, 100, 100)
    solar_ci = st.number_input("CI Impact from Solar", value=0.25)
    solar_capex = st.number_input("Solar CapEx ($)", value=5000000)
    apply_itc = st.checkbox("Apply Solar ITC (30%)", value=True)

    dryer_pct = st.slider("Electric Dryer Adoption (%)", 0, 100, 100)
    dryer_ci = st.number_input("CI Impact from Dryers", value=0.10)
    dryer_capex = st.number_input("Dryer CapEx ($)", value=3000000)

    chp_pct = st.slider("CHP Usage (%)", 0, 100, 100)
    chp_ci = st.number_input("CI Impact from CHP", value=0.15)
    chp_capex = st.number_input("CHP CapEx ($)", value=10000000)

with col2:
    boiler_pct = st.slider("Boiler Electrification (%)", 0, 100, 100)
    boiler_ci = st.number_input("CI Impact from Boilers", value=0.12)
    boiler_capex = st.number_input("Boiler CapEx ($)", value=5000000)

    st.subheader("🧊 Carbon Capture Settings")
    ccs_enabled = st.checkbox("Enable CCS", value=True)
    ccs_scope = st.selectbox("Capture Scope", ["Fermentation Only", "Full-Plant"])
    sequestration_type = st.selectbox("Sequestration Type", ["Class VI Onsite", "Offsite", "45Q Partner"])
    ccs_ci = st.number_input("CI Impact from CCS", value=25.0)
    ccs_capex = st.number_input("CCS CapEx ($)", value=20000000)

# CMS Utility
st.header("⚡ CMS Demand Charge Savings")
monthly_demand_charge = st.number_input("Monthly Demand Charge ($)", value=50000)
solar_demand_offset_pct = st.slider("Solar Offset of Demand (%)", 0, 100, 40)

# Financial
st.header("💵 Financial Assumptions")
opex_pct = st.number_input("Annual O&M (% of CapEx)", value=3.0)
lcfs_credit = st.number_input("LCFS Credit ($/ton)", value=125)
q45_credit = st.number_input("45Q Credit ($/ton)", value=85)
tax_rate = st.number_input("Effective Tax Rate (%)", value=21.0)

# CI math
solar_reduction = ci_reduction(solar_ci, solar_pct)
dryer_reduction = ci_reduction(dryer_ci, dryer_pct)
chp_reduction = ci_reduction(chp_ci, chp_pct)
boiler_reduction = ci_reduction(boiler_ci, boiler_pct)
ccs_reduction = ccs_ci if ccs_enabled else 0

total_ci_reduction = sum([solar_reduction, dryer_reduction, chp_reduction, boiler_reduction, ccs_reduction])
final_ci = baseline_ci - total_ci_reduction
ci_gap = ci_goal - final_ci

# CapEx + OpEx
if apply_itc:
    solar_capex *= 0.70  # Apply 30% ITC
total_capex = sum([solar_capex, dryer_capex, chp_capex, boiler_capex, ccs_capex if ccs_enabled else 0])
total_opex = total_capex * (opex_pct / 100)

# CMS Savings
cms_savings = monthly_demand_charge * 12 * (solar_pct / 100) * (solar_demand_offset_pct / 100)

# CO2 avoided and revenue
capacity_mgy = 110
tons_co2_avoided = (baseline_ci - final_ci) * capacity_mgy * 3780 / 1000
lcfs_revenue = tons_co2_avoided * lcfs_credit
q45_revenue = tons_co2_avoided * q45_credit if ccs_enabled else 0
total_revenue = lcfs_revenue + q45_revenue

# Net cost + payback
net_cost = total_capex + total_opex - cms_savings
payback = net_cost / total_revenue if total_revenue > 0 else float("inf")
abatement_cost = net_cost / tons_co2_avoided if tons_co2_avoided > 0 else float("inf")

# Display
st.header("📊 Results")
col1, col2 = st.columns(2)
with col1:
    st.metric("Final CI", f"{final_ci:.2f} gCO₂e/MJ")
    st.metric("CI Target Gap", f"{ci_gap:+.2f} gCO₂e/MJ")
    st.metric("Total CI Reduction", f"-{total_ci_reduction:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{tons_co2_avoided:,.0f}")

with col2:
    st.metric("Total CapEx", f"${total_capex:,.0f}")
    st.metric("OpEx (Annual)", f"${total_opex:,.0f}")
    st.metric("CMS Demand Savings", f"${cms_savings:,.0f}")
    st.metric("Net Cost (CapEx + OpEx - CMS)", f"${net_cost:,.0f}")
    st.metric("Payback (yrs)", f"{payback:.2f}")
    st.metric("Cost per Ton Avoided", f"${abatement_cost:.2f}")

st.header("💰 Revenue Summary")
st.metric("LCFS Revenue", f"${lcfs_revenue:,.0f}")
st.metric("45Q Revenue", f"${q45_revenue:,.0f}")
st.metric("Total Annual Revenue", f"${total_revenue:,.0f}")
