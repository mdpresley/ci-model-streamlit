
import streamlit as st

st.set_page_config(page_title="CI Model v4.7", layout="wide")

tab1, tab2, tab3 = st.tabs(["Dashboard", "Assumptions", "Editable Calculations"])

with tab2:
    st.title("Assumptions")
    baseline_ci = st.number_input("Baseline CI", value=65.0)
    mj_per_gal = st.number_input("MJ per gallon", value=3780.0)
    tax_rate = st.number_input("Tax Rate (%)", value=21.0)
    lcfs_price = st.number_input("LCFS Credit ($/ton)", value=125)
    q45_price = st.number_input("45Q Credit ($/ton)", value=85)
    ng_ci = st.number_input("Natural Gas CI (gCO₂e/MJ)", value=78.4)
    rng_ci = st.number_input("RNG CI (gCO₂e/MJ)", value=15.0)
    cp_ci = st.number_input("CapturePoint Grid CI (gCO₂e/MJ)", value=10.0)
    opex_pct = st.number_input("OpEx (% of CapEx)", value=3.0)
    itc_pct = st.number_input("Solar ITC (%)", value=30.0) / 100
    cms_charge = st.number_input("Monthly CMS Demand Charge ($)", value=50000)
    solar_offset = st.slider("Solar Offset of CMS Demand (%)", 0, 100, 40)

with tab3:
    st.title("Editable Calculation Constants")
    solar_ci = st.number_input("CI Reduction from Solar", value=25.0)
    dryer_ci = st.number_input("CI Reduction from Dryers", value=10.0)
    chp_ci = st.number_input("CI Reduction from CHP", value=15.0)
    boiler_ci = st.number_input("CI Reduction from Boiler Electrification", value=12.0)
    ccs_ci = st.number_input("CI Reduction from CCS", value=25.0)

    solar_capex = st.number_input("Solar CapEx ($)", value=5000000)
    dryer_capex = st.number_input("Dryer CapEx ($)", value=3000000)
    chp_capex = st.number_input("CHP CapEx ($)", value=10000000)
    boiler_capex = st.number_input("Boiler CapEx ($)", value=5000000)
    ccs_capex = st.number_input("CCS CapEx ($)", value=20000000)

with tab1:
    st.title("CI Model Dashboard")

    solar_pct = st.slider("Solar Adoption (%)", 0, 100, 100)
    dryer_pct = st.slider("Dryer Conversion (%)", 0, 100, 100)
    chp_pct = st.slider("CHP Integration (%)", 0, 100, 100)
    boiler_pct = st.slider("Boiler Electrification (%)", 0, 100, 100)
    ccs_enabled = st.checkbox("Enable CCS?", value=True)

    use_ng = st.checkbox("Use Natural Gas for Boilers/Dryers?", value=True)
    ng_boiler_pct = st.slider("NG % for Boilers", 0, 100, 50) if use_ng else 0
    ng_dryer_pct = st.slider("NG % for Dryers", 0, 100, 50) if use_ng else 0

    use_rng = st.checkbox("Use RNG for Plant Energy?", value=True)
    rng_plant_pct = st.slider("RNG % of Total Plant Energy", 0, 100, 30) if use_rng else 0

    cp_enabled = st.checkbox("Connect to CapturePoint Grid?", value=False)
    cp_pct = st.slider("CapturePoint Grid Supply %", 0, 100, 25) if cp_enabled else 0

    if itc_pct:
        solar_capex *= (1 - itc_pct)

    ci_reduction = (
        solar_pct * solar_ci +
        dryer_pct * dryer_ci +
        chp_pct * chp_ci +
        boiler_pct * boiler_ci
    ) / 100 + (ccs_ci if ccs_enabled else 0)

    ng_penalty = ((ng_boiler_pct + ng_dryer_pct) / 2) * ng_ci / 100 if use_ng else 0
    rng_offset = rng_plant_pct * (baseline_ci - rng_ci) / 100 if use_rng else 0
    cp_offset = cp_pct * (baseline_ci - cp_ci) / 100 if cp_enabled else 0

    final_ci = baseline_ci - ci_reduction + ng_penalty - rng_offset - cp_offset
    tons_avoided = (baseline_ci - final_ci) * 110 * mj_per_gal / 1000

    lcfs_revenue = tons_avoided * lcfs_price
    q45_revenue = tons_avoided * q45_price if ccs_enabled else 0
    total_revenue = lcfs_revenue + q45_revenue

    total_capex = solar_capex + dryer_capex + chp_capex + boiler_capex + (ccs_capex if ccs_enabled else 0)
    opex = total_capex * (opex_pct / 100)
    cms_savings = cms_charge * 12 * solar_pct * solar_offset / 10000
    net_cost = total_capex + opex - cms_savings
    payback = net_cost / total_revenue if total_revenue > 0 else float("inf")
    cost_per_ton = net_cost / tons_avoided if tons_avoided > 0 else float("inf")

    st.subheader("Results Summary")
    st.metric("Final CI", f"{final_ci:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{tons_avoided:,.0f}")
    st.metric("LCFS Revenue", f"${lcfs_revenue:,.0f}")
    st.metric("45Q Revenue", f"${q45_revenue:,.0f}")
    st.metric("Total Revenue", f"${total_revenue:,.0f}")
    st.metric("Total CapEx", f"${total_capex:,.0f}")
    st.metric("OpEx", f"${opex:,.0f}")
    st.metric("CMS Demand Savings", f"${cms_savings:,.0f}")
    st.metric("Net Cost", f"${net_cost:,.0f}")
    st.metric("Payback Period", f"{payback:.2f}")
    st.metric("Cost per Ton CO₂", f"${cost_per_ton:.2f}")
