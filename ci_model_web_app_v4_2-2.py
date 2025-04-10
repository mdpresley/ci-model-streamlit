
import streamlit as st

st.set_page_config(page_title="CI Model v4.2", layout="wide")

tab1, tab2 = st.tabs(["📊 CI Dashboard", "📘 Calculation Breakdown"])

# --- Assumptions Sidebar ---
st.sidebar.header("📌 Assumptions")
tax_rate = st.sidebar.number_input("Tax Rate (%)", value=21.0)
mj_per_gal = st.sidebar.number_input("MJ per gallon", value=3780.0)
lcfs_price = st.sidebar.number_input("LCFS Credit ($/ton)", value=125)
q45_price = st.sidebar.number_input("45Q Credit ($/ton)", value=85)

# --- Main Tab: CI Dashboard ---
with tab1:
    st.title("🌽 CI Model for Ethanol Plants – v4.2")

    st.subheader("🔌 RNG and NG Configuration")
    use_rng = st.checkbox("Use CapturePoint RNG for Electric Load?")
    rng_pct = st.slider("RNG % of Electric Load", 0, 100, 40) if use_rng else 0
    rng_ci = st.number_input("RNG CI (gCO₂e/MJ)", value=15.0) if use_rng else 0

    use_ng = st.checkbox("Use Natural Gas for Boilers/Dryers?")
    ng_boiler_pct = st.slider("NG % of Boiler Load", 0, 100, 50) if use_ng else 0
    ng_dryer_pct = st.slider("NG % of Dryer Load", 0, 100, 50) if use_ng else 0
    ng_ci = st.number_input("NG CI (gCO₂e/MJ)", value=78.4) if use_ng else 0

    st.subheader("⚙️ CI Reduction Inputs")
    solar_ci = st.number_input("Solar CI Reduction", value=25.0)
    dryer_ci = st.number_input("Dryer CI Reduction", value=10.0)
    chp_ci = st.number_input("CHP CI Reduction", value=15.0)
    boiler_ci = st.number_input("Boiler Electrification CI Reduction", value=12.0)
    ccs_ci = st.number_input("CCS CI Reduction", value=25.0)

    st.subheader("💰 CapEx per Bolt-On")
    solar_capex = st.number_input("Solar CapEx ($)", value=5_000_000)
    dryer_capex = st.number_input("Dryer CapEx ($)", value=3_000_000)
    chp_capex = st.number_input("CHP CapEx ($)", value=10_000_000)
    boiler_capex = st.number_input("Boiler CapEx ($)", value=5_000_000)
    ccs_capex = st.number_input("CCS CapEx ($)", value=20_000_000)
    apply_itc = st.checkbox("Apply 30% Solar ITC", value=True)

    # --- Calculations ---
    baseline_ci = 65
    total_reduction = sum([solar_ci, dryer_ci, chp_ci, boiler_ci, ccs_ci])
    ng_penalty = (ng_boiler_pct + ng_dryer_pct) * ng_ci / 200 if use_ng else 0
    rng_benefit = rng_pct * (baseline_ci - rng_ci) / 100 if use_rng else 0
    final_ci = baseline_ci - total_reduction + ng_penalty - rng_benefit

    # Tons CO₂ avoided
    capacity_mgy = 110
    tons_co2_avoided = (baseline_ci - final_ci) * capacity_mgy * mj_per_gal / 1000

    # Revenue
    lcfs_revenue = tons_co2_avoided * lcfs_price
    q45_revenue = tons_co2_avoided * q45_price
    total_revenue = lcfs_revenue + q45_revenue

    # CapEx/OpEx
    if apply_itc:
        solar_capex *= 0.70
    capex_total = sum([solar_capex, dryer_capex, chp_capex, boiler_capex, ccs_capex])
    opex_total = capex_total * 0.03
    net_cost = capex_total + opex_total
    payback = net_cost / total_revenue if total_revenue > 0 else float('inf')
    cost_per_ton = net_cost / tons_co2_avoided if tons_co2_avoided > 0 else float('inf')

    # --- Results Display ---
    st.subheader("📊 Results Summary")
    st.metric("Final CI Score", f"{final_ci:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{tons_co2_avoided:,.0f}")
    st.metric("Total CapEx", f"${capex_total:,.0f}")
    st.metric("Total OpEx", f"${opex_total:,.0f}")
    st.metric("Total Revenue", f"${total_revenue:,.0f}")
    st.metric("Payback (yrs)", f"{payback:.2f}")
    st.metric("Cost per Ton CO₂", f"${cost_per_ton:.2f}")

# --- Tab 2: Calculation Breakdown ---
with tab2:
    st.title("📘 Calculation Breakdown")
    st.markdown(f'''
    **CI Formula**  
    `Final CI = Baseline CI - Total Reductions + NG Penalty - RNG Benefit`

    **Tons CO₂ Avoided**  
    `Tons = (Baseline CI - Final CI) × MGY × MJ/gal ÷ 1000`  
    = ({baseline_ci} - {final_ci:.2f}) × {capacity_mgy} × {mj_per_gal} / 1000

    **Revenue**  
    LCFS: `{tons_co2_avoided:,.0f} × ${lcfs_price}` = `${lcfs_revenue:,.0f}`  
    45Q: `{tons_co2_avoided:,.0f} × ${q45_price}` = `${q45_revenue:,.0f}`

    **Costs**  
    - Solar ITC applied: {apply_itc}
    - Total CapEx: `${capex_total:,.0f}`
    - OpEx (3%): `${opex_total:,.0f}`  
    - Net Cost: `${net_cost:,.0f}`  
    - Payback = Net / Revenue = `${payback:.2f}` yrs  
    - Cost/Ton = `${cost_per_ton:.2f}`
    ''')

# --- Footer ---
st.caption("CI Model v4.2 – Conestoga Energy | Final Build")
