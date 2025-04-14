
import streamlit as st

st.set_page_config(page_title="CI Model v5.3", layout="wide")

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Assumptions", "Editable Calculations", "Formulas + Explanations"])

# Assumptions Tab
with tab2:
    st.title("Assumptions")
    baseline_ci = st.number_input("Baseline CI", value=65.0)
    mj_per_gal = st.number_input("MJ per gallon", value=80.5)
    lcfs_price = st.number_input("LCFS Credit ($/ton)", value=125.0)
    q45_price = st.number_input("45Q Credit ($/ton for Class VI CCS)", value=85.0)
    rng_price = st.number_input("RNG Price ($/MMBtu)", value=18.0)
    ng_price = st.number_input("Natural Gas Price ($/MMBtu)", value=4.0)
    cms_price = st.number_input("CMS Electricity Price ($/kWh)", value=0.08)
    tax_rate = st.number_input("Tax Rate (%)", value=21.0)
    opex_pct = st.number_input("OpEx (% of CapEx)", value=3.0)
    itc_pct = st.number_input("Solar ITC (%)", value=30.0) / 100
    cms_charge = st.number_input("Monthly CMS Demand Charge ($)", value=50000.0)
    solar_offset = st.slider("Solar Offset of CMS Demand (%)", 0, 100, 40)

# Editable Calculations Tab
with tab3:
    st.title("Editable Calculations")
    solar_ci = st.number_input("Solar CI Reduction", value=25.0)
    dryer_ci = st.number_input("Dryer CI Reduction", value=10.0)
    chp_ci = st.number_input("CHP CI Reduction", value=15.0)
    boiler_ci = st.number_input("Boiler CI Reduction", value=12.0)
    class6_ci = st.number_input("Class VI CCS CI Reduction", value=25.0)
    solar_capex = st.number_input("Solar CapEx ($)", value=5000000)
    dryer_capex = st.number_input("Dryer CapEx ($)", value=3000000)
    chp_capex = st.number_input("CHP CapEx ($)", value=10000000)
    boiler_capex = st.number_input("Boiler CapEx ($)", value=5000000)
    class6_capex = st.number_input("Class VI CCS CapEx ($)", value=20000000)

# Dashboard Tab
with tab1:
    st.title("CI Model Dashboard")
    solar_pct = st.slider("Solar Adoption (%)", 0, 100, 100)
    disable_dryers = st.checkbox("Disable Dryers", value=False)
    if not disable_dryers:
        dryer_pct = st.slider("Dryer Conversion (%)", 0, 100, 100)
        ng_dryer_pct = st.slider("NG % for Dryers", 0, 100, 50)
    else:
        dryer_pct = 0
        ng_dryer_pct = 0

    chp_pct = st.slider("CHP Integration (%)", 0, 100, 100)
    boiler_pct = st.slider("Boiler Electrification (%)", 0, 100, 100)
    use_class6 = st.checkbox("Enable Class VI CCS?", value=True)
    ccs_scope = st.selectbox("CCS Scope", ["Fermentation Only", "Fermentation + Boiler + CHP"]) if use_class6 else "None"

    use_ng = st.checkbox("Use Natural Gas for Boilers?", value=True)
    ng_boiler_pct = st.slider("NG % for Boilers", 0, 100, 50) if use_ng else 0

    use_rng = st.checkbox("Use RNG?", value=True)
    rng_pct = st.slider("RNG % of Plant Energy", 0, 100, 30) if use_rng else 0

    combine_cp = st.checkbox("Simulate CapturePoint Integration?", value=True)
    if combine_cp:
        arkalon_energy = st.number_input("Arkalon Energy Use (MWh/year)", value=100000.0)
        cp_energy = st.number_input("CapturePoint Available Energy (MWh/year)", value=30000.0)
        cp_ci = st.number_input("CapturePoint CI (gCO₂e/MJ)", value=10.0)
        cp_supply_pct = min(cp_energy / arkalon_energy, 1.0)
    else:
        cp_supply_pct = 0.0
        cp_ci = 0.0

    ci_reduction = (solar_pct * solar_ci + dryer_pct * dryer_ci + chp_pct * chp_ci + boiler_pct * boiler_ci) / 100
    if use_class6:
        ci_reduction += class6_ci if ccs_scope == "Fermentation + Boiler + CHP" else class6_ci * 0.6

    ng_penalty = ((ng_boiler_pct + ng_dryer_pct) / 2) * 78.4 / 100 if use_ng else 0
    rng_offset = rng_pct * (baseline_ci - 15.0) / 100 if use_rng else 0
    cp_offset = cp_supply_pct * (baseline_ci - cp_ci)

    final_ci = baseline_ci - ci_reduction + ng_penalty - rng_offset - cp_offset
    tons_avoided = (baseline_ci - final_ci) * 110 * mj_per_gal / 1000
    lcfs_revenue = tons_avoided * lcfs_price
    q45_revenue = tons_avoided * q45_price if use_class6 else 0
    total_revenue = lcfs_revenue + q45_revenue

    if itc_pct:
        solar_capex *= (1 - itc_pct)
    total_capex = solar_capex + dryer_capex + chp_capex + boiler_capex + (class6_capex if use_class6 else 0)
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
    st.metric("CapEx", f"${total_capex:,.0f}")
    st.metric("OpEx", f"${opex:,.0f}")
    st.metric("CMS Demand Savings", f"${cms_savings:,.0f}")
    st.metric("Net Cost", f"${net_cost:,.0f}")
    st.metric("Payback Period", f"{payback:.2f} yrs")
    st.metric("Cost per Ton", f"${cost_per_ton:.2f}")

# Explanations Tab
with tab4:
    st.title("Formulas + Explanations")
    st.markdown("""
### 🧠 Final CI Calculation
Final CI = Baseline CI  
− CI Reductions  
+ NG Penalty  
− RNG Offset  
− CapturePoint Offset

### 🧪 Class VI CCS
• Reduces CI based on amount of CO₂ captured.  
• If "Fermentation Only" is selected, CI reduction = 60% of full value.  
• 45Q revenue = Tons × $85  
• **NOT based on energy usage** — this is based on tons of carbon removed.

### ⚡ CapturePoint Offset
CapturePoint Offset = (CP Energy / Arkalon Energy) × (Baseline CI − CP CI)  
• Reduces CI based on how much of Arkalon's power is supplied by CapturePoint  
• **IS based on energy share**, not captured carbon

### 🧮 Tons CO₂ Avoided
= (Baseline CI − Final CI) × MGY × MJ/gal ÷ 1000  
• Converts CI savings into physical tons of CO₂

### 💸 Revenue
- LCFS = Tons × LCFS Price  
- 45Q = Tons × $85 (if CCS enabled)

### 💰 Cost Breakdown
- CapEx = Bolt-on total  
- OpEx = CapEx × OpEx %  
- CMS Savings = Monthly × 12 × Solar % × Offset %  
- Net Cost = CapEx + OpEx − CMS Savings  
- Payback = Net Cost ÷ Total Revenue  
- Cost per Ton = Net Cost ÷ Tons CO₂ Avoided
""")
