# # # import numpy as np
# # # from sklearn.cluster import DBSCAN
# # # from sklearn.preprocessing import StandardScaler
# # # from pathlib import Path
# # # import sys
# # # import matplotlib.pyplot as plt

# # # # --- Step 1: Define Your Data Structure ---

# # # base_dir = Path.cwd() 
# # # angle_dirs = [
# # #     '0 degree',
# # #     '15 degree negative',
# # #     '15 degree positive',
# # #     '30 degree negative',
# # #     '30 degree positive'
# # # ]
# # # # Colors for Plot 1 (Color by Source)
# # # source_colors = ['#FF0000', '#0000FF', '#00FF00', '#FF7F00', '#9400D3']
# # # # (Red, Blue, Green, Orange, Violet)

# # # print("Loading ONE file from each angle directory...")

# # # all_points_list = []
# # # all_source_labels = [] # To store which file each point came from

# # # # --- Step 2: Load Files and Tag Them ---

# # # for i, dir_name in enumerate(angle_dirs):
# # #     full_dir_path = base_dir / dir_name
    
# # #     if not full_dir_path.is_dir():
# # #         print(f"  Warning: Directory not found, skipping: {full_dir_path}")
# # #         continue
    
# # #     try:
# # #         first_file = next(full_dir_path.glob('*.npy'), None)
# # #         if first_file:
# # #             print(f"  Loading: {first_file.name} (as source {i})")
# # #             data = np.load(first_file)
            
# # #             if data.shape[0] > 0:
# # #                 all_points_list.append(data)
# # #                 # Create labels for this file. e.g., [0, 0, 0, ...]
# # #                 all_source_labels.append(np.full(data.shape[0], i)) 
# # #             else:
# # #                 print(f"    Warning: {first_file.name} is empty.")
# # #         else:
# # #             print(f"  Warning: No .npy files found in {dir_name}. Skipping.")
# # #     except Exception as e:
# # #         print(f"  Error loading file from {dir_name}. Error: {e}")

# # # # --- Step 3: Combine Data ---

# # # if not all_points_list:
# # #     print("\nError: No data was loaded. Please check your directories.")
# # #     sys.exit() 

# # # all_points = np.vstack(all_points_list)
# # # # Combine all source labels into one big array
# # # # e.g., [0, 0, ..., 1, 1, ..., 2, 2, ...]
# # # source_label_array = np.concatenate(all_source_labels)
# # # print(f"\nSuccessfully combined data. Total points: {all_points.shape[0]}")

# # # # --- Step 4: Prepare Data (Convert to Cartesian) ---
# # # try:
# # #     range_data = all_points[:, 0]
# # #     angle_deg_data = all_points[:, 1]
# # #     velocity_data = all_points[:, 2] 

# # #     angle_rad_data = np.deg2rad(angle_deg_data)
    
# # #     x = range_data * np.sin(angle_rad_data)
# # #     y = range_data * np.cos(angle_rad_data)
    
# # #     spatial_features = np.column_stack([x, y])

# # # except IndexError:
# # #     print(f"\nError: Failed to access data columns [0], [1], [2].")
# # #     sys.exit()


# # # # --- Step 5: Run DBSCAN (Method 2: Spatial + Velocity) ---
# # # print("\n--- Running DBSCAN (Method 2: x, y, velocity) ---")

# # # SCALED_EPS = 0.7   
# # # SCALED_MIN_SAMPLES = 10 

# # # features_3d = np.column_stack([x, y, velocity_data])
# # # features_scaled = StandardScaler().fit_transform(features_3d)
# # # db_3d = DBSCAN(eps=SCALED_EPS, min_samples=SCALED_MIN_SAMPLES).fit(features_scaled)

# # # cluster_labels = db_3d.labels_ # These are the cluster results (e.g., -1, 0, 1)
# # # n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)

# # # print(f"Found {n_clusters} targets.")
# # # print(f"Cluster Labels & Counts: {dict(zip(*np.unique(cluster_labels, return_counts=True)))}")


