# # import sys
# # import os
# # import struct
# # import time
# # import numpy as np
# # import array as arr
# # import configuration as cfg  # You still need your configuration.py file
# # from scipy.ndimage import convolve1d, gaussian_filter
# # import matplotlib.pyplot as plt
# # from sklearn.cluster import DBSCAN
# # from sklearn.preprocessing import StandardScaler
# # import math

# # # --- (All your functions from before... no changes here) ---
# # def read8byte(x):
# #     return struct.unpack('<hhhh', x)
# # class FrameConfig:
# #     def __init__(self):
# #         self.numTxAntennas = cfg.NUM_TX
# #         self.numRxAntennas = cfg.NUM_RX
# #         self.numLoopsPerFrame = cfg.LOOPS_PER_FRAME
# #         self.numADCSamples = cfg.ADC_SAMPLES
# #         self.numAngleBins = cfg.NUM_ANGLE_BINS
# #         self.numChirpsPerFrame = self.numTxAntennas * self.numLoopsPerFrame
# #         self.numRangeBins = self.numADCSamples
# #         self.numDopplerBins = self.numLoopsPerFrame
# #         self.chirpSize = self.numRxAntennas * self.numADCSamples
# #         self.chirpLoopSize = self.chirpSize * self.numTxAntennas
# #         self.frameSize = self.chirpLoopSize * self.numLoopsPerFrame
# # class PointCloudProcessCFG:
# #     def __init__(self):
# #         self.frameConfig = FrameConfig()
# #         self.enableStaticClutterRemoval = True
# #         self.EnergyTop128 = True
# #         self.RangeCut = False
# #         self.outputVelocity = True
# #         self.outputSNR = True
# #         self.outputRange = True
# #         self.outputInMeter = True
# #         self.EnergyThrMed = True
# #         self.ConstNoPCD = False
# #         self.dopplerToLog = False
# # def bin2np_frame(bin_frame):
# #     np_frame = np.zeros(shape=(len(bin_frame) // 2), dtype=np.complex128)
# #     np_frame[0::2] = bin_frame[0::4] + 1j * bin_frame[2::4]
# #     np_frame[1::2] = bin_frame[1::4] + 1j * bin_frame[3::4]
# #     return np_frame
# # def frameReshape(frame, frameConfig):
# #     frameWithChirp = np.reshape(
# #         frame,
# #         (frameConfig.numLoopsPerFrame, frameConfig.numTxAntennas, frameConfig.numRxAntennas, -1)
# #     )
# #     return frameWithChirp.transpose(1, 2, 0, 3)
# # def rangeFFT(reshapedFrame, frameConfig):
# #     windowedBins1D = reshapedFrame
# #     return np.fft.fft(windowedBins1D)
# # def clutter_removal(input_val, axis=0):
# #     reordering = np.arange(len(input_val.shape))
# #     reordering[0] = axis
# #     reordering[axis] = 0
# #     input_val = input_val.transpose(reordering)
# #     mean = input_val.mean(0)
# #     output_val = input_val - mean
# #     return output_val.transpose(reordering)
# # def dopplerFFT(rangeResult, frameConfig):
# #     windowedBins2D = rangeResult * np.reshape(np.hamming(frameConfig.numLoopsPerFrame), (1, 1, -1, 1))
# #     dopplerFFTResult = np.fft.fft(windowedBins2D, axis=2)
# #     dopplerFFTResult = np.fft.fftshift(dopplerFFTResult, axes=2)
# #     return dopplerFFTResult
# # def mod_filter(current_frame, prev_frame, alpha=0.7):
# #     if prev_frame is None:
# #         return current_frame
# #     return alpha * prev_frame + (1 - alpha) * current_frame
# # def apply_gaussian_filter(frame, sigma=1.0):
# #     filtered = gaussian_filter(np.abs(frame), sigma=sigma)
# #     return filtered * np.exp(1j * np.angle(frame))
# # def naive_xyz(virtual_ant, num_tx=3, num_rx=4, fft_size=64):
# #     num_detected_obj = virtual_ant.shape[1]
# #     azimuth_ant = virtual_ant[:2 * num_rx, :]
# #     azimuth_ant_padded = np.zeros((fft_size, num_detected_obj), dtype=np.complex128)
# #     azimuth_ant_padded[:2 * num_rx, :] = azimuth_ant
# #     azimuth_fft = np.fft.fft(azimuth_ant_padded, axis=0)
# #     k_max = np.argmax(np.abs(azimuth_fft), axis=0)
# #     peak_1 = np.array([azimuth_fft[k, i] for i, k in enumerate(k_max)])
# #     k_max[k_max > (fft_size // 2) - 1] -= fft_size
# #     wx = 2 * np.pi / fft_size * k_max
# #     x_vector = wx / np.pi
# #     elevation_ant = virtual_ant[2 * num_rx:, :]
# #     elevation_fft = np.fft.fft(elevation_ant, axis=0)
# #     elevation_max = np.argmax(np.log2(np.abs(elevation_fft)), axis=0)
# #     peak_2 = np.array([elevation_fft[k, i] for i, k in enumerate(elevation_max)])
# #     wz = np.angle(peak_1 * peak_2.conj() * np.exp(1j * 2 * wx))
# #     z_vector = wz / np.pi
# #     y_vector = np.sqrt(np.maximum(1 - x_vector**2 - z_vector**2, 0))
# #     return x_vector, y_vector, z_vector
# # def frame2pointcloud(dopplerResult, pointCloudProcessCFG):
# #     dopplerResultSumAllAntenna = np.sum(dopplerResult, axis=(0, 1))
# #     dopplerResultInDB = np.abs(dopplerResultSumAllAntenna)
# #     cfarResult = np.zeros(dopplerResultInDB.shape, bool)
# #     if pointCloudProcessCFG.EnergyTop128:
# #         top_size = 128
# #         energyThre128 = np.partition(dopplerResultInDB.ravel(), dopplerResultInDB.size - top_size - 1)[
# #             dopplerResultInDB.size - top_size - 1]
# #         cfarResult[dopplerResultInDB > energyThre128] = True
# #     det_peaks_indices = np.argwhere(cfarResult)
# #     if len(det_peaks_indices) == 0:
# #         return np.empty((0, 6))
# #     R = det_peaks_indices[:, 1].astype(np.float64)
# #     V = (det_peaks_indices[:, 0] - FrameConfig().numDopplerBins // 2).astype(np.float64)
# #     if pointCloudProcessCFG.outputInMeter:
# #         R *= cfg.RANGE_RESOLUTION
# #         V *= cfg.DOPPLER_RESOLUTION
# #     energy = dopplerResultInDB[cfarResult]
# #     AOAInput = dopplerResult[:, :, cfarResult].reshape(12, -1)
# #     if AOAInput.shape[1] ==.0:
# #         return np.empty((0, 6))
# #     x_vec, y_vec, z_vec = naive_xyz(AOAInput)
# #     x, y, z = x_vec * R, y_vec * R, z_vec * R
# #     pointCloud = np.vstack((x, y, z, V, energy, R)).T
# #     med_energy = np.median(pointCloud[:, 4])
# #     return pointCloud[pointCloud[:, 4] > med_energy]

