from tkinter import N
import matplotlib as mpl
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd
from statsmodels.formula.api import ols
import numpy as np
import pickle
from scipy.stats import zscore
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)) + '/../')
print(os.path.abspath(os.path.dirname(__file__)) + '/../')
from utils import get_avg_trace

# load what we need from the config file
with open(os.path.abspath(os.path.dirname(__file__)) +'/../../config.json','r') as f:
    config = json.load(f)

BASE_PATH = config['RecordingFolder'] # folder with all of the files generated by Suite2P for this recording (F.npy, iscell.npy, etc)
traces_file = config['AnalysisFile']
output_file = traces_file
FRAMERATE = config['RecordingFR']
EPOCH_START_IN_MS = config['EpochStart']
EPOCH_END_IN_MS = config['EpochEnd']

def make_pd_df_from_dict(cell_trace,nFreq,nItsy,nReps):
    # store the average value of each trial into the appropriate index of the data frame
    evoked_activity = np.empty(shape=(nFreq*nItsy*nReps))

    idx_counter = 0
    for freq in cell_trace:

        for itsy in cell_trace[freq]:

            each_trial_avg_container = []

            for rep in cell_trace[freq][itsy]:
                trial_activity = cell_trace[freq][itsy][rep][5:]
                trial_avg = np.average(trial_activity)
                evoked_activity[idx_counter] = trial_avg
                idx_counter += 1

            # each_trial_avg = np.array(each_trial_avg_container)
            # total_avg = np.average(each_trial_avg)
            # evoked_activity[idx_counter] = total_avg

            

    frequencies = range(1,nFreq+1)
    intensities = range(1,nItsy+1)

    df = pd.DataFrame({'frequency': np.repeat(frequencies,nItsy*nReps),
    'intensity': np.tile(np.repeat(intensities,nReps),nFreq),
    'activity':evoked_activity})

    return df

def main():
    # import our epoched and formatted recordings
    # it's formatted like this: 
    # cell { traces { freq { intensity { repetition: trace = [x,x,x,x,...] }}}}
    with open(BASE_PATH + traces_file, 'rb') as f:
        cell_dictionary = pickle.load(f)

    active_cell_counter = 0 
    for cell in cell_dictionary:
        df = make_pd_df_from_dict(cell_dictionary[cell]['traces'],12,4,10)

        model = ols('activity ~ C(frequency) + C(intensity) + C(frequency):C(intensity)',data=df).fit()

        results = sm.stats.anova_lm(model, typ=2)

        if (results['PR(>F)']['C(frequency)'] < 0.05) or (results['PR(>F)']['C(frequency):C(intensity)'] < 0.05):
            active_cell_counter += 1
            cell_dictionary[cell]['active'] = True
        else:
            cell_dictionary[cell]['active'] = False


    print("Number of total cells: ")
    print(len(cell_dictionary))
    print("Number of active cells: ")
    print(active_cell_counter)

    with open(BASE_PATH+output_file,'wb') as f:
        pickle.dump(cell_dictionary,f)

if __name__=="__main__":
    main()