#########################"HELPER FUNCTIONS"###############################################
import os
from datetime import datetime
import csv
import time
import pandas as pd
import numpy as np
import math

def read_probe_raw_and_write_to_csv(broadband_probe):
    print("starting measurements")
    # Define the folder where CSV files should be saved
    raw_data_folder = "raw-flight-data"

    # Ensure the folder exists
    os.makedirs(raw_data_folder, exist_ok=True)

    # Generate CSV filename using current datetime + custom parameter
    custom_param = "rc-normal-telem-met-en-zonder-rc-niet-verplaatsen" + "-raw"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Generate CSV filename with the correct folder path
    csv_filename = os.path.join(raw_data_folder, f"{timestamp}_{custom_param}.csv")
    test_duration = 30  # 2 minutes

    with open(csv_filename, mode="w", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Elapsed Time (s)", "Value"])  # Updated header

        start_time = time.time()  # Capture start time
        
        while time.time() - start_time < test_duration:
            line = broadband_probe.readline().decode('utf-8').rstrip()  # Read and decode
            if line:
                try:
                    value = float(line)  # Convert sensor data to float
                    elapsed_time = time.time() - start_time  # Get elapsed time in seconds
                    formatted_time = f"{elapsed_time:.3f}"  # Include milliseconds (3 decimal places)

                    # Print & Save to CSV
                    print(f"Time: {formatted_time} s | Data: {value}")
                    csv_writer.writerow([formatted_time, value])  # Save elapsed time instead of HH:MM:SS

                except ValueError:
                    print(f"Invalid data received: {line}")

def filter_burst_and_give_mean(broadband_probe,data_dict):

    # --- Parameters ---
    # start_time = 11.8 # Set to None or 0 to use all data initially
    # end_time = 13.9   # Set to None to use all data initially
    start_time = None # Set to None or 0 to use all data initially
    end_time = None
    # Parameters for Burst Identification
    initial_threshold_dbm = -40.0 # Amplitude threshold to identify POTENTIAL burst points
    max_intra_burst_gap = 0.01 # Max time gap WITHIN a single burst (tune based on sampling rate)

    # Parameters for Filtering Identified Bursts by Duration
    # *** Use values based on your "Histogram of Burst Durations" ***
    min_acceptable_telemetry_duration = 0.0098 # Example: Lower bound from histogram
    max_acceptable_telemetry_duration = 0.11 # Example: Upper bound from histogram

    # ***----------------------------------------------------***


    # --- Voltage to dBm Function ---
    def voltage_to_dbm(voltage):
        voltage = np.clip(voltage, 0.5, 2.0) # Clamp voltage based on expected range
        return (voltage / -0.025) + 20.0

    # --- Load and Prepare Data ---
    df = pd.DataFrame(data_dict)

    required_cols = {"Elapsed Time (s)", "Value"}
    if not required_cols.issubset(df.columns):
        missing_cols = required_cols - set(df.columns)
        print(f"Error: Required columns {missing_cols} not found in CSV.")
        return 0

    # Sort by time just in case
    df = df.sort_values("Elapsed Time (s)").reset_index(drop=True)

    # Apply time window if specified
    if start_time is not None and end_time is not None:
        df_filtered = df[(df["Elapsed Time (s)"] >= start_time) & (df["Elapsed Time (s)"] < end_time)].copy()
        if df_filtered.empty:
            print(f"Error: No data found in the specified time window ({start_time}s to {end_time}s).")
            return 0
    else:
        df_filtered = df.copy() # Use all data


    # Calculate dBm
    df_filtered["dBm"] = voltage_to_dbm(df_filtered["Value"])
    print(f"Loaded {len(df_filtered)} data points.")

    # --- Burst Identification (Based on your code structure) ---

    # 1. Identify *all* points above the initial threshold
    potential_burst_points_df = df_filtered[df_filtered["dBm"] > initial_threshold_dbm].copy()

    if potential_burst_points_df.empty:
        print(f"No points found above initial threshold {initial_threshold_dbm} dBm. No filtering applied.")
        df_final_filtered = df_filtered.copy() # Keep all data
        burst_events = [] # No events to analyze
    else:
        print(f"Found {len(potential_burst_points_df)} points initially above {initial_threshold_dbm} dBm.")
        all_burst_indices = potential_burst_points_df.index # Use original DataFrame indices
        all_burst_times = potential_burst_points_df["Elapsed Time (s)"].values
        all_burst_dbm = potential_burst_points_df["dBm"].values

        # 2. Group points into distinct bursts using max_intra_burst_gap
        burst_events = [] # List to store info for each identified segment
        current_burst_original_indices = []

        if len(all_burst_indices) > 0:
            current_burst_original_indices.append(all_burst_indices[0]) # Start with the first point's original index

            for i in range(1, len(all_burst_indices)):
                time_gap = all_burst_times[i] - all_burst_times[i-1]

                if time_gap > max_intra_burst_gap + 1e-9: # If gap is LARGER, previous burst ended
                    # Finalize the previous burst segment
                    start_idx_in_burst_points = all_burst_indices.get_loc(current_burst_original_indices[0])
                    end_idx_in_burst_points = all_burst_indices.get_loc(current_burst_original_indices[-1])

                    start_t = all_burst_times[start_idx_in_burst_points]
                    end_t = all_burst_times[end_idx_in_burst_points]
                    duration = end_t - start_t

                    # Store the original indices for potential removal later
                    burst_events.append({
                        "start_time": start_t,
                        "end_time": end_t,
                        "duration": duration,
                        "num_points": len(current_burst_original_indices),
                        "original_indices": list(current_burst_original_indices) # Store the indices from df_filtered
                    })
                    # Start a new burst
                    current_burst_original_indices = [all_burst_indices[i]]
                else:
                    # Add point's original index to the current burst
                    current_burst_original_indices.append(all_burst_indices[i])

            # Add the last burst after the loop finishes
            if current_burst_original_indices:
                start_idx_in_burst_points = all_burst_indices.get_loc(current_burst_original_indices[0])
                end_idx_in_burst_points = all_burst_indices.get_loc(current_burst_original_indices[-1])
                start_t = all_burst_times[start_idx_in_burst_points]
                end_t = all_burst_times[end_idx_in_burst_points]
                duration = end_t - start_t

                burst_events.append({
                    "start_time": start_t,
                    "end_time": end_t,
                    "duration": duration,
                    "num_points": len(current_burst_original_indices),
                    "original_indices": list(current_burst_original_indices)
                })

        print(f"Grouped into {len(burst_events)} distinct potential burst events based on threshold and gap.")

        # --- Filter Identified Bursts by Duration ---
        indices_to_remove = set() # Use a set for efficient addition of unique indices
        confirmed_telemetry_events = []
        outliers_not_removed=set()
        for event in burst_events:
            if min_acceptable_telemetry_duration <= event['duration'] <= max_acceptable_telemetry_duration:
                # This burst matches the telemetry duration profile

                # Extract the dBm values for this burst
                burst_points = df_filtered.loc[event['original_indices'], "dBm"]

                # --- Outlier Detection ---
                # Example: Define outliers as points > 2 standard deviations from mean
                median_dbm = burst_points.median()

                threshold = 1  
                lower_bound = median_dbm - threshold
                upper_bound = median_dbm + threshold

                # Identify good points (NOT outliers)
                good_points_mask = (burst_points >= lower_bound) & (burst_points <= upper_bound)
                outliers_not_removed.update()
                good_indices = burst_points[good_points_mask].index.tolist()
                bad_indices = burst_points[~good_points_mask].index.tolist()
                # Update: Only remove the good (non-outlier) points
                indices_to_remove.update(good_indices)
                outliers_not_removed.update(bad_indices)
                # Also optionally store the filtered event if you want
                filtered_event = event.copy()
                filtered_event['original_indices'] = good_indices
                confirmed_telemetry_events.append(filtered_event)

        print(f"Identified {len(confirmed_telemetry_events)} events matching telemetry duration profile ({min_acceptable_telemetry_duration:.4f}s - {max_acceptable_telemetry_duration:.4f}s).")
        print(f"Removing {len(indices_to_remove)} points identified as telemetry (after outlier removal).")

        # --- Final Filtering ---
        if indices_to_remove:
            # Use drop for efficiency if indices are known
            df_final_filtered = df_filtered.drop(index=list(indices_to_remove))
        else:
            df_final_filtered = df_filtered.copy() # No points to remove

    return np.mean(df_final_filtered["dBm"])


def read_raw_probe_and_burst_analysis(broadband_probe,lat,lon):
    print(f"starting measurements at {lat} {lon}")
    # Define the folder where CSV files should be saved
    raw_data_folder = "/home/exposicopter/thesis/raman/exposicopter/raw-flight-data" #absolute path needed for rc.local

    # Ensure the folder exists
    os.makedirs(raw_data_folder, exist_ok=True)

    # Generate CSV filename using current datetime + custom parameter
    custom_param = f"{lat}-{lon}" + "-raw"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Generate CSV filename with the correct folder path
    csv_filename = os.path.join(raw_data_folder, f"{timestamp}_{custom_param}.csv")
    test_duration = 5  # seconds

    data_dict = {"Elapsed Time (s)": [], "Value": []}  # Initialize dictionary to store data

    
    with open(csv_filename, mode="w", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Elapsed Time (s)", "Value"])  # Updated header

        start_time = time.time()  # Capture start time
        
        while time.time() - start_time < test_duration:
            line = broadband_probe.readline().decode('utf-8').rstrip()  # Read and decode
            if line:
                try:
                    value = float(line)  # Convert sensor data to float
                    elapsed_time = time.time() - start_time  # Get elapsed time in seconds
                    formatted_time = f"{elapsed_time:.3f}"  # Include milliseconds (3 decimal places)

                    # Print & Save to CSV
                    print(f"Time: {formatted_time} s | Data: {value}")

                    csv_writer.writerow([formatted_time, value])  # Save elapsed time instead of HH:MM:SS

                    # Save to dictionary
                    data_dict["Elapsed Time (s)"].append(float(formatted_time))  # Store as float
                    data_dict["Value"].append(value)               
                
                except ValueError:
                    print(f"Invalid data received: {line}")
        return filter_burst_and_give_mean(broadband_probe,data_dict)

def read_probe_processed(broadband_probe):
    results=[]
    while(len(results)<5):
        line = broadband_probe.readline().decode('utf-8').rstrip()  # Read and decode
        if line:
            try:
                # Convert sensor data to numbers
                values = list(map(float, line.split(",")))
                avg = values[0]
                min_val = values[1]
                max_val = values[2]
                median_val = values[3]

                # Print & Save to CSV
                print(f"Avg: {avg}, Min: {min_val}, Max: {max_val}, Median: {median_val}")
                results.append(median_val)
            except ValueError:
                print(f"Invalid data received: {line}")
    return np.mean(results)

def read_and_send_data(drone,broadband_probe,current_lat,current_lon):
    average_5_s=read_raw_probe_and_burst_analysis(broadband_probe,current_lat,current_lon)
    print("mean median "+ str(average_5_s))
    drone.send_measurement_data(current_lat,current_lon,1.5,average_5_s)

###################################################################################################