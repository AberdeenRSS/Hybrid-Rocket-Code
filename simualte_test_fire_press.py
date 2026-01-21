import math
import os
import h5py
import nitrous_engine_sim
from nitrous_engine_sim import assign_engine_parameters, read_engine_file, write_engine_file, read_engine_parameters
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nitrous_engine_sim.result_helper import get_running_results

# Load the test data

OUT_DIR = 'output/hotfire_sims/'
TYPE = 'VAPOUR' #  'LIQUID'
TIME_START = 50.5
TIME_END = 72   
NITROUS_CUTOFF = 60

#Open the H5 file in read mode
with h5py.File('data/Aberdeen_5_HOTFIRE.h5', 'r') as file:

    keys = list(file['channels'].keys())

    start_index     = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_START][0]
    end_index       = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_END][0]

    pressure_channel = file['channels']['NITROUS_PT_4']

    time    = np.array(pressure_channel['time'])
    time = time[start_index:end_index] - time[start_index]
    dt = time[1] - time[0]

    pressure_values  = np.array(pressure_channel['data'])[start_index:end_index]
    # Zero thrust values relative to start of fire
    # pressure_values -= pressure_values[start_index] 

    temp_channel = file['channels']['NITROUS_TT_4']
    temp_values  = np.array(temp_channel['data'])[start_index:end_index]

    chamber_pressure_channel = file['channels']['R2S_PT_1']
    chamber_pressure_values  = np.array(chamber_pressure_channel['data'])[start_index:end_index]

    thrust_channel = file['channels']['THRUST_STAND_LC1']
    thrust_values  = np.array(thrust_channel['data'])
    # Zero thrust values relative to start of fire
    thrust_values -= thrust_values[start_index] 
    thrust_values  = np.array(thrust_channel['data'])[start_index:end_index]


# Load a default engine to start with
engine = nitrous_engine_sim.Cengines()
nitrous_engine_sim.load_default_engine(engine, 'Nitrous_HDPE')

#Engine Andrew

engine.ox_tank_volume = 0.8/1000
engine.ox_orifice_number = 2
engine.ox_orifice_diameter = 0.001

engine.fuel_orifice_number = 0

# a_0 = 0.000116

# engine.regression_a = a_0
# engine.regression_n = 0.35 # 0.336
# engine.regression_m = 0

engine.solid_propellant_density = 960

engine.charge_length = 0.15
engine.charge_radius = 0.03
engine.centre_port_radius = 0.015
engine.port_max_radius = engine.charge_radius

engine.pre_comb_chamber_length = 0.06
engine.post_comb_chamber_length = 0.04

engine.nozzle_efficiency = 1
engine.nozzle_throat_rdot = 0
engine.nozzle_area_ratio = 3
engine.nozzle_throat_diameter = 0.003*2

# write_engine_file(read_engine_parameters(engine), 'aberdeen_r2s.engine')

# Configure manual mode
engine.ox_feed_model = 2
engine.ox_status = 0 if TYPE == 'LIQUID' else 1
engine.ox_initial_tank_pressure_bar = 30
engine.ox_tank_pressure_bar = 30
engine.ox_initial_temp_C = 30

# Fitted density values
fitted_nitrous_density_t = np.array([0,  7.5,  8, 9.03, 9.2, 9.5, 11, 17, 23])
fitted_nitrous_density_v = np.array([20, 20,  55, 32,   75,  75,  12, 5,  3.5])*2.5

# Prepare sim
engine.delta_time = 0.0001

engine.burn_status = 0
engine.initialize_engine()

engine.burn_status = 1
engine.ignition = True

engine.surpress_mixture_out_of_range = True

MAX_ITERATIONS = 200000
RESULT_PERIOD = 1
i = 0
res = list()
last_fault = 0
total_impulse = 0

while i < MAX_ITERATIONS:

    if engine.burn_time < np.max(time):
        cur_press = np.interp(engine.burn_time, time, pressure_values)
        cur_temp = np.interp(engine.burn_time, time, temp_values)

        engine.ox_tank_pressure_bar = cur_press
        engine.ox_initial_temp_C = cur_temp

        rho = np.interp(engine.burn_time, fitted_nitrous_density_t, fitted_nitrous_density_v)

        engine.ox_tank_vapour_density = rho
        engine.ox_tank_liquid_density = rho

    else:
        break


    engine.simulate_engine()

    total_impulse += engine.thrust*engine.delta_time

    if i % RESULT_PERIOD == 0:
        rr = nitrous_engine_sim.get_running_results(engine)
        rr['ox_tank_pressure'] = engine.ox_tank_pressure_bar
        rr['ox_mdot_tank_outflow'] = engine.ox_mdot_tank_outflow
        rr['isp'] = (engine.thrust/rr['nozzle_mass_flowrate'])/10
        rr['ox_density'] = rho
        res.append(rr)

    if engine._fault != last_fault:
        if engine._fault > 0:
            print(f'New engine fault at {engine.burn_time:.3f}s: {nitrous_engine_sim.get_error_msg(engine._fault)}')
        else:
            print(f'All faults cleared at {engine.burn_time:.3f}s')
        last_fault = engine._fault

    i += 1