# # # # --- Step 6: Plot the Results (Side-by-Side) ---
# # # print("\nGenerating comparison plot...")

# # # # Create a figure to hold two subplots
# # # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# # # # --- Plot 1: Color by Source File (Your Request) ---
# # # ax1.set_title(f'Plot 1: Data Colored by Source File')
# # # ax1.set_xlabel('X Position (meters) (90°)')
# # # ax1.set_ylabel('Y Position (meters) (0°)')
# # # ax1.set_facecolor('#EAEAEA') # Light gray background

# # # # Plot the points for each source file
# # # for i, (dir_name, color) in enumerate(zip(angle_dirs, source_colors)):
# # #     mask = (source_label_array == i)
# # #     ax1.scatter(spatial_features[mask, 0], spatial_features[mask, 1], 
# # #                 c=color, label=dir_name, s=5) # s=5 for small points

# # # # --- Plot 2: Color by Cluster Result (DBSCAN Output) ---
# # # ax2.set_title(f'Plot 2: Data Colored by Cluster (Found {n_clusters} Targets)')
# # # ax2.set_xlabel('X Position (meters) (90°)')
# # # ax2.set_ylabel('Y Position (meters) (0°)')
# # # ax2.set_facecolor('#EAEAEA') # Light gray background

# # # # Get unique cluster labels and colors
# # # unique_labels = set(cluster_labels)
# # # colors_dbscan = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

# # # for k, col in zip(unique_labels, colors_dbscan):
# # #     if k == -1:
# # #         col = [0, 0, 0, 1] # Noise is black
# # #         label_text = 'Noise'
# # #     else:
# # #         label_text = f'Target {k}'
    
# # #     mask = (cluster_labels == k)
# # #     ax2.plot(spatial_features[mask, 0], spatial_features[mask, 1], 'o', 
# # #              markerfacecolor=tuple(col), markeredgecolor='k', 
# # #              markersize=7, label=label_text)

# # # # --- Add Reference Lines and Labels to BOTH plots ---
# # # for ax in [ax1, ax2]:
# # #     # Add X and Y axis lines
# # #     ax.axhline(0, color='black', linestyle='--', linewidth=1) # X-axis
# # #     ax.axvline(0, color='black', linestyle='--', linewidth=1) # Y-axis
    
# # #     # Add radar position
# # #     ax.plot(0, 0, 'rx', markersize=15, label='Radar Position')
    
# # #     ax.legend(loc='best')
# # #     ax.grid(True, linestyle=':', color='white')
# # #     ax.axis('equal') # Ensure 1m on X-axis == 1m on Y-axis

# # # # Save the combined figure
# # # plot_filename = 'dbscan_comparison_plot.png'
# # # plt.savefig(plot_filename)

# # # print(f"\nPlot saved as '{plot_filename}' in your working directory.")


# # import numpy as np
# # from pathlib import Path
# # import sys
# # import matplotlib.pyplot as plt

# # # --- Step 1: Define Your Data Structure ---

# # base_dir = Path.cwd() 
# # angle_dirs = [
# #     '0 degree',
# #     '15 degree negative',
# #     '15 degree positive',
# #     '30 degree negative',
# #     '30 degree positive'
# # ]
# # # Colors for each plot
# # source_colors = ['#FF0000', '#0000FF', '#00FF00', '#FF7F00', '#9400D3'] 
# # # (Red, Blue, Green, Orange, Violet)

# # print("Loading ONE file from each angle directory...")

# # all_points_list = []
# # all_source_labels = [] # To store which file each point came from

# # # --- Step 2: Load Files and Tag Them ---

# # for i, dir_name in enumerate(angle_dirs):
# #     full_dir_path = base_dir / dir_name
    
# #     if not full_dir_path.is_dir():
# #         print(f"  Warning: Directory not found, skipping: {full_dir_path}")
# #         continue
    