# # # ======================================================================
# # # --- STEP 1: Main Processing Block (MODIFIED WITH GRACE PERIOD) ---
# # # ======================================================================
# # if __name__ == '__main__':
    
# #     try:
# #         cfg.NUM_TX 
# #     except (NameError, AttributeError):
# #         print("ERROR: configuration.py not found or is empty.")
# #         print("Please create configuration.py in the same folder.")
# #         sys.exit()

# #     # --- Parameters ---
# #     npy_filename = "./0_degree_positive1_2025-10-16_15-25-11.npy"

# #     # DBSCAN Parameters
# #     DBSCAN_EPS = 0.7 
# #     DBSCAN_MIN_SAMPLES = 5 
    
# #     # --- NEW/UPDATED TRACKER PARAMETERS ---
    
# #     # *** TUNING PARAMETER 1 ***
# #     # This is the most likely problem. The "jumps" are probably
# #     # bigger than 1.0m. Let's try 2.0m.
# #     MAX_ASSOCIATION_DISTANCE = 2.0 # (Was 1.0)
    
# #     # *** TUNING PARAMETER 2 ***
# #     # This is the new "grace period". We will only delete a track
# #     # if we haven't seen it for 5 frames in a row.
# #     MAX_LOST_FRAMES = 5 
    
# #     # This dictionary will store our *persistent* tracks
# #     # Format: { track_id: {'path': [...], 'last_pos': (x,y), 'lost_for': 0}, ... }
# #     active_tracks = {}
# #     next_track_id = 0 # Counter to give new targets a unique ID
    
# #     # --- Load Data ---
# #     data = np.load(npy_filename, allow_pickle=True)
# #     print("Loaded .npy file:", npy_filename)
# #     print("Data shape:", data.shape)

# #     pointCloudProcessCFG = PointCloudProcessCFG()
# #     frameConfig = pointCloudProcessCFG.frameConfig
# #     total_frames = data.shape[0]

# #     prev_range_fft = None
# #     scaler = StandardScaler()

# #     # ======================================================================
# #     # --- STEP 2: Frame-by-Frame Processing Loop ---
# #     # ======================================================================
# #     print("Processing frames to find trajectories...")
# #     for frame_no in range(total_frames):
# #         frame_data = data[frame_no]
# #         np_frame = frame_data if np.iscomplexobj(frame_data) else bin2np_frame(frame_data)
        
# #         # --- (Standard Processing) ---
# #         reshapedFrame = frameReshape(np_frame, frameConfig)
# #         rangeResult = rangeFFT(reshapedFrame, frameConfig)
# #         rangeResult = apply_gaussian_filter(rangeResult, sigma=1.0)
# #         rangeResult = mod_filter(rangeResult, prev_range_fft, alpha=0.6)
# #         prev_range_fft = rangeResult
# #         if pointCloudProcessCFG.enableStaticClutterRemoval:
# #             rangeResult = clutter_removal(rangeResult, axis=2)
# #         dopplerResult = dopplerFFT(rangeResult, frameConfig)
        
# #         pointCloud = frame2pointcloud(dopplerResult, pointCloudProcessCFG)

# #         if pointCloud.shape[0] == 0:
# #             print(f"Frame {frame_no+1}/{total_frames}: No points detected.")
# #             # --- NEW: We must still update "lost" counters even on empty frames ---
# #             for track_id in list(active_tracks.keys()): # Use list() to allow deletion
# #                 active_tracks[track_id]['lost_for'] += 1
# #                 if active_tracks[track_id]['lost_for'] > MAX_LOST_FRAMES:
# #                     print(f"  --> Track {track_id} removed (lost for {MAX_LOST_FRAMES} frames).")
# #                     del active_tracks[track_id]
# #             continue # Skip to next frame

# #         # ======================================================================
# #         # --- STEP 3: DBSCAN Clustering (Per Frame) ---
# #         # ======================================================================
        
# #         features_3d = pointCloud[:, [0, 1, 3]] # x, y, Velocity
# #         features_scaled = scaler.fit_transform(features_3d)
# #         db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(features_scaled)
# #         labels = db.labels_
        
# #         unique_labels = set(labels)
# #         unique_labels.discard(-1) # Remove noise label

