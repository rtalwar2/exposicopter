import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Define the folder where CSV files are stored
csv_folder = "draaitafel-processed-data"  # Change this if needed

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
            frequency, source_dbm = freq_dbm.split("-")  # e.g., "600mhz", "15dbm"
        except ValueError:
            print(f"Skipping {file}: Unable to extract frequency and dBm from {freq_dbm}")
            continue

        # Read CSV file into a DataFrame
        df = pd.read_csv(file)

        # Ensure correct column names exist
        required_columns = {"Second", "Average", "Min", "Max", "Median"}
        if required_columns.issubset(df.columns):
            # Convert "Second" to "Angle (°)"
            df["Angle (°)"] = df["Second"] * 2  # 1 second = 2 degrees

            # Store processed data in a nested dictionary grouped by frequency
            if frequency not in data_dict:
                data_dict[frequency] = {}

            data_dict[frequency][source_dbm] = df

        else:
            print(f"Skipping {file}: Incorrect columns detected")

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Check if we have valid data to plot
if not data_dict:
    print("No valid CSV files found.")
    exit()

# Predefined angles for vertical red lines
vertical_lines = [0, 45, 90, 135, 180, 225, 270, 315]

# Generate plots for each frequency
for frequency, dbm_data in data_dict.items():
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)  # Two subplots, same x-axis
    fig.suptitle(f"Sensor Data for {frequency.upper()} (dBm vs Angle)", fontsize=16)

    # Top subplot: Average dBm
    axes[0].set_title("Average dBm")
    axes[0].set_ylabel("dBm")
    for source_dbm, df in dbm_data.items():
        axes[0].plot(df["Angle (°)"], df["Average"], label=f"{source_dbm}", linewidth=1.5)

    # Add vertical red lines with labels
    for angle in vertical_lines:
        axes[0].axvline(x=angle, color="red", linestyle="--", linewidth=1)
        axes[0].text(angle, axes[0].get_ylim()[1], f"{angle}°", color="red", 
                     ha="center", va="bottom", fontsize=10, fontweight="bold")

    axes[0].set_ylim([-60, -15])

    axes[0].legend(title="Source Power")
    axes[0].grid(True)

    # Bottom subplot: Median dBm
    axes[1].set_ylim([-60, -15])

    axes[1].set_title("Median dBm")
    axes[1].set_xlabel("Angle (°)")
    axes[1].set_ylabel("dBm")
    for source_dbm, df in dbm_data.items():
        axes[1].plot(df["Angle (°)"], df["Median"], label=f"{source_dbm}", linewidth=1.5)

    # Add vertical red lines with labels
    for angle in vertical_lines:
        axes[1].axvline(x=angle, color="red", linestyle="--", linewidth=1)
        axes[1].text(angle, axes[1].get_ylim()[1], f"{angle}°", color="red", 
                     ha="center", va="bottom", fontsize=10, fontweight="bold")

    axes[1].legend(title="Source Power")
    axes[1].grid(True)

    # Adjust layout and save plot
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_filename = f"draaitafel_{frequency}.png"
    plt.savefig(output_filename)
    print(f"Saved plot: {output_filename}")

    # Uncomment below to show plots interactively
    # plt.show()
