
import streamlit as st

st.set_page_config(page_title="CI Model v4.6", layout="wide")

tab1, tab2, tab3 = st.tabs(["CI Dashboard", "Assumptions", "Calculations + Explanations"])

with tab2:
    st.title("Assumptions")
    baseline_ci = st.number_input("Baseline CI", value=65.0)
    mj_per_gal = st.number_input("MJ per gallon", value=3780.0)
    lcfs_price = st.number_input("LCFS Credit ($/ton)", value=125)
    q45_price = st.number_input("45Q Credit ($/ton)", value=85)
    ng_ci = st.number_input("Natural Gas CI (gCO₂e/MJ)", value=78.4)
    rng_ci = st.number_input("RNG CI (gCO₂e/MJ)", value=15.0)
    capturepoint_ci = st.number_input("CapturePoint Grid CI (gCO₂e/MJ)", value=10.0)
    tax_rate = st.number_input("Tax Rate (%)", value=21.0)
    opex_pct = st.number_input("OpEx as % of CapEx", value=3.0)
    itc_pct = st.number_input("Solar ITC (%)", value=30.0) / 100
    monthly_cms_charge = st.number_input("Monthly CMS Demand Charge ($)", value=50000.0)
    solar_offset_pct = st.slider("Solar Offset % of CMS Demand", 0, 100, 40)

with tab1:
    st.title("CI Model Dashboard")

    st.subheader("Strategy Sliders")
    solar_pct = st.slider("Solar Adoption (%)", 0, 100, 100)
    dryer_pct = st.slider("Dryer Electrification (%)", 0, 100, 100)
    chp_pct = st.slider("CHP Adoption (%)", 0, 100, 100)
    boiler_pct = st.slider("Boiler Electrification (%)", 0, 100, 100)
    ccs_reduction = st.number_input("CCS CI Reduction", value=25.0)

    st.subheader("Fuel Source Settings")
    use_ng = st.checkbox("Use Natural Gas for Boilers/Dryers?", value=True)
    ng_boiler_pct = st.slider("NG % for Boilers", 0, 100, 50) if use_ng else 0
    ng_dryer_pct = st.slider("NG % for Dryers", 0, 100, 50) if use_ng else 0

    use_rng = st.checkbox("Use RNG for Electric?", value=True)
    rng_pct = st.slider("RNG % of Electric", 0, 100, 40) if use_rng else 0

    capturepoint_enabled = st.checkbox("Add CapturePoint Grid Connection?", value=False)
    capturepoint_pct = st.slider("CapturePoint Grid Supply %", 0, 100, 25) if capturepoint_enabled else 0

    st.subheader("Bolt-On CapEx Inputs")
    solar_capex = st.number_input("Solar CapEx ($)", value=5000000)
    dryer_capex = st.number_input("Dryer CapEx ($)", value=3000000)
    chp_capex = st.number_input("CHP CapEx ($)", value=10000000)
    boiler_capex = st.number_input("Boiler CapEx ($)", value=5000000)
    ccs_capex = st.number_input("CCS CapEx ($)", value=20000000)
    apply_itc = st.checkbox("Apply Solar ITC", value=True)

    total_reduction = (solar_pct * 0.25 + dryer_pct * 0.10 + chp_pct * 0.15 + boiler_pct * 0.12) / 100 + ccs_reduction
    ng_penalty = ((ng_boiler_pct + ng_dryer_pct) / 2) * ng_ci / 100 if use_ng else 0
    rng_benefit = rng_pct * (baseline_ci - rng_ci) / 100 if use_rng else 0
    cp_benefit = capturepoint_pct * (baseline_ci - capturepoint_ci) / 100 if capturepoint_enabled else 0

    final_ci = baseline_ci - total_reduction + ng_penalty - rng_benefit - cp_benefit
    tons_avoided = (baseline_ci - final_ci) * 110 * mj_per_gal / 1000

    lcfs_rev = tons_avoided * lcfs_price
    q45_rev = tons_avoided * q45_price
    total_rev = lcfs_rev + q45_rev

    cms_savings = monthly_cms_charge * 12 * solar_pct * solar_offset_pct / 10000

    if apply_itc:
        solar_capex *= (1 - itc_pct)
    total_capex = solar_capex + dryer_capex + chp_capex + boiler_capex + ccs_capex
    opex = total_capex * (opex_pct / 100)
    net_cost = total_capex + opex - cms_savings
    payback = net_cost / total_rev if total_rev else float("inf")
    cost_per_ton = net_cost / tons_avoided if tons_avoided else float("inf")

    st.subheader("Results Summary")
    st.metric("Final CI Score", f"{final_ci:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{tons_avoided:,.0f}")
    st.metric("LCFS Revenue", f"${lcfs_rev:,.0f}")
    st.metric("45Q Revenue", f"${q45_rev:,.0f}")
    st.metric("Total Revenue", f"${total_rev:,.0f}")
    st.metric("CMS Demand Savings", f"${cms_savings:,.0f}")
    st.metric("CapEx", f"${total_capex:,.0f}")
    st.metric("OpEx", f"${opex:,.0f}")
    st.metric("Net Cost", f"${net_cost:,.0f}")
    st.metric("Payback Period", f"{payback:.2f} yrs")
    st.metric("Cost per Ton", f"${cost_per_ton:.2f}")

with tab3:
    st.title("Calculations + Explanations")
    st.markdown("### CI Formula")
    st.markdown("""
Final CI = Baseline CI - CI Reductions + NG Penalty - RNG Benefit - CapturePoint Offset

- CI Reductions = sum of strategy reductions (solar, dryer, CHP, boiler, CCS)
- NG Penalty = ((NG Boiler % + NG Dryer %) / 2) × NG CI / 100
- RNG Benefit = RNG % × (Baseline CI - RNG CI) / 100
- CapturePoint Offset = CapturePoint % × (Baseline CI - CapturePoint CI) / 100
""")
    st.markdown("### Tons CO₂ Avoided")
    st.markdown("Tons = (Baseline CI - Final CI) × MGY × MJ/gal ÷ 1000")
    st.markdown("### Revenue")
    st.markdown("LCFS = Tons × LCFS Price ($/ton)  
45Q = Tons × 45Q Price ($/ton)")
    st.markdown("### Costs")
    st.markdown("Total CapEx = Sum of Bolt-On Costs (Solar, CHP, etc.)  
OpEx = CapEx × OpEx %  
CMS Savings = Monthly Demand Charge × 12 × (Solar % × Solar Offset %)")
