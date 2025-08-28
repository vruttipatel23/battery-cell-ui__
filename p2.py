import random

list_of_cell = []
for i in range(0, 8):
    list_of_cell.append(input(f"Enter your cell type #{i+1} (e.g., lfp/nmc): ").strip().lower())
print("\nList of entered cell types:", list_of_cell)

cells_data = {}

for idx, cell_type in enumerate(list_of_cell, start=1):
    cell_key = f"cell_{idx}_{cell_type}"
    
    
    voltage = 3.2 if cell_type == "lfp" else 3.6
    min_voltage = 2.8 if cell_type == "lfp" else 3.2
    max_voltage = 3.6 if cell_type == "lfp" else 4.0
    current = 0.0
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * current, 2)

    cells_data[cell_key] = {
        "voltage": voltage,
        "current": current,
        "temp": temp,
        "capacity": capacity,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage
    } 
print(cells_data)