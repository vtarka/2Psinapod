import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import random


### SET VARIABLES FOR NOW - EVENTUALLY TAKE IT FROM THE CONFIG FILE OR A CSV WITH ALL RECORDINGS ###
stim_fr = 100
flu_fr = 10
epoch_start = -100 # in ms
epoch_end = 2000 # in ms
stim_fl_error_allowed = 10 # time in seconds to allow as the difference in length between the stim file and fluorescence trace

csv_path = "D:/15khz/TSeries-01042022-1431-120_Cycle00001_VoltageRecording_001.csv"

parent_dir = "D:/15khz/"


def validate_lengths(stim,fl):
    # make sure our stimulus file corresponds with our fluorescence trace in length
    
    stim_time = len(stim)/stim_fr # f * s/f = s
    fl_time = len(fl[0])/flu_fr

    # if one is short or longer by more than the allowed error, return False so we can either throw and error 
    if stim_time < fl_time-stim_fl_error_allowed or stim_time > fl_time+stim_fl_error_allowed:
        return False
    else:
        return True


def get_onset_frames(stim):
    # get our max voltage value so we know what the trigger looks like
    max_value = max(stim, key=lambda x:x[1])
    max_value = max_value[1]

    onset_times = [] # empty list to append our onset frames into
    time_list_index = 0 # counter to keep track of our index in the onset_times list

    # for each frame in the stimulus file
    for i in range(len(stim)):
        (time,voltage) = stim[i] # unpack the voltage at that timepoint

        if voltage.round() == max_value.round(): # if the voltage was our trigger voltage
            if time_list_index == 0: # and if we're at the first index (so there's no previous index to compare with)
                onset_times.append(time/1000) # add the time as an onset time in SECONDS
                time_list_index += 1

            # if we're not at index zero, we need to compare this voltage with the previous saved onset voltage
            # otherwise we save a bunch of voltages as separate triggers because they all match the max voltage
            # but we just want one timepoint per trigger
            elif time/1000 -  onset_times[time_list_index - 1] > 1: 
                onset_times.append(time/1000) # want it in second not millisecond
                time_list_index += 1

    # get the onset times in terms of frames of our fluorescence trace
    onset_flu_frames = np.multiply(onset_times,flu_fr) # s * f/s = f

    return onset_flu_frames


def epoch_traces(fl,onset_frames):
    # fl is nCells x nFrames
    # frames is nOnsetTimes x 1

    # we will return an nCells x nTrials x nFrames array

    # first we'll find the number of frames that should be in each trial
    trial_length_in_time = epoch_end - epoch_start # this gives us length in ms
    trial_length_in_time = trial_length_in_time/1000 # now we have it in seconds

    # converting to frames (at the frame rate of the 2P recording)
    trial_length_in_frames = int(trial_length_in_time * flu_fr) # s * f/s = f

    # now we intitialize an array to store what we'll ultimately return
    epoched_traces = np.zeros((len(fl),len(onset_frames),trial_length_in_frames))

    # start filling up this empty matrix
    # loop through each ROI
    for roi in range(len(fl)):

        # and for each trial onset
        for trial in range(len(onset_frames)):

            # get the trial starting frame and ending frame
            trial_starting_frame = int(onset_frames[trial] + (epoch_start/1000*flu_fr))
            trial_ending_frame = int(onset_frames[trial] + (epoch_end/1000*flu_fr))

            # grab this range of frames from the fl trace and store it in the epoched matrix
            epoched_traces[roi,trial,:] = fl[roi,trial_starting_frame:trial_ending_frame]

    return epoched_traces


def plot_trace(fl,onsets):
    for i in range(len(fl)):
        plt.plot(fl[i,:])

    plt.vlines(onsets,0,200)
    plt.show()


def plot_trials(epoched_traces):
    # epoched traces is an nCell x nTrial x nFrame matrix

    fig, axs = plt.subplots(nrows=5, ncols=1)

    # get a random sampling of 10 cells
    cell_sample = random.sample(range(len(epoched_traces)),10)

    # get a random sampling of trials
    trial_sample = random.sample(range(len(epoched_traces[0])),5)

    for trial in range(5):

        # for each cell we've sampled
        for cell in range(10):

            axs[trial].plot(epoched_traces[cell_sample[cell],trial_sample[trial],:])


        if trial == 0:
            axs[trial].set_title("Random sampling of cells and trials from the current recording")
            
        if trial != 4:
            axs[trial].get_xaxis().set_visible(False)
            axs[trial].get_yaxis().set_visible(False)
        else:
            axs[trial].set_xlabel("Time since stimulus onset (ms)")

        # add a line to show exactly where stimulus happened
        # epoching started 100 ms before the trigger
        # so have an extra 0.1s * flu_fr frames before the trigger
        axs[trial].vlines(epoch_start/-1000*flu_fr,0,100)

        # set the limits on the axes
        axs[trial].set_ylim([0,100])
        axs[trial].set_xlim([0,0])

        # set the xticks so we're seeing the time
        axs[trial].set_xticks(range(1,20,5),range(0,2000,500))
        axs[trial].set_yticks([0,100])
        
    plt.show()


def main():


    stim = np.genfromtxt(csv_path,delimiter=',',skip_header=True)
    fl = np.load(parent_dir + "F.npy")
    fneu = np.load(parent_dir + "Fneu.npy")
    iscell = np.load(parent_dir + "iscell.npy")

    # make sure the stim file and flu traces are roughly the same length
    # if they aren't the same, we'll exit the code 
    if not validate_lengths(stim, fl):
        raise ValueError("The lengths of stimulus file and the fluorescence traces are not the same. Exiting.")

    # get an array of all the stimulus onset times in terms of fluorescence frames
    onset_frames = get_onset_frames(stim)

    # get fluorescence traces for the ROIs that are actually cells
    fl_cells = fl[np.where(iscell[:,0]==1)[0],:]

    # epoch the traces so we just get the fluorescence during trials
    d = epoch_traces(fl_cells,onset_frames)

    plot_trials(d)

if __name__=='__main__':
    main()