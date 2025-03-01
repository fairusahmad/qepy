import streamlit as st
import os
from fermi_dos import extract_fermi_energies, load_pdos, plot_pdos
from run import execute_calculations, get_working_directory

# Streamlit app title
st.title("Quantum ESPRESSO Workflow with Streamlit")

# 1️⃣ Select Working Directory
st.subheader("1️⃣ Select Working Directory")

# Function to browse and list available folders
def folder_selector(base_path="."):
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    return st.selectbox("Select a working directory:", ["Enter manually..."] + folders)

# Allow user to enter or select a folder
base_path = os.getcwd()
selected_folder = folder_selector(base_path)
directory = st.text_input("Or enter the directory manually:", os.path.join(base_path, selected_folder if selected_folder != "Enter manually..." else ""))

# Set working directory
if st.button("Set Directory"):
    if os.path.isdir(directory):
        os.chdir(directory)
        st.success(f"✅ Working directory set to: {directory}")
    else:
        st.error("❌ Invalid directory. Please enter a valid path.")

# Define folders
folders = ["C-STO-00", "C-STO-20"]

# 2️⃣ Run Quantum ESPRESSO Calculations
st.subheader("2️⃣ Run Quantum ESPRESSO Calculations")

# Define calculation steps with checkboxes
task_options = {
    "run_relax": "mpirun -np 38 pw.x < input.pw_relax.x > output_relax.pw.x",
    "run_scf": "mpirun -np 38 pw.x < input.pw.x > output_scf.pw.x",
    "run_nscf": "mpirun -np 38 pw.x < nscf_input.pw.x > nscf_output.pw.x",
    "run_bands": "mpirun -np 38 pw.x < bands_input.pw.x > bands_output.pw.x",
    "run_bands_post": "mpirun -np 38 bands.x < bands_post_input.x > bands_post_output.x",
    "run_projwfc": "mpirun -np 38 projwfc.x < input.projwfc.x > projwfc.out",
    "run_potential_pp": "mpirun -np 38 pp.x <potential_pp.in> potential_pp.out",
    "run_potential_average": "average.x <potential_average.in> potential_average.out",
    "run_phonon": "mpirun -np 38 ph.x < ph.in > ph.out",
    "run_q2r": "mpirun -np 38 q2r.x < q2r.in > q2r.out",
    "run_matdyn": "mpirun -np 38 matdyn.x < matdyn.in > matdyn.out",
    "run_plotband": "plotband.x <plotband.in> plotband.out",
}

# Create a dictionary to store selected tasks
selected_tasks = {folder: [] for folder in folders}

# Arrange folder settings in two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 C-STO-00 Settings")
    for task, command in task_options.items():
        checkbox = st.checkbox(f"{task.replace('_', ' ').title()}", key=f"{task}_C-STO-00")
        selected_tasks["C-STO-00"].append((checkbox, command))

with col2:
    st.subheader("📂 C-STO-20 Settings")
    for task, command in task_options.items():
        checkbox = st.checkbox(f"{task.replace('_', ' ').title()}", key=f"{task}_C-STO-20")
        selected_tasks["C-STO-20"].append((checkbox, command))

# Execute button
st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
if st.button("Run Selected Steps"):
    execute_calculations(selected_tasks, directory)

# 3️⃣ Select SCF Output Files for Fermi Energy Extraction
st.subheader("3️⃣ Select SCF Output Files for Fermi Energy Extraction")

# File selection function for SCF output
def file_selector(folder_path):
    if os.path.isdir(folder_path):
        filenames = [f for f in os.listdir(folder_path) if f.endswith('.txt') or f.endswith('.out')]
        if filenames:
            selected_filename = st.selectbox(f"Select SCF file for {os.path.basename(folder_path)}", filenames)
            return os.path.join(folder_path, selected_filename)
        else:
            st.warning(f"No SCF files found in {folder_path}")
            return None
    else:
        st.error(f"Folder {folder_path} does not exist.")
        return None

# User selects SCF files for Fermi energy extraction
selected_scf_files = {folder: file_selector(os.path.join(directory, folder)) for folder in folders}

# Fermi energy extraction button
if st.button("Extract Fermi Energies"):
    if all(selected_scf_files.values()):
        fermi_energies = extract_fermi_energies(selected_scf_files)
    else:
        st.error("Please select SCF output files for all folders.")

# 4️⃣ Plot Projected Density of States (PDOS)
st.subheader("4️⃣ Plot Projected Density of States (PDOS)")

# Checkbox to enable saving as PDF
save_pdf = st.checkbox("Save as PDF")

# Button to generate PDOS plot
if st.button("Generate PDOS Plot"):
    if all(selected_scf_files.values()):
        fermi_energies = extract_fermi_energies(selected_scf_files)
        if fermi_energies:
            df1 = load_pdos(directory, "C-STO-00", fermi_energies.get("C-STO-00"))
            df2 = load_pdos(directory, "C-STO-20", fermi_energies.get("C-STO-20"))
            plot_pdos(df1, df2, "C-STO-00", "C-STO-20", directory, save_pdf=save_pdf)
    else:
        st.error("Please select SCF output files before plotting PDOS.")
