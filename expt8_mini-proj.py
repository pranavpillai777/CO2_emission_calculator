import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import io
import tempfile
import math
from datetime import datetime
import os 

# --- 1. Data Definitions ---
co2_factors = {
    # NOTE: These factors are highly variable. Using these is for demonstration only.
    "Electricity (kWh)": 0.85,
    "Petrol (liters)": 2.31,
    "Diesel (liters)": 2.68,
    "Car Travel (km)": 0.21,
    "Bus Travel (km)": 0.11,
    "Train Travel (km)": 0.05,
    "Air Travel (km)": 0.18,
    "Gas Consumption (m3)": 2.0,
    "Industrial Processes (tons of material)": 1000.0 
}

state_tree_co2_data = {
    "Maharashtra": {"plant": "Neem", "peak_age": 10, "co2_absorbed": 31.82},
    "Karnataka": {"plant": "Mango", "peak_age": 12, "co2_absorbed": 28.5},
    "Delhi": {"plant": "Peepal", "peak_age": 15, "co2_absorbed": 22.0},
    "Uttar Pradesh": {"plant": "Banyan", "peak_age": 20, "co2_absorbed": 45.0},
    "West Bengal": {"plant": "Coconut", "peak_age": 8, "co2_absorbed": 18.5},
    "Tamil Nadu": {"plant": "Tamarind", "peak_age": 14, "co2_absorbed": 25.0},
    "Gujarat": {"plant": "Mahua", "peak_age": 11, "co2_absorbed": 30.5},
    "Rajasthan": {"plant": "Khejri", "peak_age": 10, "co2_absorbed": 15.0},
    "Kerala": {"plant": "Jackfruit", "peak_age": 13, "co2_absorbed": 26.0},
    "Punjab": {"plant": "Sheesham", "peak_age": 16, "co2_absorbed": 33.0},
    "Andhra Pradesh": {"plant": "Mango", "peak_age": 12, "co2_absorbed": 28.5},
    "Telangana": {"plant": "Neem", "peak_age": 10, "co2_absorbed": 31.82},
    "Bihar": {"plant": "Peepal", "peak_age": 15, "co2_absorbed": 22.0},
    "Assam": {"plant": "Sal", "peak_age": 18, "co2_absorbed": 38.0},
    "Odisha": {"plant": "Banyan", "peak_age": 20, "co2_absorbed": 45.0},
    "Madhya Pradesh": {"plant": "Teak", "peak_age": 17, "co2_absorbed": 40.0},
    "Haryana": {"plant": "Khejri", "peak_age": 10, "co2_absorbed": 15.0},
    "Himachal Pradesh": {"plant": "Deodar", "peak_age": 25, "co2_absorbed": 50.0},
    "Jammu and Kashmir": {"plant": "Chinar", "peak_age": 30, "co2_absorbed": 55.0},
    "Jharkhand": {"plant": "Sal", "peak_age": 18, "co2_absorbed": 38.0},
    "Uttarakhand": {"plant": "Deodar", "peak_age": 25, "co2_absorbed": 50.0},
    "Chhattisgarh": {"plant": "Teak", "peak_age": 17, "co2_absorbed": 40.0},
    "Goa": {"plant": "Coconut", "peak_age": 8, "co2_absorbed": 18.5},
    "Meghalaya": {"plant": "Pine", "peak_age": 22, "co2_absorbed": 42.0},
    "Manipur": {"plant": "Pine", "peak_age": 22, "co2_absorbed": 42.0},
    "Tripura": {"plant": "Bamboo", "peak_age": 5, "co2_absorbed": 10.0},
    "Mizoram": {"plant": "Bamboo", "peak_age": 5, "co2_absorbed": 10.0},
    "Nagaland": {"plant": "Pine", "peak_age": 22, "co2_absorbed": 42.0},
    "Sikkim": {"plant": "Rhododendron", "peak_age": 15, "co2_absorbed": 20.0},
    "Arunachal Pradesh": {"plant": "Sal", "peak_age": 18, "co2_absorbed": 38.0},
    "Andaman and Nicobar Islands": {"plant": "Coconut", "peak_age": 8, "co2_absorbed": 18.5},
    "Chandigarh": {"plant": "Peepal", "peak_age": 15, "co2_absorbed": 22.0},
    "Dadra and Nagar Haveli and Daman and Diu": {"plant": "Teak", "peak_age": 17, "co2_absorbed": 40.0},
    "Lakshadweep": {"plant": "Coconut", "peak_age": 8, "co2_absorbed": 18.5},
    "Puducherry": {"plant": "Tamarind", "peak_age": 14, "co2_absorbed": 25.0},
    "Ladakh": {"plant": "Willow", "peak_age": 10, "co2_absorbed": 12.0}
}

STATES_UT_LIST = sorted(state_tree_co2_data.keys())

# --- Gauge Logic based on CO2 Mass (kg) vs. Benchmark ---
MAX_GAUGE_KG = 50000 

