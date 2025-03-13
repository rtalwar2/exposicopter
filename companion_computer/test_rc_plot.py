import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Define the folder where CSV files are stored
csv_folder = "processed-data"  # Change this if needed

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

# # Function to convert voltage to dBm
# def voltage_to_dbm(voltage):
#     if voltage > 2:
#         return (2.0 / -0.025) + 20.0  # -60 dB
#     elif voltage < 0.5:
#         return (0.5 / -0.025) + 20.0  # 0 dB
#     else:
#         return (voltage / -0.025) + 20.0

# Dictionary to store processed data
data_dict = {}
average_dbm_per_file = {}

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
            # Apply the mapping function to the numeric columns
            # df["Average"] = df["Average"].apply(voltage_to_dbm)
            # df["Min"] = df["Min"].apply(voltage_to_dbm)
            # df["Max"] = df["Max"].apply(voltage_to_dbm)
            # df["Median"] = df["Median"].apply(voltage_to_dbm)

            # Store processed data
            data_dict[custom_param] = df

            # Compute the average of the "Median" column and store it
            average_dbm_per_file[custom_param] = df["Average"].mean()

        else:
            print(f"Skipping {file}: Incorrect columns detected")

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Check if we have valid data to plot
if not data_dict:
    print("No valid CSV files found.")
    exit()

# Plot configuration (adding an extra row for the new subplot)
fig, axes = plt.subplots(3, 2, figsize=(24, 24))  # Increased figure size to fit the new plot
fig.suptitle("Sensor Data Comparison (dBm)", fontsize=16)

# Plot each metric
for custom_param, df in data_dict.items():
    axes[0, 0].plot(df["Average"], label=custom_param)
    axes[0, 1].plot(df["Min"], label=custom_param)
    axes[1, 0].plot(df["Max"], label=custom_param)
    axes[1, 1].plot(df["Median"], label=custom_param)

# Titles and legends
axes[0, 0].set_title("Average (dBm)")
axes[0, 1].set_title("Min (dBm)")
axes[1, 0].set_title("Max (dBm)")
axes[1, 1].set_title("Median (dBm)")

for ax in axes[:2, :].flat:  # Apply to the first 4 subplots
    ax.set_xlabel("Elapsed time (s)")
    ax.set_ylabel("dBm")
    ax.legend()

# New subplot for average of "Average" per file
for file_name, avg_value in average_dbm_per_file.items():
    # Determine color and marker based on filename
    color = "c"  # Default color
    marker = "o"  # Default marker (circle)
    linestyle = "solid"  # Default line style

    if "rc-on" in file_name:
        color = "r"  # Red for "rc-on"
    if "telem-on" in file_name:
        marker = "X"  # X marker for "telem-on"
        linestyle = "dotted"  # Dotted line for "telem-on"

    # Scatter plot point
    axes[2, 0].scatter(file_name, avg_value, color=color, marker=marker)
axes[2, 0].set_title("Average of 'Average' per CSV File (dBm)")
axes[2, 0].set_xlabel("CSV File")
axes[2, 0].set_ylabel("dBm")
axes[2, 0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels for readability

# Hide empty subplot in the bottom right (axes[2,1])
axes[2, 1].axis("off")

# Adjust layout and show plots
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("rc_average_dbm.png")
plt.show()