# #     try:
# #         first_file = next(full_dir_path.glob('*.npy'), None)
# #         if first_file:
# #             print(f"  Loading: {first_file.name} (as source {i})")
# #             data = np.load(first_file)
            
# #             if data.shape[0] > 0:
# #                 all_points_list.append(data)
# #                 # Create labels for this file. e.g., [0, 0, 0, ...]
# #                 all_source_labels.append(np.full(data.shape[0], i)) 
# #             else:
# #                 print(f"    Warning: {first_file.name} is empty.")
# #         else:
# #             print(f"  Warning: No .npy files found in {dir_name}. Skipping.")
# #     except Exception as e:
# #         print(f"  Error loading file from {dir_name}. Error: {e}")

# # # --- Step 3: Combine Data ---

# # if not all_points_list:
# #     print("\nError: No data was loaded. Please check your directories.")
# #     sys.exit() 

# # all_points = np.vstack(all_points_list)
# # # Combine all source labels into one big array
# # # e.g., [0, 0, ..., 1, 1, ..., 2, 2, ...]
# # source_label_array = np.concatenate(all_source_labels)
# # print(f"\nSuccessfully combined data. Total points: {all_points.shape[0]}")

# # # --- Step 4: Prepare Data (Convert to Cartesian) ---
# # try:
# #     range_data = all_points[:, 0]
# #     angle_deg_data = all_points[:, 1]
    
# #     angle_rad_data = np.deg2rad(angle_deg_data)
    
# #     x = range_data * np.sin(angle_rad_data)
# #     y = range_data * np.cos(angle_rad_data)
    
# #     spatial_features = np.column_stack([x, y])

# # except IndexError:
# #     print(f"\nError: Failed to access data columns [0] and [1].")
# #     print("This script only needs [range] and [angle] columns.")
# #     sys.exit()

# # # --- Step 5: Plot the 5 Individual Plots ---
# # print("\nGenerating 5-plot grid...")

# # # Create a figure with a 3x2 grid of subplots.
# # # We have 5 plots, so 3x2 (6 plots) is the neatest layout.
# # fig, axes = plt.subplots(3, 2, figsize=(15, 20))
# # fig.suptitle('Individual Plot for Each Beamsteering Angle', fontsize=20)

# # # 'axes' is a 2D array (3 rows, 2 cols). We'll flatten it to loop easily.
# # axes_flat = axes.flatten()

# # # Find the max x and y range across ALL points to keep all plots on the same scale
# # all_x = spatial_features[:, 0]
# # all_y = spatial_features[:, 1]
# # max_range = max(np.abs(all_x).max(), np.abs(all_y).max()) * 1.1 # 10% buffer
# # plot_limit = (-max_range, max_range)

# # for i in range(len(angle_dirs)):
# #     ax = axes_flat[i] # Get the current axis (subplot)
# #     dir_name = angle_dirs[i]
# #     color = source_colors[i]
    
# #     # Create a mask to select points *only* from this file
# #     mask = (source_label_array == i)
    
# #     if not np.any(mask): # Skip if this file had no data
# #         ax.set_title(f'{dir_name}\n(No data)', fontweight='bold')
# #         continue
    
# #     # Get the (x, y) points for this file
# #     xy = spatial_features[mask]
    
# #     # Plot these points
# #     ax.scatter(xy[:, 0], xy[:, 1], c=color, s=5, label=dir_name)
    
# #     # --- Add Reference Lines and Labels ---
# #     ax.set_title(f'Source: {dir_name}', fontweight='bold')
# #     ax.set_xlabel('X Position (meters)')
# #     ax.set_ylabel('Y Position (meters)')
# #     ax.set_facecolor('#EAEAEA') # Light gray background
    
# #     # Add X and Y axis lines
# #     ax.axhline(0, color='black', linestyle='--', linewidth=1) # X-axis
# #     ax.axvline(0, color='black', linestyle='--', linewidth=1) # Y-axis
    
