from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
import os
from fermi_dos import extract_fermi_energies, load_pdos, plot_pdos
from run import execute_calculations
from jinja2 import Template, FileSystemLoader, Environment

app = FastAPI()

# Load templates
env = Environment(loader=FileSystemLoader("templates"))

# Define folders
folders = ["C-STO-00", "C-STO-20"]

@app.get("/", response_class=HTMLResponse)
async def home():
    template = env.get_template("index.html")
    return template.render(directory=os.getcwd(), folders=folders)

@app.post("/set_directory/")
async def set_directory(directory: str = Form(...)):
    if os.path.isdir(directory):
        os.chdir(directory)
        return {"message": f"✅ Working directory set to: {directory}"}
    else:
        return {"error": "❌ Invalid directory. Please enter a correct path."}

@app.post("/run_calculations/")
async def run_calculations(tasks: dict):
    execute_calculations(tasks, os.getcwd())
    return {"message": "✅ Quantum ESPRESSO calculations executed successfully!"}

@app.post("/extract_fermi/")
async def extract_fermi(selected_scf_files: dict):
    if all(selected_scf_files.values()):
        fermi_energies = extract_fermi_energies(selected_scf_files)
        return {"fermi_energies": fermi_energies}
    else:
        return {"error": "❌ Please provide valid SCF file paths for all folders."}

@app.post("/plot_pdos/")
async def plot_pdos_endpoint(save_pdf: bool = Form(False)):
    directory = os.getcwd()
    fermi_energies = extract_fermi_energies({folder: f"{directory}/{folder}/scf_output.txt" for folder in folders})
    if fermi_energies:
        df1 = load_pdos(directory, "C-STO-00", fermi_energies.get("C-STO-00"))
        df2 = load_pdos(directory, "C-STO-20", fermi_energies.get("C-STO-20"))
        plot_pdos(df1, df2, "C-STO-00", "C-STO-20", directory, save_pdf=save_pdf)
        return {"message": "✅ PDOS plot generated!"}
    else:
        return {"error": "❌ Please extract Fermi energy before plotting PDOS."}
