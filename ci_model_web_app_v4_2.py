
import streamlit as st

st.set_page_config(page_title="CI Model v4.2", layout="wide")

tab1, tab2 = st.tabs(["📊 Main CI Dashboard", "📘 Calculation Breakdown"])

st.sidebar.header("📌 Assumptions")
tax_rate = st.sidebar.number_input("Tax Rate (%)", value=21.0)
mj_per_gal = st.sidebar.number_input("MJ per gallon", value=3780.0)
rng_ci = st.sidebar.number_input("RNG CI (gCO₂e/MJ)", value=15.0)
ng_ci = st.sidebar.number_input("Natural Gas CI (gCO₂e/MJ)", value=78.4)
solar_itc = st.sidebar.checkbox("Apply 30% Solar ITC", value=True)

with tab1:
    st.title("🌽 CI Model v4.2 – Main Dashboard")

    st.subheader("🔌 RNG and NG Settings")
    use_rng = st.checkbox("Use RNG for Electric Load?")
    rng_pct = st.slider("RNG % of Electric Load", 0, 100, 40) if use_rng else 0

    use_ng = st.checkbox("Use Natural Gas for Boilers/Dryers?")
    ng_boiler_pct = st.slider("NG % of Boiler Load", 0, 100, 50) if use_ng else 0
    ng_dryer_pct = st.slider("NG % of Dryer Load", 0, 100, 50) if use_ng else 0

    st.subheader("⚙️ CI Reductions and CapEx")
    solar_ci = st.number_input("Solar CI Reduction", value=25.0)
    dryer_ci = st.number_input("Dryer CI Reduction", value=10.0)
    chp_ci = st.number_input("CHP CI Reduction", value=15.0)
    boiler_ci = st.number_input("Boiler CI Reduction", value=12.0)
    ccs_ci = st.number_input("CCS CI Reduction", value=25.0)

    solar_capex = st.number_input("Solar CapEx ($)", value=5_000_000)
    dryer_capex = st.number_input("Dryer CapEx ($)", value=3_000_000)
    chp_capex = st.number_input("CHP CapEx ($)", value=10_000_000)
    boiler_capex = st.number_input("Boiler CapEx ($)", value=5_000_000)
    ccs_capex = st.number_input("CCS CapEx ($)", value=20_000_000)

    baseline_ci = 65
    total_reduction = sum([solar_ci, dryer_ci, chp_ci, boiler_ci, ccs_ci])
    ng_penalty = (ng_boiler_pct + ng_dryer_pct) * ng_ci / 200 if use_ng else 0
    rng_benefit = rng_pct * (baseline_ci - rng_ci) / 100 if use_rng else 0
    final_ci = baseline_ci - total_reduction + ng_penalty - rng_benefit

    st.metric("Final CI Score", f"{final_ci:.2f} gCO₂e/MJ")
    st.metric("Total CI Reduction", f"{baseline_ci - final_ci:.2f} gCO₂e/MJ")

    if solar_itc:
        solar_capex *= 0.70
    total_capex = sum([solar_capex, dryer_capex, chp_capex, boiler_capex, ccs_capex])
    st.metric("Total CapEx", f"${total_capex:,.0f}")

with tab2:
    st.title("📘 Calculation Breakdown")

    st.markdown("""
### CI Calculation Formula:
```
Final CI = Baseline CI - (Solar CI + Dryer CI + CHP CI + Boiler CI + CCS CI)
           + NG Penalty - RNG Benefit
```

### Tons CO₂ Avoided:
```
Tons = (Baseline CI - Final CI) × MGY × MJ/gal ÷ 1000
```

### Revenue:
```
LCFS = Tons × LCFS $/ton
45Q  = Tons × 45Q $/ton
```

### CapEx:
```
Solar ITC: Solar CapEx × 0.70 if applied
```

Editable version with full formulas will be added in next build.
""")

st.caption("CI Model v4.2 – Conestoga Energy | Full working logic")