# #     # Add radar position
# #     ax.plot(0, 0, 'rx', markersize=10, label='Radar Position')
    
# #     ax.legend(loc='best')
# #     ax.grid(True, linestyle=':', color='white')
    
# #     # Set the SAME x and y limits for all plots
# #     ax.set_xlim(plot_limit)
# #     ax.set_ylim(plot_limit)

# # # We have a 3x2 grid (6 plots) but only 5 files.
# # # We need to hide the last (unused) plot.
# # if len(angle_dirs) < 6:
# #     axes_flat[5].axis('off') # Hide the 6th subplot

# # # Adjust layout to prevent labels from overlapping
# # plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust for main title

# # # Save the combined figure
# # plot_filename = 'individual_source_plots.png'
# # plt.savefig(plot_filename)

# # print(f"\nPlot grid saved as '{plot_filename}' in your working directory.")


# import numpy as np
# from sklearn.cluster import DBSCAN
# from sklearn.preprocessing import StandardScaler
# from pathlib import Path
# import sys
# import matplotlib.pyplot as plt

# # --- Step 1: Define Your Data Structure ---

# base_dir = Path.cwd() 
# angle_dirs = [
#     '0 degree',
#     '15 degree negative',
#     '15 degree positive',
#     '30 degree negative',
#     '30 degree positive'
# ]
# # Colors for Plot 1 (Color by Source)
# source_colors = ['#FF0000', '#0000FF', '#00FF00', '#FF7F00', '#9400D3'] 
# # (Red, Blue, Green, Orange, Violet)

# print("Loading ONE file from each angle directory...")

# all_points_list = []
# all_source_labels = [] # To store which file each point came from

# # --- Step 2: Load Files and Tag Them ---

# for i, dir_name in enumerate(angle_dirs):
#     full_dir_path = base_dir / dir_name
    
#     if not full_dir_path.is_dir():
#         print(f"  Warning: Directory not found, skipping: {full_dir_path}")
#         continue
    
#     try:
#         first_file = next(full_dir_path.glob('*.npy'), None)
#         if first_file:
#             print(f"  Loading: {first_file.name} (as source {i})")
#             data = np.load(first_file)
            
#             if data.shape[0] > 0:
#                 all_points_list.append(data)
#                 all_source_labels.append(np.full(data.shape[0], i)) 
#             else:
#                 print(f"    Warning: {first_file.name} is empty.")
#         else:
#             print(f"  Warning: No .npy files found in {dir_name}. Skipping.")
#     except Exception as e:
#         print(f"  Error loading file from {dir_name}. Error: {e}")

# # --- Step 3: Combine Data ---

# if not all_points_list:
#     print("\nError: No data was loaded. Please check your directories.")
#     sys.exit() 

# all_points = np.vstack(all_points_list)
# source_label_array = np.concatenate(all_source_labels)
# print(f"\nSuccessfully combined data. Total points: {all_points.shape[0]}")

# # --- Step 4: Extract Data Columns ---
# try:
#     range_data = all_points[:, 0]
#     angle_deg_data = all_points[:, 1]
#     velocity_data = all_points[:, 2] 

#     # Convert angle to radians for polar plot
#     angle_rad_data = np.deg2rad(angle_deg_data)

# except IndexError:
#     print(f"\nError: Failed to access data columns [0], [1], [2].")
#     sys.exit()


# # --- Step 5: Run DBSCAN (to get cluster labels for Plot 2) ---
# # We need to run DBSCAN on (x,y,v) to get the cluster labels
# print("\n--- Running DBSCAN (for Plot 2) ---")

# # Convert to (x, y) *just* for the clustering algorithm
# x_cartesian = range_data * np.sin(angle_rad_data)
# y_cartesian = range_data * np.cos(angle_rad_data)

# SCALED_EPS = 0.7   
# SCALED_MIN_SAMPLES = 10 

