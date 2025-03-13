import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Define the folder where CSV files are stored
csv_folder = "raw-data"  # Change this if needed
output_folder = "raw-plots"  # Folder to save individual plots

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

# Function to convert voltage to dBm
def voltage_to_dbm(voltage):
    if voltage > 2:
        return (2.0 / -0.025) + 20.0  # -60 dB
    elif voltage < 0.5:
        return (0.5 / -0.025) + 20.0  # 0 dB
    else:
        return (voltage / -0.025) + 20.0

# Initialize combined plot
plt.figure(figsize=(12, 6))  # Adjust size as needed
plt.title("Sensor Data (dBm) - Combined")
plt.xlabel("Elapsed Time (s)")
plt.ylabel("dBm")

# Read each CSV file and plot the data
for file in csv_files:
    try:
        # Extract filename (without extension) for labeling
        filename = os.path.basename(file).replace(".csv", "")
        custom_param = filename.split("_")[-1].replace(".csv", "")

        # Read CSV file into a DataFrame
        df = pd.read_csv(file)

        # Ensure correct columns exist
        if {"Elapsed Time (s)", "Value"}.issubset(df.columns):
            # Convert values
            df["dBm"] = df["Value"].apply(voltage_to_dbm)

            # Add to combined plot
            plt.plot(df["Elapsed Time (s)"], df["dBm"], label=custom_param, linewidth=0.5)

            # Generate individual plot
            plt.figure(figsize=(10, 5))
            plt.plot(df["Elapsed Time (s)"], df["dBm"], label=custom_param, linewidth=0.5)
            plt.xlabel("Elapsed Time (s)")
            plt.ylabel("dBm")
            plt.title(f"Sensor Data (dBm) - {custom_param}")
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(output_folder, f"{filename}.png"))
            plt.close()  # Close the individual figure to save memory

        else:
            print(f"Skipping {file}: Incorrect columns detected")

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Save combined plot
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "combined_sensor_data_plot.png"))
plt.show()