# #         # ======================================================================
# #         # --- STEP 4: Calculate Centroids for This Frame ---
# #         # ======================================================================
        
# #         current_frame_centroids = []
# #         for target_id in unique_labels:
# #             mask = (labels == target_id)
# #             cluster_points_xy = pointCloud[mask, :2] # Get x,y columns
# #             centroid = np.mean(cluster_points_xy, axis=0)
# #             current_frame_centroids.append(centroid)

# #         if not current_frame_centroids:
# #             print(f"Frame {frame_no+1}/{total_frames}: Found {pointCloud.shape[0]} points, but no clusters.")
# #             # --- NEW: We must still update "lost" counters ---
# #             for track_id in list(active_tracks.keys()):
# #                 active_tracks[track_id]['lost_for'] += 1
# #                 if active_tracks[track_id]['lost_for'] > MAX_LOST_FRAMES:
# #                     print(f"  --> Track {track_id} removed (lost).")
# #                     del active_tracks[track_id]
# #             continue # Skip to next frame
            
# #         print(f"Frame {frame_no+1}/{total_frames}: Found {len(current_frame_centroids)} target(s).")

# #         # ======================================================================
# #         # --- STEP 5: NEW TRACKER - Associate Centroids to Tracks ---
# #         # ======================================================================

# #         unmatched_centroids = list(range(len(current_frame_centroids)))
# #         matched_track_ids = set()

# #         # Try to match existing tracks
# #         for track_id, track_data in active_tracks.items():
# #             last_pos = track_data['last_pos']
            
# #             distances = []
# #             for i in unmatched_centroids:
# #                 dist = np.linalg.norm(last_pos - current_frame_centroids[i])
# #                 distances.append(dist)
            
# #             if not distances:
# #                 continue 

# #             min_dist = min(distances)
# #             best_match_index_in_list = np.argmin(distances)
# #             best_match_centroid_index = unmatched_centroids[best_match_index_in_list]
            
# #             if min_dist < MAX_ASSOCIATION_DISTANCE:
# #                 best_match_centroid = current_frame_centroids[best_match_centroid_index]
                
# #                 track_data['path'].append(best_match_centroid)
# #                 track_data['last_pos'] = best_match_centroid
# #                 track_data['lost_for'] = 0 # Reset lost counter
                
# #                 matched_track_ids.add(track_id)
# #                 unmatched_centroids.remove(best_match_centroid_index) 

# #         # --- THIS IS THE NEW "GRACE PERIOD" LOGIC ---
# #         # Any track that wasn't matched is "lost" for one frame
# #         for track_id in list(active_tracks.keys()): # Use list() to allow deletion
# #             if track_id not in matched_track_ids:
# #                 active_tracks[track_id]['lost_for'] += 1
                
# #                 # Check if we've exceeded the grace period
# #                 if active_tracks[track_id]['lost_for'] > MAX_LOST_FRAMES:
# #                     print(f"  --> Track {track_id} removed (lost for {MAX_LOST_FRAMES} frames).")
# #                     del active_tracks[track_id]

# #         # Any centroid that wasn't matched is a *new* target
# #         for i in unmatched_centroids:
# #             new_centroid = current_frame_centroids[i]
# #             active_tracks[next_track_id] = {
# #                 'path': [new_centroid],
# #                 'last_pos': new_centroid,
# #                 'lost_for': 0
# #             }
# #             print(f"  --> New Target {next_track_id} detected at ({new_centroid[0]:.2f}, {new_centroid[1]:.2f})")
# #             next_track_id += 1 # Increment for the next new target

# #     # ======================================================================
# #     # --- STEP 6: Plot the Final Persistent Trajectories ---
# #     # ======================================================================
# #     print("\nProcessing complete. Plotting trajectories.")

# #     if active_tracks:
# #         plt.figure(figsize=(10, 8))
        
# #         for track_id, track_data in active_tracks.items():
# #             path = track_data['path']
            
# #             # Only plot tracks that have more than one point
# #             if len(path) > 1:
# #                 path_np = np.array(path)
                
# #                 # Plot the trajectory
# #                 plt.plot(path_np[:, 0], path_np[:, 1], 'o-', label=f'Person {track_id} Trajectory')
# #                 # Plot the start point
# #                 plt.plot(path_np[0, 0], path_np[0, 1], 'g*', markersize=15, label=f'Start Person {track_id}') 
# #                 # Plot the end point
# #                 plt.plot(path_np[-1, 0], path_np[-1, 1], 'rs', markersize=10, label=f'End Person {track_id}') 

# #         plt.xlabel("X (m)")
# #         plt.ylabel("Y (m)")
# #         plt.title(f"Persistent Target Trajectories from {npy_filename}")
# #         plt.grid(True)
# #         plt.axis('equal')
        
# #         # Clean up the legend to avoid duplicates
# #         handles, labels = plt.gca().get_legend_handles_labels()
# #         by_label = dict(zip(labels, handles))
# #         plt.legend(by_label.values(), by_label.keys())
        
# #         plt.show()
# #     else:
# #         print("No trajectories were found.")



# import sys
# import os
# import struct
# import time
# import numpy as np
# import array as arr
# import configuration as cfg  # You still need your configuration.py file
# from scipy.ndimage import convolve1d, gaussian_filter
# import matplotlib.pyplot as plt
# from sklearn.cluster import DBSCAN
# from sklearn.preprocessing import StandardScaler
# import math

