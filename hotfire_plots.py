import h5py
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.integrate

OUT_DIR = 'data/hotfire_plots/'
TIME_START = 50
TIME_END = 70   
NITROUS_CUTOFF = 60

#Open the H5 file in read mode
with h5py.File('data/Aberdeen_5_HOTFIRE.h5', 'r') as file:

    keys = list(file['channels'].keys())

    start_index     = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_START][0]
    end_index       = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_END][0]


    thrust_channel = file['channels']['THRUST_STAND_LC1_CALIBRATED']

    time    = np.array(thrust_channel['time'])
    dt = time[1] - time[0]

    thrust_values  = np.array(thrust_channel['data'])
    # Zero thrust values relative to start of fire
    thrust_values -= thrust_values[start_index] 

    nitrous_mass_flow_channel = file['channels']['NITROUS_FT_1']
    nitrous_mass_flow_values  = np.array(nitrous_mass_flow_channel['data'])

    # Zero nitrous flow values relative to their min value (this is an assumption as it gets us realistic isp values)
    # nitrous_mass_flow_values -= np.min(nitrous_mass_flow_values[start_index:end_index])

    os.makedirs(OUT_DIR, exist_ok=True)

    plt.title('Thrust')
    plt.plot(time[start_index:end_index], thrust_values[start_index:end_index], 'o', color='0', ms=0.5)
    plt.axvline(NITROUS_CUTOFF, label=f'Nitrous cutoff ({NITROUS_CUTOFF:.2f}s)', ls='--', color='r')

    plt.xlabel('Time (s)')
    plt.ylabel('Thrust (N)')
    plt.legend()

    plt.savefig(f'{OUT_DIR}/thrust.png', dpi=500)
    plt.close()

    # total_thrust = scipy.integrate.trapezoid(thrust_values[start_index:end_index], time[start_index:end_index])
    # total_nitrous_mass_flow = scipy.integrate.trapezoid(nitrous_mass_flow_values[start_index:end_index], time[start_index:end_index])


    total_thrust = np.sum(thrust_values[start_index:end_index]*dt)
    total_nitrous_mass_flow = np.sum(nitrous_mass_flow_values[start_index:end_index]*dt)

    isp = total_thrust/((total_nitrous_mass_flow + 0.09)*10)

    print(f'Total thrust: {total_thrust}Ns')
    print(f'Total nitrous: {total_nitrous_mass_flow}kg')
    print(f'Isp: {isp}')


        
    
    # Getting the data
    # data = list(file[a_group_key])
    # print(data)``