co2_mass_ranges = [
    (0, 5000, "Excellent (Pioneer)", "green"),
    (5000, 15000, "Good (Standard)", "lime"),
    (15000, 30000, "Fair (Improvement Needed)", "orange"),
    (30000, MAX_GAUGE_KG, "Poor (High Risk)", "red")
]

uploaded_data = None
gauge_buffer = None 

# --- 2. Core Functions ---

def calculate_emissions(df):
    emissions_df = df.copy()
    emissions_df['CO2_Emission_kg'] = emissions_df.apply(
        lambda row: row['Amount'] * co2_factors.get(row['Source'], 0), axis=1
    )
    co2_per_source = emissions_df.groupby('Source')['CO2_Emission_kg'].sum().reset_index()
    total_co2 = co2_per_source['CO2_Emission_kg'].sum()
    return total_co2, co2_per_source[co2_per_source['CO2_Emission_kg'] > 0]

def generate_gauge(total_co2_kg):
    """Generates a gauge comparing total CO2 mass against performance benchmarks."""
    
    display_co2 = min(total_co2_kg, MAX_GAUGE_KG) 
    
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis('off')
    start_angle = 180
    radius = 1.0
    
    # 1. Plot the colored wedges based on mass thresholds
    for low, high, label, color in co2_mass_ranges:
        theta1 = start_angle - (low / MAX_GAUGE_KG) * 180
        theta2 = start_angle - (high / MAX_GAUGE_KG) * 180
        
        wedge = plt.matplotlib.patches.Wedge((0, 0), radius, theta2, theta1, facecolor=color, edgecolor='white')
        ax.add_patch(wedge)
        
        label_angle = (theta1 + theta2) / 2
        label_rad = math.radians(label_angle)
        ax.text(0.9 * radius * math.cos(label_rad), 0.9 * radius * math.sin(label_rad), 
                label, rotation=-(180 - label_angle), ha='center', va='center', fontsize=7)
    
    # 2. Plot the pointer based on the company's total CO2
    pointer_angle = start_angle - (display_co2 / MAX_GAUGE_KG) * 180
    pointer_rad = math.radians(pointer_angle)
    
    ax.plot([0, 0.85 * radius * math.cos(pointer_rad)], 
            [0, 0.85 * radius * math.sin(pointer_rad)], color='black', linewidth=3)
    
    # 3. Display the final calculated CO2 mass in the center
    ax.text(0, -0.2, f"{total_co2_kg:,.0f} kg CO2", ha='center', va='center', fontsize=12, fontweight='bold')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.2, 1.1)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_pdf_report(state_name, total_co2, co2_per_source, trees_required, state_data, gauge_buffer):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Annual Carbon Offset Report", 0, 1, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 7, f"Region: {state_name}", 0, 1)
    pdf.cell(0, 7, f"Report Year: {datetime.now().year}-{datetime.now().year+1}",0,1)
    pdf.cell(0,7,f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",0,1)
    pdf.ln(5)
    
    # I. Summary
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0,10,"I. Summary of Carbon Footprint",0,1)
    pdf.set_font("Arial","",12)
    pdf.cell(0,7,f"Total CO2 Emitted: {total_co2:,.2f} kg",0,1)
    pdf.ln(3)
    
    # II. Carbon Offset Requirement
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"II. Carbon Offset Requirement",0,1)
    pdf.set_font("Arial","",12)
    pdf.cell(0,7,f"Tree Species: {state_data['plant']}",0,1)
    pdf.cell(0,7,f"Peak Absorption Age of {state_data['plant']}: {state_data['peak_age']} years",0,1)
    pdf.cell(0,7,f"Annual CO2 Absorption per tree: {state_data['co2_absorbed']} kg/year",0,1)
    pdf.cell(0,7,f"Number of Trees Required: {trees_required:,.0f}",0,1)
    pdf.ln(5)
    
    # III. CO2 Emissions per Source
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"III. CO2 Emissions per Source",0,1)
    pdf.set_font("Arial","B",10)
    col_width = 70
    pdf.cell(col_width,7,"Source",1,0,"C")
    pdf.cell(col_width,7,"CO2 Emission (kg)",1,1,"C")
    pdf.set_font("Arial","",10)
    for _, row in co2_per_source.iterrows():
        pdf.cell(col_width,7,row['Source'],1,0)
        pdf.cell(col_width,7,f"{row['CO2_Emission_kg']:,.2f}",1,1,"R")
    pdf.ln(5)

    # IV. Benchmark Gauge (Visualization)
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"IV. Benchmark Gauge (Performance)",0,1)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_gauge:
        tmp_gauge.write(gauge_buffer.getbuffer())
        tmp_gauge_name = tmp_gauge.name 
    
    pdf.image(tmp_gauge_name, x=40, y=pdf.get_y(), w=130)
    os.remove(tmp_gauge_name) 
    pdf.ln(75)

    # V. Carbon Offset Info 
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"V. Carbon Offset Info for Businesses",0,1)
    pdf.set_font("Arial","",12)
    info_text = (
        "Carbon offsets can potentially be tax deductible for businesses if purchased from qualified non-profits.\n"
        "Businesses can invest directly, purchase future contracts, or buy spot credits.\n"
        "Prices vary by project type and location, typically $5-15 per ton of CO2."
    )
    pdf.multi_cell(0,7,info_text)
    pdf.ln(5)
    
    # VI. Conclusion and Offset Recommendation (FIXED for variable safety)
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"VI. Conclusion and Offset Recommendation",0,1)
    pdf.set_font("Arial","",12)
    
    conclusion_text = (
        # Check: total_co2 variable is correctly used here.
        f"Your organization's total annual CO2 emissions are **{total_co2:,.2f} kg**. "
        f"To achieve a carbon-neutral footprint, we suggest planting indigenous species based on your selected region, {state_name}.\n\n"
        f"Recommendation:\n"
        f"- **Species:** {state_data['plant']} (Peak absorption at {state_data['peak_age']} years)\n"
        f"- **Trees Required:** **{trees_required:,.0f}** trees."
    )
    pdf.multi_cell(0,7,conclusion_text)
    
    pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
    if pdf_filename:
        pdf.output(pdf_filename)
        return True, pdf_filename
    return False,""

