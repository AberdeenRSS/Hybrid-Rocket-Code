import h5py
import os
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = 'data/hotfire_plots_raw_full/'
TIME_START = 0
TIME_END = 72

#Open the H5 file in read mode
with h5py.File('data/Aberdeen_5_HOTFIRE.h5', 'r') as file:

    keys = list(file['channels'].keys())

    start_index     = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_START][0]
    end_index       = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_END][0]

    os.makedirs(OUT_DIR, exist_ok=True)

    for c in list(file['channels']):

        channel = file['channels'][c]

        time    = np.array(channel['time'])
        values  = np.array(channel['data'])

        plt.title(c)
        plt.plot(time[start_index:end_index], values[start_index:end_index])
        plt.xlabel('Time (s)')

        plt.savefig(f'{OUT_DIR}/{c}.png', dpi=500)
        plt.close()

    
    # Getting the data
    # data = list(file[a_group_key])
    # print(data)