# # --- (All your functions from before... no changes here) ---
# def read8byte(x):
#     return struct.unpack('<hhhh', x)
# class FrameConfig:
#     def __init__(self):
#         self.numTxAntennas = cfg.NUM_TX
#         self.numRxAntennas = cfg.NUM_RX
#         self.numLoopsPerFrame = cfg.LOOPS_PER_FRAME
#         self.numADCSamples = cfg.ADC_SAMPLES
#         self.numAngleBins = cfg.NUM_ANGLE_BINS
#         self.numChirpsPerFrame = self.numTxAntennas * self.numLoopsPerFrame
#         self.numRangeBins = self.numADCSamples
#         self.numDopplerBins = self.numLoopsPerFrame
#         self.chirpSize = self.numRxAntennas * self.numADCSamples
#         self.chirpLoopSize = self.chirpSize * self.numTxAntennas
#         self.frameSize = self.chirpLoopSize * self.numLoopsPerFrame
# class PointCloudProcessCFG:
#     def __init__(self):
#         self.frameConfig = FrameConfig()
#         self.enableStaticClutterRemoval = True
#         self.EnergyTop128 = True
#         self.RangeCut = False
#         self.outputVelocity = True
#         self.outputSNR = True
#         self.outputRange = True
#         self.outputInMeter = True
#         self.EnergyThrMed = True
#         self.ConstNoPCD = False
#         self.dopplerToLog = False
# def bin2np_frame(bin_frame):
#     np_frame = np.zeros(shape=(len(bin_frame) // 2), dtype=np.complex128)
#     np_frame[0::2] = bin_frame[0::4] + 1j * bin_frame[2::4]
#     np_frame[1::2] = bin_frame[1::4] + 1j * bin_frame[3::4]
#     return np_frame
# def frameReshape(frame, frameConfig):
#     frameWithChirp = np.reshape(
#         frame,
#         (frameConfig.numLoopsPerFrame, frameConfig.numTxAntennas, frameConfig.numRxAntennas, -1)
#     )
#     return frameWithChirp.transpose(1, 2, 0, 3)
# def rangeFFT(reshapedFrame, frameConfig):
#     windowedBins1D = reshapedFrame
#     return np.fft.fft(windowedBins1D)
# def clutter_removal(input_val, axis=0):
#     reordering = np.arange(len(input_val.shape))
#     reordering[0] = axis
#     reordering[axis] = 0
#     input_val = input_val.transpose(reordering)
#     mean = input_val.mean(0)
#     output_val = input_val - mean
#     return output_val.transpose(reordering)
# def dopplerFFT(rangeResult, frameConfig):
#     windowedBins2D = rangeResult * np.reshape(np.hamming(frameConfig.numLoopsPerFrame), (1, 1, -1, 1))
#     dopplerFFTResult = np.fft.fft(windowedBins2D, axis=2)
#     dopplerFFTResult = np.fft.fftshift(dopplerFFTResult, axes=2)
#     return dopplerFFTResult
# def mod_filter(current_frame, prev_frame, alpha=0.7):
#     if prev_frame is None:
#         return current_frame
#     return alpha * prev_frame + (1 - alpha) * current_frame
# def apply_gaussian_filter(frame, sigma=1.0):
#     filtered = gaussian_filter(np.abs(frame), sigma=sigma)
#     return filtered * np.exp(1j * np.angle(frame))
# def naive_xyz(virtual_ant, num_tx=3, num_rx=4, fft_size=64):
#     num_detected_obj = virtual_ant.shape[1]
#     azimuth_ant = virtual_ant[:2 * num_rx, :]
#     azimuth_ant_padded = np.zeros((fft_size, num_detected_obj), dtype=np.complex128)
#     azimuth_ant_padded[:2 * num_rx, :] = azimuth_ant
#     azimuth_fft = np.fft.fft(azimuth_ant_padded, axis=0)
#     k_max = np.argmax(np.abs(azimuth_fft), axis=0)
#     peak_1 = np.array([azimuth_fft[k, i] for i, k in enumerate(k_max)])
#     k_max[k_max > (fft_size // 2) - 1] -= fft_size
#     wx = 2 * np.pi / fft_size * k_max
#     x_vector = wx / np.pi
#     elevation_ant = virtual_ant[2 * num_rx:, :]
#     elevation_fft = np.fft.fft(elevation_ant, axis=0)
#     elevation_max = np.argmax(np.log2(np.abs(elevation_fft)), axis=0)
#     peak_2 = np.array([elevation_fft[k, i] for i, k in enumerate(elevation_max)])
#     wz = np.angle(peak_1 * peak_2.conj() * np.exp(1j * 2 * wx))
#     z_vector = wz / np.pi
#     y_vector = np.sqrt(np.maximum(1 - x_vector**2 - z_vector**2, 0))
#     return x_vector, y_vector, z_vector
# def frame2pointcloud(dopplerResult, pointCloudProcessCFG):
#     dopplerResultSumAllAntenna = np.sum(dopplerResult, axis=(0, 1))
#     dopplerResultInDB = np.abs(dopplerResultSumAllAntenna)
#     cfarResult = np.zeros(dopplerResultInDB.shape, bool)
#     if pointCloudProcessCFG.EnergyTop128:
#         top_size = 128
#         energyThre128 = np.partition(dopplerResultInDB.ravel(), dopplerResultInDB.size - top_size - 1)[
#             dopplerResultInDB.size - top_size - 1]
#         cfarResult[dopplerResultInDB > energyThre128] = True
#     det_peaks_indices = np.argwhere(cfarResult)
#     if len(det_peaks_indices) == 0:
#         return np.empty((0, 6))
#     R = det_peaks_indices[:, 1].astype(np.float64)
#     V = (det_peaks_indices[:, 0] - FrameConfig().numDopplerBins // 2).astype(np.float64)
#     if pointCloudProcessCFG.outputInMeter:
#         R *= cfg.RANGE_RESOLUTION
#         V *= cfg.DOPPLER_RESOLUTION
#     energy = dopplerResultInDB[cfarResult]
#     AOAInput = dopplerResult[:, :, cfarResult].reshape(12, -1)
#     if AOAInput.shape[1] == 0:
#         return np.empty((0, 6))
#     x_vec, y_vec, z_vec = naive_xyz(AOAInput)
#     x, y, z = x_vec * R, y_vec * R, z_vec * R
#     pointCloud = np.vstack((x, y, z, V, energy, R)).T
#     med_energy = np.median(pointCloud[:, 4])
#     return pointCloud[pointCloud[:, 4] > med_energy]

