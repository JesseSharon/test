import math
import streamlit as st
import time
import pandas as pd
import plotly.express as px

# --- Hardware Options ---
gpu_options = {
    "NVIDIA GTX 1080 Ti": {"speed_hps": 1_000_000_000, "power_watts": 250, "cost_per_hour": 0.5},
    "NVIDIA RTX 3090": {"speed_hps": 3_500_000_000, "power_watts": 350, "cost_per_hour": 1.0},
    "AMD RX 6900 XT": {"speed_hps": 3_000_000_000, "power_watts": 300, "cost_per_hour": 0.8},
}

asic_options = {
    "AntMiner S19": {"speed_hps": 10_000_000_000, "power_watts": 1500, "cost_per_hour": 3},
    "WhatsMiner M30S++": {"speed_hps": 11_200_000_000, "power_watts": 3472, "cost_per_hour": 4},
}

cloud_vm_options = {
    "AWS p3.2xlarge": {"speed_hps": 500_000_000, "power_watts": 0, "cost_per_hour": 5},
    "Azure NC6": {"speed_hps": 600_000_000, "power_watts": 0, "cost_per_hour": 6},
    "Google Cloud A100": {"speed_hps": 700_000_000, "power_watts": 0, "cost_per_hour": 7},
}

electricity_cost_per_kwh = 0.10

# --- Helper Functions ---
def calculate_entropy(password):
    char_sets = 0
    if any(c.islower() for c in password): char_sets += 26
    if any(c.isupper() for c in password): char_sets += 26
    if any(c.isdigit() for c in password): char_sets += 10
    if any(c in "!@#$%^&*()-_=+[{]};:'\",<.>/?\\|" for c in password): char_sets += 32
    entropy = math.log2(char_sets) * len(password) if char_sets > 0 else 0
    return entropy

def estimate_guesses(entropy, method):
    if method == "Brute Force":
        return max(1, (2 ** entropy) / 2)
    elif method == "Dictionary Attack":
        return 100_000_000
    elif method == "Hybrid Attack":
        return 10_000_000_000
    else:
        return 2 ** entropy

def estimate_cracking_time_and_cost(password, hardware_choice, hardware_details, method):
    entropy = calculate_entropy(password)
    total_guesses = estimate_guesses(entropy, method)
    
    hashes_per_second = hardware_details["speed_hps"]
    if hashes_per_second <= 0:
        hashes_per_second = 1

    time_seconds = total_guesses / hashes_per_second
    time_hours = time_seconds / 3600

    compute_cost = time_hours * hardware_details["cost_per_hour"]

    energy_cost = 0
    if hardware_choice != "Cloud VM":
        energy_kwh = (hardware_details["power_watts"] * time_hours) / 1000
        energy_cost = energy_kwh * electricity_cost_per_kwh
    else:
        energy_kwh = 0

    total_cost = compute_cost + energy_cost
    return time_seconds, time_hours, total_cost, entropy, total_guesses, energy_kwh

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.2f} minutes"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.2f} hours"
    days = hours / 24
    if days < 365:
        return f"{days:.2f} days"
    years = days / 365
    return f"{years:.2f} years"

# --- App Layout ---
st.set_page_config(page_title="🔐 Password Cracking Cost Calculator", layout="centered")

st.markdown("<h1 style='text-align: center;'>🔐 Password Cracking Cost Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Estimate the time & cost to crack your password 💸</h4>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3064/3064197.png", width=100)
    st.title("🔧 Configuration")

    password = st.text_input("🔑 Enter your password:", type="password")

    method = st.radio("⚔️ Select Cracking Method", ("Brute Force", "Dictionary Attack", "Hybrid Attack"))

    hardware_category = st.selectbox("🖥️ Select Hardware Category", ("GPU", "ASIC", "Cloud VM", "Custom Rig"))

    if hardware_category == "GPU":
        hardware_list = list(gpu_options.keys())
        hardware_selected = st.selectbox("Select GPU", hardware_list)
        selected_hardware_specs = gpu_options[hardware_selected]

    elif hardware_category == "ASIC":
        hardware_list = list(asic_options.keys())
        hardware_selected = st.selectbox("Select ASIC", hardware_list)
        selected_hardware_specs = asic_options[hardware_selected]

    elif hardware_category == "Cloud VM":
        hardware_list = list(cloud_vm_options.keys())
        hardware_selected = st.selectbox("Select Cloud VM", hardware_list)
        selected_hardware_specs = cloud_vm_options[hardware_selected]

    elif hardware_category == "Custom Rig":
        st.markdown("### 🛠️ Enter Custom Hardware Specs")
        custom_speed = st.number_input("Hash rate (hashes/sec):", min_value=1.0, value=1_000_000_000.0)
        custom_power = st.number_input("Power consumption (watts):", min_value=0.0, value=300.0)
        custom_cost = st.number_input("Hourly compute cost ($):", min_value=0.0, value=1.0)

        hardware_selected = "Your Custom Rig"
        selected_hardware_specs = {
            "speed_hps": custom_speed,
            "power_watts": custom_power,
            "cost_per_hour": custom_cost
        }

st.markdown("## 📊 Results")

if st.button("🚀 Estimate Cracking Cost"):
    if not password:
        st.warning("⚠️ Please enter a password.")
    else:
        with st.spinner(f"🔍 Analyzing password using {method}..."):
            progress = st.progress(0)
            for percent in range(100):
                time.sleep(0.01)
                progress.progress(percent + 1)

            time_seconds, time_hours, total_crack_cost, entropy, total_guesses, energy_kwh = estimate_cracking_time_and_cost(
                password, hardware_category, selected_hardware_specs, method
            )

            formatted_time = format_time(time_seconds)

        st.success("✅ Analysis Complete!")

        # Show Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Entropy", f"{entropy:.2f} bits", help="Higher entropy = stronger password.")
        col2.metric("Guesses", f"{total_guesses:,.0f}", help="Number of guesses required.")
        col3.metric("Time to Crack", formatted_time)

        st.metric("💸 Estimated Total Cost", f"${total_crack_cost:.2f}")

        if hardware_category != "Cloud VM":
            st.metric("⚡ Energy Consumption", f"{energy_kwh:.2f} kWh")

        # Password strength bar
        st.markdown("### 🔋 Password Strength")
        strength_level = int(min(entropy / 1.28, 100))  # scale entropy for progress bar
        st.progress(strength_level)

        if entropy < 40:
            st.error("🔴 Very Weak Password! Increase length and complexity.")
        elif entropy < 60:
            st.warning("🟠 Moderate Password. Consider improving complexity.")
        else:
            st.success("🟢 Strong Password! Expensive and difficult to crack.")

        # Comparison Chart
        st.markdown("### 📈 Time Comparison Across Methods")

        methods = ["Brute Force", "Dictionary Attack", "Hybrid Attack"]
        times = []
        for m in methods:
            sec, _, _, _, _, _ = estimate_cracking_time_and_cost(password, hardware_category, selected_hardware_specs, m)
            times.append(sec / 3600)  # convert to hours

        df = pd.DataFrame({
            "Method": methods,
            "Time to Crack (hours)": times
        })

        fig = px.bar(df, x="Method", y="Time to Crack (hours)", color="Method", text_auto=".2s", height=400)
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>🔐 Made with ❤️ by YourName | Powered by Streamlit</p>", unsafe_allow_html=True)
