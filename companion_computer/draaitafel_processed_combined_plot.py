import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Define the folder where CSV files are stored
csv_folder = "draaitafel-processed-data"  # Change this if needed

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

# Dictionary to store processed data
data_dict = {}

# Read each CSV file and process the data
for file in csv_files:
    try:
        # Extract custom_param from filename
        filename = os.path.basename(file)
        print(filename)
        custom_param = filename.split("_")[-1].replace(".csv", "")

        # Read CSV file into a DataFrame
        df = pd.read_csv(file)

        # Ensure correct column names exist
        required_columns = {"Second", "Average", "Min", "Max", "Median"}
        if required_columns.issubset(df.columns):
            # Convert "Second" to "Angle (°)"
            df["Angle (°)"] = df["Second"] * 2  # 1 second = 2 degrees

            # Store processed data
            data_dict[custom_param] = df

        else:
            print(f"Skipping {file}: Incorrect columns detected")

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Check if we have valid data to plot
if not data_dict:
    print("No valid CSV files found.")
    exit()

# Plot configuration
fig, axes = plt.subplots(2, 2, figsize=(24, 24))  # Increased figure size
fig.suptitle("Sensor Data Comparison (dBm) vs Angle", fontsize=16)

# Plot each metric with Angle (°) on the X-axis
for custom_param, df in data_dict.items():
    axes[0, 0].plot(df["Angle (°)"], df["Average"], label=custom_param)
    axes[0, 1].plot(df["Angle (°)"], df["Min"], label=custom_param)
    axes[1, 0].plot(df["Angle (°)"], df["Max"], label=custom_param)
    axes[1, 1].plot(df["Angle (°)"], df["Median"], label=custom_param)

# Titles and legends
axes[0, 0].set_title("Average (dBm)")
axes[0, 1].set_title("Min (dBm)")
axes[1, 0].set_title("Max (dBm)")
axes[1, 1].set_title("Median (dBm)")

for ax in axes.flat:  
    ax.set_xlabel("Angle (°)")  # X-axis label changed to Angle
    ax.set_ylabel("dBm")
    ax.legend()
    ax.grid(True)

# Adjust layout and save plot
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("draaitafel.png")
# plt.show()
