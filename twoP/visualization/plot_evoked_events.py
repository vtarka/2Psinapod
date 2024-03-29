"""
TODO doc!
"""

import matplotlib.pyplot as plt
import numpy as np
import json
import os

# load what we need from the config file
with open(os.path.abspath(os.path.dirname(__file__)) +'/../../config.json','r') as f:
    config = json.load(f)

BASE_PATH = config['RecordingFolder'] # folder with all of the files generated by Suite2P for this recording (F.npy, iscell.npy, etc)

def main():
    events = np.load(BASE_PATH + "evoked_events.npy")

    plt.figure(1)
    plt.hist(events[:,0])
    

    plt.figure(2)
    plt.hist(events[:,1])

    plt.show()



if __name__=="__main__":
    main()