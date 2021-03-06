import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import json

# load what we need from the config file
with open('/Users/veronica/2Psinapod/config.json','r') as f:
    config = json.load(f)

BASE_PATH = config['RecordingFolder'] # folder with all of the files generated by Suite2P for this recording (F.npy, iscell.npy, etc)
# csv_path = config['Triggers'] # name of CSV (assumed to be in the folder given in line above) with the trigger voltages over the recording
# conditions_path = config['Conditions'] # name of the CSV (assumed to be in folder given two lines above) with the condition types of each trial (freq, intensity, etc)
# output_path = config['AnalysisFile'] # name of the file that all of the analysis is getting saved in (tuning, best frequency, etc)
# STIMULUS_FRAMERATE = config['TriggerFR']
# TRIGGER_DELAY_IN_MS = config['TriggerDelay'] # delay between TDT sending a trigger and the stimulus actually happening
RECORDING_FRAMERATE = config['RecordingFR']
EPOCH_START_IN_MS = config['EpochStart']

# STIMULUS_FRAMERATE = 100
# TRIGGER_DELAY_IN_MS = 50 # delay between TDT sending a trigger and the stimulus actually happening
# RECORDING_FRAMERATE = 10

# epoch_start_in_ms = -500 # in ms
# epoch_end_in_ms = 6000 # in ms
# stim_fl_error_allowed = 10 # time in seconds to allow as the difference in length between the stim file and fluorescence trace

# BASE_PATH = "/Volumes/Office_USB/Vid_157/"
SPIKE_THRESHOLD = 150


def get_spike_train(cell_trace):
    # we're getting an nTrials x nFrames array
    # but let's just make one continuous trace
    trace = cell_trace
    trace[trace<SPIKE_THRESHOLD] = 0
    trace[trace>SPIKE_THRESHOLD] = 1
    return trace

def get_raster_matrix(epoched_traces):
    # we will go cell by cell (row by row)
    # nCells x nTrials x nFrames array

    raster_matrix = np.zeros((len(epoched_traces),len(epoched_traces[1,:])))    
    # and count each frame above the threshold as 1
    for cell_idx in range(len(epoched_traces)):
        raster_matrix[cell_idx,:] = get_spike_train(epoched_traces[cell_idx,:])

    return raster_matrix

def plot_raster(raster_matrix,onsets):
    counter = 1
    for row in raster_matrix:
        raster = np.where(row==1)[0]
        plt.scatter(raster, np.ones(len(raster))*counter,marker="s",color="k",linewidths=0.75,alpha=0.7,s=2)
        counter+=1

    plt.xlabel("Frames (10 Hz)")
    plt.ylabel("Cell #")
    plt.title("Raster plot (spike threshold = 100 dF/F)")
    plt.suptitle("Pseudorandom stim")
    plt.vlines(onsets,0,counter,linewidth=2)

    plt.draw()

def main():
    raw_traces = np.load(BASE_PATH+"raw_corrected_traces.npy",allow_pickle=True)
    onsets = np.load(BASE_PATH+"onsets.npy",allow_pickle=True)

    raster_matrix = get_raster_matrix(raw_traces)

    plot_raster(raster_matrix,onsets)

    plt.show()

if __name__=="__main__":
    main()