
import streamlit as st

st.set_page_config(page_title="CI Model v4.5", layout="wide")

tab1, tab2, tab3 = st.tabs(["📊 CI Dashboard", "📋 Assumptions", "🧮 Editable Calculations"])

# --- Shared Inputs
baseline_ci = 65
capacity_mgy = 110

# --- Tab 2: Assumptions
with tab2:
    st.title("📋 Assumptions")
    mj_per_gal = st.number_input("MJ per gallon", value=3780.0)
    tax_rate = st.number_input("Tax Rate (%)", value=21.0)
    lcfs_price = st.number_input("LCFS Credit ($/ton)", value=125)
    q45_price = st.number_input("45Q Credit ($/ton)", value=85)
    ng_ci = st.number_input("Natural Gas CI (gCO₂e/MJ)", value=78.4)
    rng_ci = st.number_input("CapturePoint RNG CI (gCO₂e/MJ)", value=15.0)
    monthly_demand_charge = st.number_input("Monthly CMS Demand Charge ($)", value=50000)
    solar_demand_offset_pct = st.slider("Solar Offset of CMS Demand (%)", 0, 100, 40)

# --- Tab 3: Editable Calculations
with tab3:
    st.title("🧮 Editable Calculation Constants")
    st.markdown("Tune the calculation weights and costs used throughout the model.")
    solar_ci = st.number_input("Solar CI Reduction", value=25.0)
    dryer_ci = st.number_input("Dryer CI Reduction", value=10.0)
    chp_ci = st.number_input("CHP CI Reduction", value=15.0)
    boiler_ci = st.number_input("Boiler Electrification CI Reduction", value=12.0)
    ccs_ci = st.number_input("CCS CI Reduction", value=25.0)

    solar_capex = st.number_input("Solar CapEx ($)", value=5000000)
    dryer_capex = st.number_input("Dryer CapEx ($)", value=3000000)
    chp_capex = st.number_input("CHP CapEx ($)", value=10000000)
    boiler_capex = st.number_input("Boiler CapEx ($)", value=5000000)
    ccs_capex = st.number_input("CCS CapEx ($)", value=20000000)
    apply_itc = st.checkbox("Apply 30% Solar ITC?", value=True)
    opex_pct = st.number_input("Opex (% of CapEx)", value=3.0)

# --- Tab 1: Main CI Dashboard
with tab1:
    st.title("📊 CI Model Dashboard")

    st.subheader("Strategy Adoption")
    solar_pct = st.slider("Solar Adoption (%)", 0, 100, 100)
    dryer_pct = st.slider("Dryer Conversion (%)", 0, 100, 100)
    chp_pct = st.slider("CHP Usage (%)", 0, 100, 100)
    boiler_pct = st.slider("Boiler Electrification (%)", 0, 100, 100)

    st.subheader("Fuel Source Settings")
    use_rng = st.checkbox("Use CapturePoint RNG for Electric Load?", value=True)
    rng_pct = st.slider("RNG % of Electric Load", 0, 100, 50) if use_rng else 0

    use_ng = st.checkbox("Use Natural Gas for Boilers/Dryers?", value=True)
    ng_boiler_pct = st.slider("NG % of Boiler Load", 0, 100, 50) if use_ng else 0
    ng_dryer_pct = st.slider("NG % of Dryer Load", 0, 100, 50) if use_ng else 0

    # CI math
    total_reduction = (solar_pct * solar_ci + dryer_pct * dryer_ci + chp_pct * chp_ci + boiler_pct * boiler_ci) / 100 + ccs_ci
    ng_penalty = ((ng_boiler_pct + ng_dryer_pct) / 2) * ng_ci / 100 if use_ng else 0
    rng_benefit = rng_pct * (baseline_ci - rng_ci) / 100 if use_rng else 0
    final_ci = baseline_ci - total_reduction + ng_penalty - rng_benefit
    tons_avoided = (baseline_ci - final_ci) * capacity_mgy * mj_per_gal / 1000

    # CapEx + OpEx
    if apply_itc:
        solar_capex *= 0.70
    total_capex = solar_capex + dryer_capex + chp_capex + boiler_capex + ccs_capex
    opex = total_capex * (opex_pct / 100)
    cms_savings = monthly_demand_charge * 12 * solar_pct * solar_demand_offset_pct / 10000
    net_cost = total_capex + opex - cms_savings

    # Revenue + Payback
    lcfs_revenue = tons_avoided * lcfs_price
    q45_revenue = tons_avoided * q45_price
    total_revenue = lcfs_revenue + q45_revenue
    payback = net_cost / total_revenue if total_revenue > 0 else float("inf")
    cost_per_ton = net_cost / tons_avoided if tons_avoided > 0 else float("inf")

    st.subheader("📈 Results Summary")
    st.metric("Final CI Score", f"{final_ci:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{tons_avoided:,.0f}")
    st.metric("Total CapEx", f"${total_capex:,.0f}")
    st.metric("OpEx (Annual)", f"${opex:,.0f}")
    st.metric("CMS Demand Savings", f"${cms_savings:,.0f}")
    st.metric("Net Cost", f"${net_cost:,.0f}")
    st.metric("Total Revenue", f"${total_revenue:,.0f}")
    st.metric("Payback Period", f"{payback:.2f} yrs")
    st.metric("Cost per Ton CO₂", f"${cost_per_ton:.2f}")