# # ======================================================================
# # --- STEP 1: Main Processing Block (Final Tuning) ---
# # ======================================================================
# if __name__ == '__main__':
    
#     try:
#         cfg.NUM_TX 
#     except (NameError, AttributeError):
#         print("ERROR: configuration.py not found or is empty.")
#         sys.exit()

#     # --- Parameters ---
#     npy_filename = "./0_degree_positive1_2025-10-16_15-25-11.npy"

#     # DBSCAN Parameters
#     DBSCAN_EPS = 0.7 
#     DBSCAN_MIN_SAMPLES = 5 
    
#     # --- TRACKER PARAMETERS ---
    
#     # Keep this high to bridge gaps
#     MAX_ASSOCIATION_DISTANCE = 4.0 
    
#     # --- *** THIS IS THE FIX *** ---
#     # Increase the grace period from 5 to 20 frames
#     MAX_LOST_FRAMES = 20 # (Was 5)
    
#     # --- RANGE FILTER ---
#     # This is working well to remove ghosts
#     MIN_RANGE_FILTER = 2.5 # in meters
#     MAX_RANGE_FILTER = 10.0 # in meters 
    
    
#     active_tracks = {}
#     next_track_id = 0 
    
#     data = np.load(npy_filename, allow_pickle=True)
#     print(f"Loaded .npy file: {npy_filename}")
#     print(f"Data shape: {data.shape}")

#     pointCloudProcessCFG = PointCloudProcessCFG()
#     frameConfig = pointCloudProcessCFG.frameConfig
#     total_frames = data.shape[0]

#     prev_range_fft = None
#     scaler = StandardScaler()

#     # ======================================================================
#     # --- STEP 2: Frame-by-Frame Processing Loop ---
#     # ======================================================================
#     print("Processing frames to find trajectories...")
#     for frame_no in range(total_frames):
#         frame_data = data[frame_no]
#         np_frame = frame_data if np.iscomplexobj(frame_data) else bin2np_frame(frame_data)
        
#         # --- (Standard Processing) ---
#         reshapedFrame = frameReshape(np_frame, frameConfig)
#         rangeResult = rangeFFT(reshapedFrame, frameConfig)
#         rangeResult = apply_gaussian_filter(rangeResult, sigma=1.0)
#         rangeResult = mod_filter(rangeResult, prev_range_fft, alpha=0.6)
#         prev_range_fft = rangeResult
#         if pointCloudProcessCFG.enableStaticClutterRemoval:
#             rangeResult = clutter_removal(rangeResult, axis=2)
#         dopplerResult = dopplerFFT(rangeResult, frameConfig)
        
#         pointCloud = frame2pointcloud(dopplerResult, pointCloudProcessCFG)

#         # --- Update "lost" counters on empty/no-cluster frames ---
#         def update_lost_tracks():
#             for track_id in list(active_tracks.keys()): # Use list() to allow deletion
#                 active_tracks[track_id]['lost_for'] += 1
#                 if active_tracks[track_id]['lost_for'] > MAX_LOST_FRAMES:
#                     print(f"  --> Track {track_id} removed (lost for {MAX_LOST_FRAMES} frames).")
#                     del active_tracks[track_id]

#         if pointCloud.shape[0] == 0:
#             print(f"Frame {frame_no+1}/{total_frames}: No points detected.")
#             update_lost_tracks()
#             continue # Skip to next frame

#         # ======================================================================
#         # --- STEP 3: DBSCAN Clustering (Per Frame) ---
#         # ======================================================================
        
#         features_3d = pointCloud[:, [0, 1, 3]] # x, y, Velocity
#         features_scaled = scaler.fit_transform(features_3d)
#         db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(features_scaled)
#         labels = db.labels_
        
#         unique_labels = set(labels)
#         unique_labels.discard(-1) # Remove noise label

#         # ======================================================================
#         # --- STEP 4: Calculate Centroids & FILTER GHOSTS (Per Frame) ---
#         # ======================================================================
        
#         current_frame_centroids = []
#         for target_id in unique_labels:
#             mask = (labels == target_id)
            
#             cluster_points_xy = pointCloud[mask, :2] # Get x,y columns
#             centroid = np.mean(cluster_points_xy, axis=0)
            
#             # --- *** RANGE FILTER *** ---
#             centroid_range = np.linalg.norm(centroid) 
            
#             if not (MIN_RANGE_FILTER < centroid_range < MAX_RANGE_FILTER):
#                 print(f"  ... Ignoring 'ghost' cluster at range: {centroid_range:.2f} m")
#                 continue # Skip this cluster
            
#             current_frame_centroids.append(centroid)

#         if not current_frame_centroids:
#             print(f"Frame {frame_no+1}/{total_frames}: Found points, but no targets in valid range.")
#             update_lost_tracks()
#             continue # Skip to next frame
            
#         print(f"Frame {frame_no+1}/{total_frames}: Found {len(current_frame_centroids)} target(s) in range.")

#         # ======================================================================
#         # --- STEP 5: TRACKER - Associate Centroids to Tracks ---
#         # ======================================================================

