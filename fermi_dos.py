import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import streamlit as st

# Define function to extract Fermi energy
def get_fermi_energy(output_file):
    try:
        with open(output_file, "r") as file:
            lines = file.readlines()  # Read all lines
            for line in reversed(lines):
                match = re.search(r"the Fermi energy is\s+([-]?\d+\.\d+)\s+ev", line, re.IGNORECASE)
                if match:
                    return float(match.group(1))
    except FileNotFoundError:
        st.error(f"❌ Error: File not found - {output_file}")
    return None

# Function to extract Fermi energy from SCF output files
def extract_fermi_energies(directory, folders):
    fermi_energies = {}
    for folder in folders:
        file_path = os.path.join(directory, folder, "scf_output.txt")  # Change if needed
        fermi_energy = get_fermi_energy(file_path)
        if fermi_energy is not None:
            fermi_energies[folder] = fermi_energy
            st.success(f"✅ {folder}: Fermi Energy = {fermi_energy} eV")
        else:
            st.warning(f"⚠️ {folder}: Fermi Energy not found.")

    # Save results to a text file
    output_file = os.path.join(directory, "fermi_energies.txt")
    with open(output_file, "w") as f:
        for folder, energy in fermi_energies.items():
            f.write(f"{folder}: {energy} eV\n")
    
    st.success(f"✅ Extraction completed. Results saved in '{output_file}'")
    return fermi_energies

# Function to load and shift PDOS data
def load_pdos(directory, folder, fermi_energy, pdos_filename="VLAB.pdos_tot"):
    file_path = os.path.join(directory, folder, pdos_filename)
    if not os.path.exists(file_path):
        st.warning(f"⚠️ PDOS file not found in {folder}: {file_path}")
        return None
    df = pd.read_csv(file_path, delim_whitespace=True, comment="#", names=["Energy (eV)", "DOS", "PDOS"])
    df["Energy (eV)"] -= fermi_energy  # Shift energy by Fermi level
    return df

# Function to plot and optionally save PDOS
def plot_pdos(df1, df2, folder1, folder2, directory, energy_range=(-4, 4), save_pdf=False):
    if df1 is None or df2 is None:
        st.error("❌ Error: Missing PDOS data. Please check file paths.")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    df1_filtered = df1[(df1["Energy (eV)"] >= energy_range[0]) & (df1["Energy (eV)"] <= energy_range[1])]
    df2_filtered = df2[(df2["Energy (eV)"] >= energy_range[0]) & (df2["Energy (eV)"] <= energy_range[1])]

    ax.plot(df1_filtered["Energy (eV)"], df1_filtered["PDOS"], label=folder1, linestyle="dashed", color="blue")
    ax.plot(df2_filtered["Energy (eV)"], df2_filtered["PDOS"], label=folder2, color="red")

    ax.set_xlabel("Energy - $E_F$ (eV)")
    ax.set_ylabel("Projected Density of States (PDOS)")
    ax.set_title("Projected DOS Comparison (Shifted by $E_F$)")
    ax.set_xlim(energy_range)
    ax.axhline(0, color="black", linewidth=0.5, linestyle="dotted")
    ax.axvline(0, color="black", linewidth=1, linestyle="dotted", label="Fermi Level ($E_F$)")
    ax.legend()
    ax.grid()
    st.pyplot(fig)

    # Save to PDF if selected
    if save_pdf:
        pdf_filename = os.path.join(directory, "projected_dos.pdf")
        with PdfPages(pdf_filename) as pdf:
            fig.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
        st.success(f"✅ Plot saved as {pdf_filename}")