# features_3d = np.column_stack([x_cartesian, y_cartesian, velocity_data])
# features_scaled = StandardScaler().fit_transform(features_3d)
# db_3d = DBSCAN(eps=SCALED_EPS, min_samples=SCALED_MIN_SAMPLES).fit(features_scaled)

# cluster_labels = db_3d.labels_ # Results (-1, 0, 1, etc.)
# n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)

# print(f"DBSCAN found {n_clusters} targets.")


# # --- Step 6: Generate New Plots (Side-by-Side) ---
# print("\nGenerating alternative plots...")

# fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
# fig.suptitle('Alternative Data Visualizations', fontsize=20)

# # --- Plot 1: Polar Plot (Color by Source File) ---
# # This plot uses a polar projection
# ax1 = plt.subplot(1, 2, 1, projection='polar')
# ax1.set_title(f'Plot 1: Polar View (Color by Source File)', pad=20)

# for i, (dir_name, color) in enumerate(zip(angle_dirs, source_colors)):
#     mask = (source_label_array == i)
#     # Plot (angle, range)
#     ax1.scatter(angle_rad_data[mask], range_data[mask], 
#                 c=color, label=dir_name, s=5)

# # Configure the polar plot
# ax1.set_theta_zero_location('N') # 0 degrees (North) at the top
# ax1.set_theta_direction(-1) # Clockwise (angles to the right are positive)
# ax1.set_rlabel_position(22.5) # Move range labels
# ax1.set_xlabel('Angle (degrees)')
# ax1.set_ylabel('Range (meters)', labelpad=-60)
# ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))


# # --- Plot 2: Range-Velocity Plot (Color by Cluster) ---
# ax2 = plt.subplot(1, 2, 2)
# ax2.set_title(f'Plot 2: Range vs. Velocity (Color by Cluster)')
# ax2.set_facecolor('#EAEAEA')

# # Get unique cluster labels and colors
# unique_labels = set(cluster_labels)
# colors_dbscan = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

# for k, col in zip(unique_labels, colors_dbscan):
#     if k == -1:
#         col = [0, 0, 0, 1] # Noise is black
#         label_text = 'Noise'
#     else:
#         label_text = f'Target {k}'
    
#     mask = (cluster_labels == k)
    
#     # Plot (velocity, range)
#     ax2.plot(velocity_data[mask], range_data[mask], 'o', 
#              markerfacecolor=tuple(col), markeredgecolor='k', 
#              markersize=7, label=label_text)

# # Add reference lines
# ax2.axhline(0, color='black', linestyle='--', linewidth=1) # Zero range
# ax2.axvline(0, color='black', linestyle='--', linewidth=1) # Zero velocity (static clutter)

# ax2.set_xlabel('Velocity (m/s)  (Negative=Away, Positive=Towards)')
# ax2.set_ylabel('Range (meters)')
# ax2.legend(loc='best')
# ax2.grid(True, linestyle=':', color='white')


# # Save the combined figure
# plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust for main title
# plot_filename = 'alternative_plots.png'
# plt.savefig(plot_filename)

# print(f"\nPlot grid saved as '{plot_filename}' in your working directory.")


import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import sys
import matplotlib.pyplot as plt

print("Loading ONE file from each angle directory...")

# --- Step 1: Define Your Data Structure ---
base_dir = Path.cwd() 
angle_dirs = [
    '0 degree',
    '15 degree negative',
    '15 degree positive',
    '30 degree negative',
    '30 degree positive'
]
source_colors = ['#FF0000', '#0000FF', '#00FF00', '#FF7F00', '#9400D3'] 

all_points_list = []
all_source_labels = []

