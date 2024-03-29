'''
Script to correct misaligned voltage recording files so that triggers line up with the first stim on the calcium (Ca2+) trace.
Inputs: stim triggers in a csv (filepath in config.json file, "Trigger_if_wrong"), Frame of Ca2+ trace where first stim is 
    estimated to occur. Stimulus frame rate (TriggerFR in config) and recording frame rate (RecordingFR in config)   
Outputs: Realigned stim CSV where the required number of frames are removed from beginning of voltage recording, to line it
    up correctly. Saved to BASE_PATH, "RecordingFolder" in config.json.
AUTHOR: Conor Lane, Created March 2023, Conor.lane1995@gmail.com
'''

import numpy as np
import os
import json
import pandas as pd 


FIRST_RESPONSE_FRAME = 50


# load what we need from the config.json file
with open(os.path.abspath(os.path.dirname(__file__)) +'/../../config.json','r') as f:
    config = json.load(f)

BASE_PATH = config['RecordingFolder'] # folder with all of the files generated by Suite2P for this recording (F.npy, iscell.npy, etc)
CSV_PATH = config['Trigger_if_wrong'] # name of CSV (assumed to be in the folder given in line above) with the trigger voltages over the recording
STIMULUS_FRAMERATE = config['TriggerFR'] # framerate of the trigger file
RECORDING_FRAMERATE = config['RecordingFR'] # framerate of the fluorescence recording

def realign_triggers(stimulus):
    # Find the first frame in the trigger file that corresponds to a TTL pulse being sent (voltage jumps to above 3 mV)
    FIRST_TRIGGER_FRAME = next(i for i,v in enumerate(stimulus[:,1]) if v > 3)
    print("The first stim begins at trigger frame: ", FIRST_TRIGGER_FRAME)

    # Find the discrepancy between the length to the first trigger frame and the length to the first Ca2+ response onset. 
    remove_from_trigger = int(FIRST_TRIGGER_FRAME - ((FIRST_RESPONSE_FRAME * STIMULUS_FRAMERATE) / RECORDING_FRAMERATE))
    print("frames to remove to align stim: ", remove_from_trigger)

    # Remove the required number of frames from the trigger array, and reset the index column to zero.
    stimulus = stimulus[remove_from_trigger:,:]
    stimulus[:,0] = np.arange(len(stimulus))
    return stimulus



def main():
    # Load our incorrect voltage trace from the config file.
    stimulus = np.genfromtxt(BASE_PATH + CSV_PATH,delimiter=',',skip_header=True)
    # Realign the voltage trace so that first trigger and first response are matched. 
    stimulus = realign_triggers(stimulus)

    # Save the corrected voltage trace in the recording folder. 
    pd.DataFrame(stimulus).to_csv(os.path.join(BASE_PATH, "voltage_recording_corrected" + '.' + "csv"),header=None,index=None)

if __name__=='__main__':
    main()