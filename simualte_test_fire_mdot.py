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
TIME_START = 50.6
TIME_END = 72   
NITROUS_CUTOFF = 60

#Open the H5 file in read mode
with h5py.File('data/Aberdeen_5_HOTFIRE.h5', 'r') as file:

    keys = list(file['channels'].keys())

    start_index     = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_START][0]
    end_index       = [i for i, x in enumerate(file['channels'][keys[0]]['time']) if x > TIME_END][0]

    nitrous_massflow_channel = file['channels']['NITROUS_FT_1']

    time    = np.array(nitrous_massflow_channel['time'])
    time = time[start_index:end_index] - time[start_index]
    dt = time[1] - time[0]

    nitrous_massflow_values  = np.array(nitrous_massflow_channel['data'])[start_index:end_index]
    nitrous_massflow_values[nitrous_massflow_values < 0] = 0.001



# Load a default engine to start with
engine = nitrous_engine_sim.Cengines()
nitrous_engine_sim.load_default_engine(engine, 'Nitrous_HDPE')

#Engine Andrew

engine.ox_tank_volume = 0.8/1000
engine.ox_orifice_number = 2
engine.ox_orifice_diameter = 0.01

engine.fuel_orifice_number = 0

a_0 = 0.000116

engine.regression_a = a_0
engine.regression_n = 0.336
engine.regression_m = 0

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
engine.ox_status = 0
engine.ox_initial_tank_pressure_bar = 30
engine.ox_tank_pressure_bar = 30
engine.ox_initial_temp_C = 30


# Prepare sim
engine.delta_time = 0.001

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
        cur_mdot = np.interp(engine.burn_time, time, nitrous_massflow_values)

        engine.ox_mdot_tank_outflow = cur_mdot
    else:
        break

    engine.simulate_engine()

    total_impulse += engine.thrust*engine.delta_time

    if i % RESULT_PERIOD == 0:
        rr = nitrous_engine_sim.get_running_results(engine)
        rr['ox_tank_pressure'] = engine.ox_tank_pressure_bar
        rr['ox_mdot_tank_outflow'] = engine.ox_mdot_tank_outflow
        rr['isp'] = (engine.thrust/rr['nozzle_mass_flowrate'])/10
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



plt.figure(figsize=(18,18))
plt.subplot(3, 3, 1)

plt.title('Mass flow rates')
plt.plot(df['time'], df['total_inflow']/1000, label='Total inflow')
plt.plot(df['time'], df['nozzle_mass_flowrate']/1000, label='Nozzle mass flow')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Mass flow (g/s)')

plt.subplot(3, 3, 2)

plt.title('Thrust')
plt.plot(df['time'], df['thrust'])
plt.xlabel('Time (s)')
plt.ylabel('Force (N)')

plt.subplot(3, 3, 3)

plt.title('Chamber pressure')
plt.plot(df['time'], df['chamber_pressure_bar'], label='Chamber pressure')
plt.xlabel('Time (s)')
plt.ylabel('Pressure (bar)')

plt.subplot(3, 3, 4)

plt.title('Nozzile exit pressure')
plt.plot(df['time'], df['nozzle_exit_pressure']/1e5)
plt.xlabel('Time (s)')
plt.ylabel('Pressure (bar)')

plt.subplot(3, 3, 5)

plt.title('Fuel grain hole size')
plt.plot(df['time'], df['centre_port_radius'])
plt.xlabel('Time (s)')
plt.ylabel('Radius (m)')

plt.subplot(3, 3, 6)

plt.title('Oxidizer mass flow (experimental)')
plt.plot(df['time'], df['ox_mdot_tank_outflow']*1000)
plt.xlabel('Time (s)')
plt.ylabel('Ox mdot (g/s)')

plt.subplot(3, 3, 7)

plt.title('Oxydizer to fuel ratio')
plt.plot(df['time'], 1/df['fuel_to_ox_ratio'])
plt.xlabel('Time (s)')
plt.ylabel('O/F ratio')

plt.subplot(3, 3, 8)

plt.title('Isp')
plt.plot(df['time'], df['isp'])
plt.xlabel('Time (s)')
plt.ylabel('Isp (s)')


os.makedirs(OUT_DIR, exist_ok=True)
plt.savefig(f'{OUT_DIR}/mdot.png', dpi=300, bbox_inches='tight')