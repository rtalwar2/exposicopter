import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the folder where CSV files are stored
csv_folder = "draaitafel-processed-data"  # Change this if needed
output_folder = "polar_plots_draaitafel"  # Folder to save individual plots

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

# Dictionary to store processed data, grouped by frequency
data_dict = {}

# Read each CSV file and process the data
for file in csv_files:
    try:
        # Extract filename
        filename = os.path.basename(file)
        print(f"Processing: {filename}")

        # Extract frequency and source dBm from filename (Format: YYYY-MM-DD_HH-MM-SS_FREQ-dbM.csv)
        parts = filename.split("_")
        if len(parts) < 3:
            print(f"Skipping {file}: Incorrect filename format")
            continue
        
        freq_dbm = parts[-1].replace(".csv", "")  # e.g., "600mhz-15dbm"
        
        try:
            d = freq_dbm.split("-")  # e.g., "600mhz", "15dbm"
            frequency = d[-2]
            source_dbm=d[-1]
        except ValueError:
            print(f"Skipping {file}: Unable to extract frequency and dBm from {freq_dbm}")
            continue

        # Read CSV file into a DataFrame
        df = pd.read_csv(file)

        # Ensure correct column names exist
        required_columns = {"Second", "Average", "Min", "Max", "Median"}
        if required_columns.issubset(df.columns):
            # Convert "Second" to "Angle (°)" and then to Radians for polar plot
            df["Angle (°)"] = df["Second"] * 2  # 1 second = 2 degrees
            
            df_forward=df[df["Second"]<=180]
            df_backward=df[df["Second"]>181]

            df_backward["Angle (°)"]=720-df_backward["Angle (°)"]-2#compensate for missing second

            df_forward["Angle (rad)"] = np.radians(df_forward["Angle (°)"])  # Convert degrees to radians
            df_backward["Angle (rad)"] = np.radians(df_backward["Angle (°)"])  # Convert degrees to radians

            # df["Angle (rad)"] = np.radians(df["Angle (°)"])  # Convert degrees to radians

            # Store processed data in a nested dictionary grouped by frequency
            if frequency not in data_dict:
                data_dict[frequency] = {}

            data_dict[frequency][source_dbm] = {}
            data_dict[frequency][source_dbm]["forward"] = df_forward
            data_dict[frequency][source_dbm]["backward"] = df_backward
            

        else:
            print(f"Skipping {file}: Incorrect columns detected")

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Check if we have valid data to plot
if not data_dict:
    print("No valid CSV files found.")
    exit()

# Generate polar plots for each frequency
for frequency, dbm_data in data_dict.items():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={'projection': 'polar'})
    fig.suptitle(f"Polar Plot for {frequency.upper()}", fontsize=16)

    # Plot each dBm level
    for source_dbm, df_dict in dbm_data.items():
        for direction, df in df_dict.items():
            # Plot Average dBm
            axes[0].plot(df["Angle (rad)"], df["Average"], label=f"{source_dbm} {direction}", linewidth=1.5)

            # Plot Median dBm
            axes[1].plot(df["Angle (rad)"], df["Median"], label=f"{source_dbm} {direction}", linewidth=1.5)
        # break

    # Format the polar plots
    for ax, title in zip(axes, ["Average dBm", "Median dBm"]):
        ax.set_title(title)
        ax.set_theta_zero_location("S")  # 0° at the bottom
        ax.set_theta_direction(1)  # CounterClockwise
        ax.set_xticks(np.radians([0, 45, 90, 135, 180, 225, 270, 315]))  # Angle labels
        ax.set_xticklabels(["0°", "45°", "90°", "135°", "180°", "225°", "270°", "315°"])
        ax.set_ylim([-60, -15])  # Normalize limits
        ax.legend(title="Source Power", loc="upper right")

    # Save the plot
    output_filename = f"polar_plot_{frequency}.png"
    plt.savefig(os.path.join(output_folder, f"{output_filename}.png"))
    print(f"Saved polar plot: {output_filename}")

    # Uncomment to display the plots interactively
    # plt.show()
