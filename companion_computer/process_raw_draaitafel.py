import pandas as pd
import numpy as np
import os

# Define input and output directories
raw_data_folder = "draaitafel-raw-data"
processed_data_folder = "draaitafel-processed-data"

# Ensure the output folder exists
os.makedirs(processed_data_folder, exist_ok=True)

# Function to convert voltage to dBm
def voltage_to_dbm(voltage):
    if voltage > 2:
        return (2.0 / -0.025) + 20.0  # -60 dB
    elif voltage < 0.5:
        return (0.5 / -0.025) + 20.0  # 0 dB
    else:
        return (voltage / -0.025) + 20.0

# Function to convert dBm to Watt
def dbm_to_watt(dbm):
    return 10**(dbm / 10) / 1000

# Function to convert Watt to dBm
def watt_to_dbm(watt):
    return 10 * np.log10(watt * 1000)

# Process each CSV file in the raw-data folder
for filename in os.listdir(raw_data_folder):
    if filename.endswith(".csv"):
        input_csv = os.path.join(raw_data_folder, filename)
        output_csv = os.path.join(processed_data_folder, f"{filename[:-8]}.csv")

        # Read the CSV file
        df = pd.read_csv(input_csv)

        # Ensure the column names are correctly recognized
        df.columns = [col.strip() for col in df.columns]

        # Convert "Elapsed Time (s)" to integer seconds
        df["Second"] = df["Elapsed Time (s)"].astype(float).astype(int)

        # Convert voltage to dBm
        df["dBm"] = df["Value"].apply(voltage_to_dbm)

        # Convert dBm to Watt
        df["Watt"] = df["dBm"].apply(dbm_to_watt)

        # Group by second and calculate statistics
        aggregated_df = df.groupby("Second").agg(
            Average=("Watt", "mean"),  # Take the mean in Watt
            Min=("Watt", "min"),
            Max=("Watt", "max"),
            Median=("Watt", "median")
        ).reset_index()

        # Convert the Watt back to dBm
        aggregated_df["Average"] = aggregated_df["Average"].apply(watt_to_dbm)
        aggregated_df["Min"] = aggregated_df["Min"].apply(watt_to_dbm)
        aggregated_df["Max"] = aggregated_df["Max"].apply(watt_to_dbm)
        aggregated_df["Median"] = aggregated_df["Median"].apply(watt_to_dbm)

        # Save the processed data to a new CSV file
        aggregated_df.to_csv(output_csv, index=False)

        print(f"Processed data saved to {output_csv}")