print(f'Iterations: {i}')
print(f'Result data points {len(res)}')
print(f'Engine burn time: {engine.burn_time}')
print(f'Total impulse: {total_impulse}')

df = pd.DataFrame(res)

total_ox_mass_spent = np.sum(df['ox_mdot_tank_outflow']) * engine.delta_time

initial_radius = df['centre_port_radius'][0]
final_radius = df['centre_port_radius'][len(df['centre_port_radius'])-1]
fuel_volume_spent = (final_radius**2 - initial_radius**2)*math.pi*engine.charge_length
fuel_mass_spent = fuel_volume_spent*engine.solid_propellant_density

print(f'Fuel spent {fuel_mass_spent:.3f}kg')
print(f'Oxidizer spent: {total_ox_mass_spent:.3f}kg')
print(f'Engine specific impulse: {np.average(df["isp"]):.2f}')


# plt.figure(figsize=(18,18))
# plt.subplot(3, 3, 1)

# plt.title('Mass flow rates')
# plt.plot(df['time'], df['total_inflow']*1000, label='Total inflow')
# plt.plot(df['time'], df['nozzle_mass_flowrate']*1000, label='Nozzle')
# plt.plot(df['time'], df['ox_mdot_tank_outflow']*1000, label='Oxidizer')

# plt.legend()
# plt.xlabel('Time (s)')
# plt.ylabel('Mass flow (g/s)')

# plt.subplot(3, 3, 2)

# plt.title('Thrust')
# plt.plot(df['time'], df['thrust'])
# plt.xlabel('Time (s)')
# plt.ylabel('Force (N)')

# plt.subplot(3, 3, 3)

# plt.title('Chamber pressure')
# plt.plot(df['time'], df['chamber_pressure_bar'], label='Chamber pressure')
# plt.xlabel('Time (s)')
# plt.ylabel('Pressure (bar)')

# plt.subplot(3, 3, 4)

# plt.title('Nozzile exit pressure')
# plt.plot(df['time'], df['nozzle_exit_pressure']/1e5)
# plt.xlabel('Time (s)')
# plt.ylabel('Pressure (bar)')

# plt.subplot(3, 3, 5)

# plt.title('Fuel grain hole size')
# plt.plot(df['time'], df['centre_port_radius'])
# plt.xlabel('Time (s)')
# plt.ylabel('Radius (m)')

# plt.subplot(3, 3, 6)

# plt.title('Pressure (Experimental)')
# plt.plot(time, pressure_values)
# plt.xlabel('Time (s)')
# plt.ylabel('Pressure (bar)')

# plt.subplot(3, 3, 7)

# plt.title('Oxydizer to fuel ratio')
# plt.plot(df['time'], 1/df['fuel_to_ox_ratio'])
# plt.xlabel('Time (s)')
# plt.ylabel('O/F ratio')

# plt.subplot(3, 3, 8)

# plt.title('Isp')
# plt.plot(df['time'], df['isp'])
# plt.xlabel('Time (s)')
# plt.ylabel('Isp (s)')

# plt.subplot(3, 3, 9)

# plt.title('Nitrous Temperature (Experimental)')
# plt.plot(time, temp_values)
# plt.xlabel('Time (s)')
# plt.ylabel('T (K)')

# os.makedirs(OUT_DIR, exist_ok=True)
# plt.savefig(f'{OUT_DIR}/pressure_{TYPE}.png', dpi=300, bbox_inches='tight')
# plt.clf()

plt.figure(figsize=(9,6))


# plt.plot(time, thrust_values, '-', label='Experimental')
# plt.plot(df['time'], df['thrust'], '.', label='Simulated')
# plt.xlabel('Time (s)')
# plt.ylabel('Thrust (N)')
# plt.legend()
# plt.title('Thrust')
# plt.savefig(f'{OUT_DIR}/pressure_{TYPE}_thrust.png', dpi=300, bbox_inches='tight')
# plt.clf()

# plt.plot(time, chamber_pressure_values, '-', label='Experimental')
# plt.plot(df['time'], df['chamber_pressure_bar'], '.', label='Simulated')
# plt.xlabel('Time (s)')
# plt.ylabel('Pressure (Bar)')
# plt.legend()
# plt.title('Chamber pressure')
# plt.savefig(f'{OUT_DIR}/pressure_{TYPE}_pressure.png', dpi=300, bbox_inches='tight')
# plt.clf()

plt.plot(df['time'], df['ox_density'])
plt.xlabel('Time (s)')
plt.ylabel('Density (kg/m^3)')
plt.title('Nitrous density')
plt.savefig(f'{OUT_DIR}/pressure_{TYPE}_density.png', dpi=300, bbox_inches='tight')