# --- Step 2: Load Files and Tag Them ---
for i, dir_name in enumerate(angle_dirs):
    full_dir_path = base_dir / dir_name
    if not full_dir_path.is_dir():
        print(f"  Warning: Directory not found, skipping: {full_dir_path}")
        continue
    try:
        first_file = next(full_dir_path.glob('*.npy'), None)
        if first_file:
            print(f"  Loading: {first_file.name} (as source {i})")
            data = np.load(first_file)
            if data.shape[0] > 0:
                all_points_list.append(data)
                all_source_labels.append(np.full(data.shape[0], i)) 
            else:
                print(f"    Warning: {first_file.name} is empty.")
        else:
            print(f"  Warning: No .npy files found in {dir_name}. Skipping.")
    except Exception as e:
        print(f"  Error loading file from {dir_name}. Error: {e}")

# --- Step 3: Combine Data ---
if not all_points_list:
    print("\nError: No data was loaded. Please check your directories.")
    sys.exit() 

all_points = np.vstack(all_points_list)
source_label_array = np.concatenate(all_source_labels)
print(f"\nSuccessfully combined data. Total points: {all_points.shape[0]}")

# --- Step 4: Extract Data and Convert ---
# *** ASSUMING UNITS: range (um), angle (deg), velocity (m/s) ***
try:
    range_data_um = all_points[:, 0] # Range in micrometers
    angle_deg_data = all_points[:, 1]
    velocity_data_ms = all_points[:, 2] # Velocity in m/s

    angle_rad_data = np.deg2rad(angle_deg_data)
    
    # Calculate X and Y positions in micrometers
    x_um = range_data_um * np.sin(angle_rad_data)
    y_um = range_data_um * np.cos(angle_rad_data)
    
    spatial_features_um = np.column_stack([x_um, y_um])

except IndexError:
    print(f"\nError: Failed to access data columns [0], [1], [2].")
    sys.exit()


# --- Step 5: Run DBSCAN ---
# We scale the data for clustering
# We'll use range in meters for scaling to balance with velocity
range_data_m = range_data_um / 1_000_000.0 
x_m = x_um / 1_000_000.0
y_m = y_um / 1_000_000.0

print("\n--- Running DBSCAN (x, y, velocity) ---")
SCALED_EPS = 0.7   
SCALED_MIN_SAMPLES = 10 
features_3d_scaled = np.column_stack([x_m, y_m, velocity_data_ms])
features_scaled = StandardScaler().fit_transform(features_3d_scaled)

db_3d = DBSCAN(eps=SCALED_EPS, min_samples=SCALED_MIN_SAMPLES).fit(features_scaled)
cluster_labels = db_3d.labels_
n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
print(f"DBSCAN found {n_clusters} targets.")


# --- Step 6: Generate 2x2 Comprehensive Plot Grid ---
print("\nGenerating 2x2 plot grid with fixed labels...")

fig, axes = plt.subplots(2, 2, figsize=(20, 20))
fig.suptitle('Comprehensive Data Visualization (Fixed)', fontsize=24)

demarcation_angles_deg = [-30, -15, 15, 30]
demarcation_angles_rad = [np.deg2rad(angle) for angle in demarcation_angles_deg]
max_range_um = range_data_um.max() * 1.1

# --- Plot 1: (x, y) "Zoomed Out" View, Color by Source ---
ax1 = axes[0, 0]
ax1.set_title('"Zoomed Out" View (Color by Source)', fontweight='bold')
ax1.set_xlabel('X Position (um)')
ax1.set_ylabel('Y Position (um)')
ax1.set_facecolor('#EAEAEA')

# Plot demarcation lines
for angle_rad in demarcation_angles_rad:
    line_x = max_range_um * np.sin(angle_rad)
    line_y = max_range_um * np.cos(angle_rad)
    ax1.plot([0, line_x], [0, line_y], 'k:', label=f'{int(np.rad2deg(angle_rad))}° line')

# Plot data
for i, (dir_name, color) in enumerate(zip(angle_dirs, source_colors)):
    mask = (source_label_array == i)
    ax1.scatter(spatial_features_um[mask, 0], spatial_features_um[mask, 1], 
                c=color, label=dir_name, s=5)

