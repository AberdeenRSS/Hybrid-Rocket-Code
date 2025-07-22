import math
import nitrous_engine_sim
from nitrous_engine_sim import assign_engine_parameters, read_engine_file, write_engine_file, read_engine_parameters
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nitrous_engine_sim.result_helper import get_running_results

# Load a default engine to start with
engine = nitrous_engine_sim.Cengines()
nitrous_engine_sim.load_default_engine(engine, 'Nitrous_HDPE')

#Engine Andrew

engine.ox_initial_tank_pressure_bar = 50
engine.ox_tank_volume = 10/1000
engine.ox_initial_temp_C = 20
engine.ox_orifice_number = 4
engine.ox_orifice_diameter = 0.0015

engine.fuel_orifice_number = 0

a_0 = 0.000116

engine.regression_a = a_0
engine.regression_n = 0.331
engine.regression_m = 0

engine.solid_propellant_density = 960

engine.charge_length = 0.15
engine.charge_radius = 0.03
engine.centre_port_radius = 0.01
engine.port_max_radius = engine.charge_radius

engine.pre_comb_chamber_length = 0.06
engine.post_comb_chamber_length = 0.04

engine.nozzle_efficiency = 1
engine.nozzle_throat_rdot = 0
engine.nozzle_area_ratio = 2.3
engine.nozzle_throat_diameter = 0.005*2

write_engine_file(read_engine_parameters(engine), 'aberdeen_r2s.engine')

# Prepare sim
engine.delta_time = 0.01

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

while engine.burn_status == 1 and i < MAX_ITERATIONS:

    engine.simulate_engine()

    total_impulse += engine.thrust*engine.delta_time

    if i % RESULT_PERIOD == 0:
        rr = nitrous_engine_sim.get_running_results(engine)
        rr['ox_tank_pressure'] = engine.ox_tank_pressure_bar
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
print(f'Engine specific impulse: {engine.average_ISP}')
print(f'Oxidizer spent: {engine.ox_initial_liquid_mass - engine.ox_tank_liquid_mass}kg')
# print(f'Fuel burnt: {engine.fuel_initial_liquid_mass - engine.fuel_tank_liquid_mass}')

print(f'Total impulse: {total_impulse}')

df = pd.DataFrame(res)

plt.figure(figsize=(18,18))
plt.subplot(3, 3, 1)

plt.title('Mass flow rates')
plt.plot(df['time'], df['total_inflow'], label='Total inflow')
plt.plot(df['time'], df['nozzle_mass_flowrate'], label='Nozzle mass flow')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Mass flow (kg/s)')

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

plt.title('Oxygen remaining mass')
plt.plot(df['time'], df['ox_tank_contents_mass'])
plt.xlabel('Time (s)')
plt.ylabel('Ox mass (kg)')

plt.subplot(3, 3, 7)

plt.title('Oxydizer to fuel ratio')
plt.plot(df['time'], 1/df['fuel_to_ox_ratio'])
plt.xlabel('Time (s)')
plt.ylabel('O/F ratio')

plt.subplot(3, 3, 8)

plt.title('Oxygen tank pressure')
plt.plot(df['time'], df['ox_tank_pressure'])
plt.xlabel('Time (s)')
plt.ylabel('Pressure (bar)')



plt.show()

print('x')