# --- 3. GUI Handlers ---
def select_file():
    global uploaded_data
    file_path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
    if not file_path:
        return
    try:
        df = pd.read_csv(file_path)
        if not all(col in df.columns for col in ['Source','Amount']):
            messagebox.showerror("CSV Error","CSV must contain 'Source' and 'Amount' columns.")
            uploaded_data = None
            return
        uploaded_data = df
        file_label.config(text=f"Selected: {file_path.split('/')[-1]}")
        preview_data(uploaded_data)
        confirm_btn.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("File Error",f"Error reading CSV: {e}")
        file_label.config(text="No CSV file selected.")
        uploaded_data = None
        confirm_btn.config(state=tk.DISABLED)

def preview_data(df):
    for item in preview_tree.get_children():
        preview_tree.delete(item)
    preview_tree["columns"] = list(df.columns)
    preview_tree["show"] = "headings"
    for col in df.columns:
        preview_tree.heading(col,text=col)
        preview_tree.column(col,width=100,anchor='center')
    for _,row in df.head(15).iterrows():
        preview_tree.insert("", "end", values=list(row))

def calculate():
    global uploaded_data, gauge_buffer
    if uploaded_data is None:
        messagebox.showerror("Input Error","Please select a valid CSV file first.")
        return
    state_name = state_combobox.get().strip()
    if state_name not in state_tree_co2_data:
        messagebox.showerror("Input Error","Please select a valid State/UT.")
        return
    try:
        total_co2,total_per_source = calculate_emissions(uploaded_data)
        if total_co2==0:
            messagebox.showinfo("Result","Total $\text{CO}_2$ emission is zero.")
            return
        state_data = state_tree_co2_data[state_name]
        trees_required = total_co2/state_data['co2_absorbed']
        
        gauge_buffer = generate_gauge(total_co2) 
        
        success, filename = generate_pdf_report(state_name, total_co2, total_per_source, trees_required, state_data, gauge_buffer)
        if success:
            messagebox.showinfo("Success",f"PDF generated:\n{filename}")
    except Exception as e:
        messagebox.showerror("Calculation Error",f"{e}")

# --- 4. GUI Setup ---
root = tk.Tk()
root.title("Carbon Offset Calculator")
root.geometry("850x800")
main_frame = ttk.Frame(root,padding="10")
main_frame.pack(fill='both',expand=True)

input_frame = ttk.LabelFrame(main_frame,text="Input Data",padding="10")
input_frame.pack(fill='x', pady=10)
ttk.Label(input_frame,text="Select/Type State/UT:").grid(row=0,column=0,padx=5,pady=5,sticky='w')
state_combobox = ttk.Combobox(input_frame,values=STATES_UT_LIST,width=40)
state_combobox.grid(row=0,column=1,padx=5,pady=5,sticky='ew')
state_combobox.set("Select State/UT")
file_label = ttk.Label(input_frame,text="No CSV file selected.")
file_label.grid(row=1,column=0,padx=5,pady=5,sticky='w')
select_file_btn = ttk.Button(input_frame,text="Select CSV File",command=select_file)
select_file_btn.grid(row=1,column=1,padx=5,pady=5,sticky='ew')

preview_frame = ttk.LabelFrame(main_frame,text="CSV Data Preview (First 15 Rows)",padding="10")
preview_frame.pack(fill='both',expand=True,pady=10)
preview_tree = ttk.Treeview(preview_frame,show="headings")
preview_tree.pack(fill='both',expand=True)

confirm_btn = ttk.Button(main_frame,text="Generate PDF Report",command=calculate,state=tk.DISABLED)
confirm_btn.pack(pady=15)

root.mainloop()