ax1.plot(0, 0, 'rx', markersize=15, label='Radar Position')
ax1.grid(True, linestyle=':', color='white')
ax1.axis('equal')
# Filter duplicate line labels for a clean legend
handles, labels = ax1.get_legend_handles_labels()
unique_labels = {}
for h, l in zip(handles, labels):
    if l not in unique_labels: unique_labels[l] = h
ax1.legend(unique_labels.values(), unique_labels.keys(), loc='best')


# --- Plot 2: (x, y) "Zoomed In" View, Color by Cluster ---
ax2 = axes[0, 1]
ax2.set_title(f'"Zoomed In" View (Color by Cluster, {n_clusters} Targets)', fontweight='bold')
ax2.set_xlabel('X Position (um)')
ax2.set_ylabel('Y Position (um)')
ax2.set_facecolor('#EAEAEA')

# Plot data (colored by cluster)
unique_labels = set(cluster_labels)
colors_dbscan = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors_dbscan):
    if k == -1: col = [0, 0, 0, 1]; label_text = 'Noise'
    else: label_text = f'Target {k}'
    mask = (cluster_labels == k)
    ax2.plot(spatial_features_um[mask, 0], spatial_features_um[mask, 1], 'o', 
             markerfacecolor=tuple(col), markeredgecolor='k', 
             markersize=7, label=label_text)
ax2.grid(True, linestyle=':', color='white')
ax2.legend(loc='best')
ax2.axis('equal') # Auto-zooms to the data clusters


# --- Plot 3: Polar Plot, Colored by Source File ---
ax3 = plt.subplot(2, 2, 3, projection='polar')
ax3.set_title(f'Polar View (Color by Source File)', pad=20, fontweight='bold')
for i, (dir_name, color) in enumerate(zip(angle_dirs, source_colors)):
    mask = (source_label_array == i)
    ax3.scatter(angle_rad_data[mask], range_data_um[mask], c=color, label=dir_name, s=5)
# Add demarcation lines
for angle_rad in demarcation_angles_rad:
    ax3.axvline(angle_rad, color='black', linestyle=':', label=f'{int(np.rad2deg(angle_rad))}° line')
ax3.set_theta_zero_location('N')
ax3.set_theta_direction(-1)
ax3.set_rlabel_position(22.5)
ax3.set_ylabel('Range (um)', labelpad=-60) # Set correct label
ax3.set_rlim(0, max_range_um)
# Filter duplicate line labels
handles, labels = ax3.get_legend_handles_labels()
unique_labels = {}
for h, l in zip(handles, labels):
    if l not in unique_labels: unique_labels[l] = h
ax3.legend(unique_labels.values(), unique_labels.keys(), loc='upper right', bbox_to_anchor=(1.35, 1.1))


# --- Plot 4: Range-Velocity Plot, Colored by Cluster ---
ax4 = axes[1, 1]
ax4.set_title(f'Range-Velocity - Color by Cluster', fontweight='bold')
ax4.set_facecolor('#EAEAEA')
for k, col in zip(unique_labels, colors_dbscan):
    if k == -1: col = [0, 0, 0, 1]; label_text = 'Noise'
    else: label_text = f'Target {k}'
    mask = (cluster_labels == k)
    # Plot Velocity vs Range (um)
    ax4.plot(velocity_data_ms[mask], range_data_um[mask], 'o', 
             markerfacecolor=tuple(col), markeredgecolor='k', 
             markersize=7, label=label_text)
ax4.axvline(0, color='black', linestyle='--', linewidth=1, label='Static (Zero Velocity)')
ax4.set_xlabel('Velocity (m/s)')
ax4.set_ylabel('Range (um)') # Set correct label
ax4.legend(loc='best')
ax4.grid(True, linestyle=':', color='white')


# --- Save the combined figure ---
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plot_filename = 'comprehensive_2x2_plot_FIXED.png'
plt.savefig(plot_filename)

print(f"\nFixed 2x2 plot grid saved as '{plot_filename}' in your working directory.")