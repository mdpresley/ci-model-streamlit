
import streamlit as st

def calculate_ci_model(inputs):
    baseline_ci = 65

    ci_reductions = {
        'solar': -inputs['solar_ci'] * (inputs['solar_pct'] / 100),
        'dryer': -inputs['dryer_ci'] * (inputs['dryer_pct'] / 100),
        'chp': -inputs['chp_ci'] * (inputs['chp_pct'] / 100),
        'boiler_elec': -inputs['boiler_ci'] * (inputs['boiler_pct'] / 100),
        'ccs': inputs['ccs_ci']
    }

    total_ci = baseline_ci + sum(ci_reductions.values())
    tons_co2_avoided = (baseline_ci - total_ci) * inputs['capacity_mgy'] * 3780 / 1000

    lcfs_revenue = tons_co2_avoided * inputs['lcfs_price']
    q45_revenue = tons_co2_avoided * inputs['q45_price']
    total_revenue = lcfs_revenue + q45_revenue

    annual_demand_charge = inputs['monthly_demand_charge'] * 12
    demand_savings = annual_demand_charge * (inputs['solar_pct'] / 100) * (inputs['demand_reduction_pct'] / 100)

    capex = {
        'solar': inputs['solar_cost_per_kw'] * inputs['solar_kw'] / 100,
        'dryer': inputs['dryer_cost_per_unit'] * inputs['dryer_units'],
        'chp': inputs['chp_cost_per_mmbtu'] * inputs['chp_mmbtu'],
        'boiler_elec': inputs['boiler_cost_per_mmbtu'] * inputs['boiler_mmbtu'],
        'ccs': inputs['ccs_capex']
    }

    total_capex = sum(capex.values())
    total_opex = total_capex * (inputs['opex_pct'] / 100)
    total_cost = total_capex + total_opex - demand_savings

    payback = total_cost / total_revenue if total_revenue > 0 else float('inf')
    abatement_cost = total_cost / tons_co2_avoided if tons_co2_avoided > 0 else float('inf')

    return {
        'CI': total_ci,
        'Tons CO2': tons_co2_avoided,
        'LCFS': lcfs_revenue,
        '45Q': q45_revenue,
        'Revenue': total_revenue,
        'CapEx': total_capex,
        'OpEx': total_opex,
        'Demand Savings': demand_savings,
        'Total Cost': total_cost,
        'Payback': payback,
        'Abatement Cost': abatement_cost
    }

st.title("Ethanol Plant CI Model – v3")

plant = st.selectbox("Select Plant", ["Arkalon (110 MGY)", "Bonanza (65 MGY)"])
capacity = 110 if "Arkalon" in plant else 65

st.header("Utility (CMS)")
monthly_demand_charge = st.number_input("Monthly CMS Demand Charge ($)", value=50000)
demand_reduction_pct = st.slider("Solar Impact on Demand Charge (%)", 0, 100, 50)

st.header("Solar")
solar_pct = st.slider("Solar Adoption (%)", 0, 100, 50)
solar_ci = st.number_input("CI Reduction from Solar (gCO₂e/MJ)", value=0.25)
solar_cost_per_kw = st.number_input("Cost per kW installed ($)", value=1500)
solar_kw = st.number_input("Installed Solar Capacity (kW)", value=3000)

st.header("Electric Dryers")
dryer_pct = st.slider("Dryer Conversion (%)", 0, 100, 100)
dryer_ci = st.number_input("CI Reduction from Dryers (gCO₂e/MJ)", value=0.1)
dryer_cost_per_unit = st.number_input("Cost per Dryer ($)", value=750000)
dryer_units = st.number_input("Number of Dryers", value=4)

st.header("CHP")
chp_pct = st.slider("CHP Usage (%)", 0, 100, 80)
chp_ci = st.number_input("CI Reduction from CHP (gCO₂e/MJ)", value=0.15)
chp_cost_per_mmbtu = st.number_input("Cost per MMBtu/hr CHP Capacity ($)", value=150000)
chp_mmbtu = st.number_input("CHP Capacity (MMBtu/hr)", value=50)

st.header("Boiler Electrification")
boiler_pct = st.slider("Boiler Electrification (%)", 0, 100, 40)
boiler_ci = st.number_input("CI Reduction from Boilers (gCO₂e/MJ)", value=0.12)
boiler_cost_per_mmbtu = st.number_input("Cost per MMBtu/hr Boiler Capacity ($)", value=100000)
boiler_mmbtu = st.number_input("Electrified Boiler Capacity (MMBtu/hr)", value=30)

st.header("Carbon Capture")
ccs_ci = st.number_input("CI Reduction from CCS (gCO₂e/MJ)", value=-25.0)
ccs_capex = st.number_input("CCS CapEx ($)", value=20000000)

st.header("Financial Assumptions")
opex_pct = st.number_input("Annual O&M (% of CapEx)", value=3.0)
lcfs_price = st.number_input("LCFS Credit ($/ton)", value=125)
q45_price = st.number_input("45Q Credit ($/ton)", value=85)

if st.button("Calculate CI & Economics"):
    result = calculate_ci_model({
        'capacity_mgy': capacity,
        'solar_pct': solar_pct,
        'solar_ci': solar_ci,
        'solar_cost_per_kw': solar_cost_per_kw,
        'solar_kw': solar_kw,
        'dryer_pct': dryer_pct,
        'dryer_ci': dryer_ci,
        'dryer_cost_per_unit': dryer_cost_per_unit,
        'dryer_units': dryer_units,
        'chp_pct': chp_pct,
        'chp_ci': chp_ci,
        'chp_cost_per_mmbtu': chp_cost_per_mmbtu,
        'chp_mmbtu': chp_mmbtu,
        'boiler_pct': boiler_pct,
        'boiler_ci': boiler_ci,
        'boiler_cost_per_mmbtu': boiler_cost_per_mmbtu,
        'boiler_mmbtu': boiler_mmbtu,
        'ccs_ci': ccs_ci,
        'ccs_capex': ccs_capex,
        'opex_pct': opex_pct,
        'lcfs_price': lcfs_price,
        'q45_price': q45_price,
        'monthly_demand_charge': monthly_demand_charge,
        'demand_reduction_pct': demand_reduction_pct
    })

    st.subheader("Results")
    st.metric("Final CI Score", f"{result['CI']:.2f} gCO₂e/MJ")
    st.metric("Tons CO₂ Avoided", f"{result['Tons CO2']:,.0f}")
    st.metric("LCFS Revenue", f"${result['LCFS']:,.0f}")
    st.metric("45Q Revenue", f"${result['45Q']:,.0f}")
    st.metric("Total Revenue", f"${result['Revenue']:,.0f}")
    st.metric("Total CapEx", f"${result['CapEx']:,.0f}")
    st.metric("OpEx (Annual)", f"${result['OpEx']:,.0f}")
    st.metric("CMS Demand Savings", f"${result['Demand Savings']:,.0f}")
    st.metric("Total Cost (CapEx + OpEx - CMS Savings)", f"${result['Total Cost']:,.0f}")
    st.metric("Payback (yrs)", f"{result['Payback']:.2f}")
    st.metric("Cost per Ton CO₂ Avoided", f"${result['Abatement Cost']:,.2f}")