#         unmatched_centroids = list(range(len(current_frame_centroids)))
#         matched_track_ids = set()

#         for track_id, track_data in active_tracks.items():
#             last_pos = track_data['last_pos']
            
#             distances = []
#             for i in unmatched_centroids:
#                 dist = np.linalg.norm(last_pos - current_frame_centroids[i])
#                 distances.append(dist)
            
#             if not distances: continue 

#             min_dist = min(distances)
#             best_match_index_in_list = np.argmin(distances)
#             best_match_centroid_index = unmatched_centroids[best_match_index_in_list]
            
#             if min_dist < MAX_ASSOCIATION_DISTANCE:
#                 best_match_centroid = current_frame_centroids[best_match_centroid_index]
                
#                 track_data['path'].append(best_match_centroid)
#                 track_data['last_pos'] = best_match_centroid
#                 track_data['lost_for'] = 0 
                
#                 matched_track_ids.add(track_id)
#                 unmatched_centroids.remove(best_match_centroid_index) 

#         # --- Update "lost" counters ---
#         for track_id in list(active_tracks.keys()): 
#             if track_id not in matched_track_ids:
#                 active_tracks[track_id]['lost_for'] += 1
                
#                 if active_tracks[track_id]['lost_for'] > MAX_LOST_FRAMES:
#                     print(f"  --> Track {track_id} removed (lost).")
#                     del active_tracks[track_id]

#         # --- Create new tracks ---
#         for i in unmatched_centroids:
#             new_centroid = current_frame_centroids[i]
#             active_tracks[next_track_id] = {
#                 'path': [new_centroid],
#                 'last_pos': new_centroid,
#                 'lost_for': 0
#             }
#             print(f"  --> New Target {next_track_id} detected at ({new_centroid[0]:.2f}, {new_centroid[1]:.2f})")
#             next_track_id += 1 

#     # ======================================================================
#     # --- STEP 6: Plot the Final Persistent Trajectories ---
#     # ======================================================================
#     print("\nProcessing complete. Plotting trajectories.")

#     if active_tracks:
#         plt.figure(figsize=(10, 8))
        
#         for track_id, track_data in active_tracks.items():
#             path = track_data['path']
            
#             if len(path) > 1:
#                 path_np = np.array(path)
                
#                 plt.plot(path_np[:, 0], path_np[:, 1], 'o-', label=f'Person {track_id} Trajectory')
#                 plt.plot(path_np[0, 0], path_np[0, 1], 'g*', markersize=15, label=f'Start Person {track_id}') 
#                 plt.plot(path_np[-1, 0], path_np[-1, 1], 'rs', markersize=10, label=f'End Person {track_id}') 

#         plt.xlabel("X (m)")
#         plt.ylabel("Y (m)")
#         plt.title(f"Persistent Target Trajectories from {npy_filename}")
#         plt.grid(True)
#         plt.axis('equal')
        
#         handles, labels = plt.gca().get_legend_handles_labels()
#         by_label = dict(zip(labels, handles))
#         plt.legend(by_label.values(), by_label.keys())
        
#         plt.show()
#     else:
#         print("No trajectories were found.")


import sys
import os
import struct
import time
import numpy as np
import array as arr
import configuration as cfg  # You still need your configuration.py file
from scipy.ndimage import convolve1d, gaussian_filter
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import math

# --- (All your functions from before... no changes here) ---
def read8byte(x):
    return struct.unpack('<hhhh', x)
class FrameConfig:
    def __init__(self):
        self.numTxAntennas = cfg.NUM_TX
        self.numRxAntennas = cfg.NUM_RX
        self.numLoopsPerFrame = cfg.LOOPS_PER_FRAME
        self.numADCSamples = cfg.ADC_SAMPLES
        self.numAngleBins = cfg.NUM_ANGLE_BINS
        self.numChirpsPerFrame = self.numTxAntennas * self.numLoopsPerFrame
        self.numRangeBins = self.numADCSamples
        self.numDopplerBins = self.numLoopsPerFrame
        self.chirpSize = self.numRxAntennas * self.numADCSamples
        self.chirpLoopSize = self.chirpSize * self.numTxAntennas
        self.frameSize = self.chirpLoopSize * self.numLoopsPerFrame
class PointCloudProcessCFG:
    def __init__(self):
        self.frameConfig = FrameConfig()
        self.enableStaticClutterRemoval = True
        self.EnergyTop128 = True
        self.RangeCut = False
        self.outputVelocity = True
        self.outputSNR = True
        self.outputRange = True
        self.outputInMeter = True
        self.EnergyThrMed = True
        self.ConstNoPCD = False
        self.dopplerToLog = False
