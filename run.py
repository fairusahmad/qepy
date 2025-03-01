import os
import subprocess
import streamlit as st

# Function to get the working directory
def get_working_directory():
    return os.getcwd()

# Function to run a command in a specific folder
def run_command(command, folder, parent_dir):
    folder_path = os.path.join(parent_dir, folder)  # Full path to subfolder

    # Check if the folder exists before running the command
    if not os.path.exists(folder_path):
        st.warning(f"⚠️ Folder {folder} not found in {parent_dir}, skipping...")
        return

    st.write(f"⚙️ Running: {command} in {folder} ...")
    
    process = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=folder_path)
    
    st.write(f"\n📂 Executed in {folder}: {command}")
    if process.stdout:
        st.success(f"✅ Standard Output:\n{process.stdout}")
    if process.stderr:
        st.error(f"❌ Error Output:\n{process.stderr}")

# Function to execute selected calculations
def execute_calculations(selected_tasks, parent_dir):
    any_task_run = False  # Track if any checkbox is selected
    folders = ["C-STO-00", "C-STO-20"]

    for folder in folders:
        # Filter selected tasks
        tasks_to_run = [cmd for checkbox, cmd in selected_tasks[folder] if checkbox]

        if tasks_to_run:
            any_task_run = True
            st.write(f"\n📂 Processing folder: {folder}")

            for command in tasks_to_run:
                run_command(command, folder, parent_dir)

    if not any_task_run:
        st.warning("⚠️ No calculations selected. Please choose at least one!")
    else:
        st.success("✅ All selected calculations are completed.")