def bin2np_frame(bin_frame):
    np_frame = np.zeros(shape=(len(bin_frame) // 2), dtype=np.complex128)
    np_frame[0::2] = bin_frame[0::4] + 1j * bin_frame[2::4]
    np_frame[1::2] = bin_frame[1::4] + 1j * bin_frame[3::4]
    return np_frame
def frameReshape(frame, frameConfig):
    frameWithChirp = np.reshape(
        frame,
        (frameConfig.numLoopsPerFrame, frameConfig.numTxAntennas, frameConfig.numRxAntennas, -1)
    )
    return frameWithChirp.transpose(1, 2, 0, 3)
def rangeFFT(reshapedFrame, frameConfig):
    windowedBins1D = reshapedFrame
    return np.fft.fft(windowedBins1D)
def clutter_removal(input_val, axis=0):
    reordering = np.arange(len(input_val.shape))
    reordering[0] = axis
    reordering[axis] = 0
    input_val = input_val.transpose(reordering)
    mean = input_val.mean(0)
    output_val = input_val - mean
    return output_val.transpose(reordering)
def dopplerFFT(rangeResult, frameConfig):
    windowedBins2D = rangeResult * np.reshape(np.hamming(frameConfig.numLoopsPerFrame), (1, 1, -1, 1))
    dopplerFFTResult = np.fft.fft(windowedBins2D, axis=2)
    dopplerFFTResult = np.fft.fftshift(dopplerFFTResult, axes=2)
    return dopplerFFTResult
def mod_filter(current_frame, prev_frame, alpha=0.7):
    if prev_frame is None:
        return current_frame
    return alpha * prev_frame + (1 - alpha) * current_frame
def apply_gaussian_filter(frame, sigma=1.0):
    filtered = gaussian_filter(np.abs(frame), sigma=sigma)
    return filtered * np.exp(1j * np.angle(frame))
def naive_xyz(virtual_ant, num_tx=3, num_rx=4, fft_size=64):
    num_detected_obj = virtual_ant.shape[1]
    azimuth_ant = virtual_ant[:2 * num_rx, :]
    azimuth_ant_padded = np.zeros((fft_size, num_detected_obj), dtype=np.complex128)
    azimuth_ant_padded[:2 * num_rx, :] = azimuth_ant
    azimuth_fft = np.fft.fft(azimuth_ant_padded, axis=0)
    k_max = np.argmax(np.abs(azimuth_fft), axis=0)
    peak_1 = np.array([azimuth_fft[k, i] for i, k in enumerate(k_max)])
    k_max[k_max > (fft_size // 2) - 1] -= fft_size
    wx = 2 * np.pi / fft_size * k_max
    x_vector = wx / np.pi
    elevation_ant = virtual_ant[2 * num_rx:, :]
    elevation_fft = np.fft.fft(elevation_ant, axis=0)
    elevation_max = np.argmax(np.log2(np.abs(elevation_fft)), axis=0)
    peak_2 = np.array([elevation_fft[k, i] for i, k in enumerate(elevation_max)])
    wz = np.angle(peak_1 * peak_2.conj() * np.exp(1j * 2 * wx))
    z_vector = wz / np.pi
    y_vector = np.sqrt(np.maximum(1 - x_vector**2 - z_vector**2, 0))
    return x_vector, y_vector, z_vector
def frame2pointcloud(dopplerResult, pointCloudProcessCFG):
    dopplerResultSumAllAntenna = np.sum(dopplerResult, axis=(0, 1))
    dopplerResultInDB = np.abs(dopplerResultSumAllAntenna)
    cfarResult = np.zeros(dopplerResultInDB.shape, bool)
    if pointCloudProcessCFG.EnergyTop128:
        top_size = 128
        energyThre128 = np.partition(dopplerResultInDB.ravel(), dopplerResultInDB.size - top_size - 1)[
            dopplerResultInDB.size - top_size - 1]
        cfarResult[dopplerResultInDB > energyThre128] = True
    det_peaks_indices = np.argwhere(cfarResult)
    if len(det_peaks_indices) == 0:
        return np.empty((0, 6))
    R = det_peaks_indices[:, 1].astype(np.float64)
    V = (det_peaks_indices[:, 0] - FrameConfig().numDopplerBins // 2).astype(np.float64)
    if pointCloudProcessCFG.outputInMeter:
        R *= cfg.RANGE_RESOLUTION
        V *= cfg.DOPPLER_RESOLUTION
    energy = dopplerResultInDB[cfarResult]
    AOAInput = dopplerResult[:, :, cfarResult].reshape(12, -1)
    if AOAInput.shape[1] == 0:
        return np.empty((0, 6))
    x_vec, y_vec, z_vec = naive_xyz(AOAInput)
    x, y, z = x_vec * R, y_vec * R, z_vec * R
    pointCloud = np.vstack((x, y, z, V, energy, R)).T
    med_energy = np.median(pointCloud[:, 4])
    return pointCloud[pointCloud[:, 4] > med_energy]

# ======================================================================
# --- STEP 1: Main Processing Block (Final Tuning) ---
# ======================================================================
if __name__ == '__main__':
    
    try:
        cfg.NUM_TX 
    except (NameError, AttributeError):
        print("ERROR: configuration.py not found or is empty.")
        sys.exit()

    # --- Parameters ---
    npy_filename = "./0_degree_positive1_2025-10-16_15-25-11.npy"

    # DBSCAN Parameters
    DBSCAN_EPS = 0.7 
    DBSCAN_MIN_SAMPLES = 5 
    
    # --- TRACKER PARAMETERS ---
    
    # Keep this high to bridge gaps
    MAX_ASSOCIATION_DISTANCE = 4.0 
    
    # --- *** THIS IS THE FIX *** ---
    # Increase the grace period to 50 frames to wait out long dropouts
    MAX_LOST_FRAMES = 50 # (Was 20)
    
    # --- RANGE FILTER ---
    # This is working well to remove ghosts
    MIN_RANGE_FILTER = 2.5 # in meters
    MAX_RANGE_FILTER = 10.0 # in meters 
    
    
    active_tracks = {}
    next_track_id = 0 
    
    data = np.load(npy_filename, allow_pickle=True)
    print(f"Loaded .npy file: {npy_filename}")
    print(f"Data shape: {data.shape}")

    pointCloudProcessCFG = PointCloudProcessCFG()
    frameConfig = pointCloudProcessCFG.frameConfig
    total_frames = data.shape[0]

    prev_range_fft = None
    scaler = StandardScaler()

    # ======================================================================
    # --- STEP 2: Frame-by-Frame Processing Loop ---
    # ======================================================================
    print("Processing frames to find trajectories...")
    for frame_no in range(total_frames):
        frame_data = data[frame_no]
        np_frame = frame_data if np.iscomplexobj(frame_data) else bin2np_frame(frame_data)
        
        # --- (Standard Processing) ---
        reshapedFrame = frameReshape(np_frame, frameConfig)
        rangeResult = rangeFFT(reshapedFrame, frameConfig)
        rangeResult = apply_gaussian_filter(rangeResult, sigma=1.0)
        rangeResult = mod_filter(rangeResult, prev_range_fft, alpha=0.6)
        prev_range_fft = rangeResult
        if pointCloudProcessCFG.enableStaticClutterRemoval:
            rangeResult = clutter_removal(rangeResult, axis=2)
        dopplerResult = dopplerFFT(rangeResult, frameConfig)
        
        pointCloud = frame2pointcloud(dopplerResult, pointCloudProcessCFG)

        # --- Update "lost" counters on empty/no-cluster frames ---
        def update_lost_tracks():
            for track_id in list(active_tracks.keys()): # Use list() to allow deletion
                active_tracks[track_id]['lost_for'] += 1
                if active_tracks[track_id]['lost_for'] > MAX_LOST_FRAMES:
                    print(f"  --> Track {track_id} removed (lost for {MAX_LOST_FRAMES} frames).")
                    del active_tracks[track_id]

        if pointCloud.shape[0] == 0:
            print(f"Frame {frame_no+1}/{total_frames}: No points detected.")
            update_lost_tracks()
            continue # Skip to next frame

        # ======================================================================
        # --- STEP 3: DBSCAN Clustering (Per Frame) ---
        # ======================================================================
        
        features_3d = pointCloud[:, [0, 1, 3]] # x, y, Velocity
        features_scaled = scaler.fit_transform(features_3d)
        db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(features_scaled)
        labels = db.labels_
        
        unique_labels = set(labels)
        unique_labels.discard(-1) # Remove noise label

        # ======================================================================
        # --- STEP 4: Calculate Centroids & FILTER GHOSTS (Per Frame) ---
        # ======================================================================
        
        current_frame_centroids = []
        for target_id in unique_labels:
            mask = (labels == target_id)
            
            cluster_points_xy = pointCloud[mask, :2] # Get x,y columns
            centroid = np.mean(cluster_points_xy, axis=0)
            
            # --- *** RANGE FILTER *** ---
            centroid_range = np.linalg.norm(centroid) 
            
            if not (MIN_RANGE_FILTER < centroid_range < MAX_RANGE_FILTER):
                print(f"  ... Ignoring 'ghost' cluster at range: {centroid_range:.2f} m")
                continue # Skip this cluster
            
            current_frame_centroids.append(centroid)

        if not current_frame_centroids:
            print(f"Frame {frame_no+1}/{total_frames}: Found points, but no targets in valid range.")
            update_lost_tracks()
            continue # Skip to next frame
            
        print(f"Frame {frame_no+1}/{total_frames}: Found {len(current_frame_centroids)} target(s) in range.")

        # ======================================================================
        # --- STEP 5: TRACKER - Associate Centroids to Tracks ---
        # ======================================================================

        unmatched_centroids = list(range(len(current_frame_centroids)))
        matched_track_ids = set()

        for track_id, track_data in active_tracks.items():
            last_pos = track_data['last_pos']
            
            distances = []
            for i in unmatched_centroids:
                dist = np.linalg.norm(last_pos - current_frame_centroids[i])
                distances.append(dist)
            
            if not distances: continue 

            min_dist = min(distances)
            best_match_index_in_list = np.argmin(distances)
            best_match_centroid_index = unmatched_centroids[best_match_index_in_list]
            
            if min_dist < MAX_ASSOCIATION_DISTANCE:
                best_match_centroid = current_frame_centroids[best_match_centroid_index]
                
                track_data['path'].append(best_match_centroid)
                track_data['last_pos'] = best_match_centroid
                track_data['lost_for'] = 0 
                
                matched_track_ids.add(track_id)
                unmatched_centroids.remove(best_match_centroid_index) 

        # --- Update "lost" counters ---
        for track_id in list(active_tracks.keys()): 
            if track_id not in matched_track_ids:
                active_tracks[track_id]['lost_for'] += 1
                
                if active_tracks[track_id]['lost_for'] > MAX_LOST_FRAMES:
                    print(f"  --> Track {track_id} removed (lost).")
                    del active_tracks[track_id]

        # --- Create new tracks ---
        for i in unmatched_centroids:
            new_centroid = current_frame_centroids[i]
            active_tracks[next_track_id] = {
                'path': [new_centroid],
                'last_pos': new_centroid,
                'lost_for': 0
            }
            print(f"  --> New Target {next_track_id} detected at ({new_centroid[0]:.2f}, {new_centroid[1]:.2f})")
            next_track_id += 1 

    # ======================================================================
    # --- STEP 6: Plot the Final Persistent Trajectories ---
    # =================================S=====================================
    print("\nProcessing complete. Plotting trajectories.")

    if active_tracks:
        plt.figure(figsize=(10, 8))
        
        for track_id, track_data in active_tracks.items():
            path = track_data['path']
            
            if len(path) > 1:
                path_np = np.array(path)
                
                plt.plot(path_np[:, 0], path_np[:, 1], 'o-', label=f'Person {track_id} Trajectory')
                plt.plot(path_np[0, 0], path_np[0, 1], 'g*', markersize=15, label=f'Start Person {track_id}') 
                plt.plot(path_np[-1, 0], path_np[-1, 1], 'rs', markersize=10, label=f'End Person {track_id}') 

        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")
        plt.title(f"Persistent Target Trajectories from {npy_filename}")
        plt.grid(True)
        plt.axis('equal')
        
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        
        plt.show()
    else:
        print("No trajectories were found.")