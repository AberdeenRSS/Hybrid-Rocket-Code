import math
import nitrous_engine_sim
from nitrous_engine_sim import assign_engine_parameters, load_default_prop, Cengines
from nitrous_engine_sim.engine_file_reader import read_engine_file
from nitrous_engine_sim.result_helper import get_running_results
import pandas as pd
import matplotlib.pyplot as plt

MAX_ITERATIONS = 200000
DT = 0.001

engine_parameters = read_engine_file('data/aberdeen_r2s.engine')


def set_engine_geometry(engine):
    engine.ox_initial_tank_pressure_bar = 50
    engine.ox_tank_volume = 40/1000
    engine.ox_initial_temp_C = 20
    engine.ox_orifice_number = 26
    engine.ox_orifice_diameter = 0.0012*2

    engine.ox_feed_model = 0

    engine.fuel_orifice_number = 0

    engine.charge_length = 0.9
    engine.charge_radius = 0.136/2
    engine.centre_port_radius = 0.02
    engine.port_max_radius = engine.charge_radius

    engine.pre_comb_chamber_length = 0.24
    engine.post_comb_chamber_length = 0.24

    engine.nozzle_efficiency = 1
    engine.nozzle_throat_rdot = 0
    engine.nozzle_area_ratio = 6
    engine.nozzle_throat_diameter = 0.0115*2

# Prepare sim
def prepare_sim(engine,dt):
    engine.delta_time = dt

    engine.burn_status = 0
    engine.initialize_engine()

    engine.burn_status = 1
    engine.ignition = True

    engine.surpress_mixture_out_of_range = True

def simulate(engine, MAX_ITERATIONS):
    i = 0
    last_fault = 0
    total_impulse = 0
    total_thrust = 0

    res = list()
    engine.simulate_engine()


    while engine.burn_status == 1 and i < MAX_ITERATIONS:
        engine.simulate_engine()

        total_impulse += engine.thrust*engine.delta_time

        if engine._fault != last_fault:
            if engine._fault > 0:
                print(f'New engine fault at {engine.burn_time:.3f}s: {nitrous_engine_sim.get_error_msg(engine._fault)}')
            else:
                print(f'All faults cleared at {engine.burn_time:.3f}s')
            last_fault = engine._fault

        total_thrust += engine.thrust
        res.append(get_running_results(engine))
        i += 1

    avg_thrust = total_thrust/i
    
    df = pd.DataFrame(res)
    initial_radius = df['centre_port_radius'][0]
    final_radius = df['centre_port_radius'][len(df['centre_port_radius'])-1]
    fuel_volume_spent = (final_radius**2 - initial_radius**2)*2*math.pi*engine.charge_length
    fuel_mass_spent = fuel_volume_spent*engine.solid_propellant_density

    print(f'    Iterations: {i}')
    print(f'    Result data points {len(res)}')
    print(f'    Engine burn time: {engine.burn_time}')
    print(f'    Total impulse: {total_impulse}')
    print(f'    Engine specific impulse: {engine.average_ISP}')
    print(f'    Oxidizer spent: {engine.ox_initial_liquid_mass - engine.ox_tank_liquid_mass}kg')
    # print(    f'Fuel burnt: {engine.fuel_initial_liquid_mass - engine.fuel_tank_liquid_mass}')
    print(f'    Total impulse: {total_impulse}')
    print(f'    Fuel spent {fuel_mass_spent}')

    return df, total_impulse, total_thrust

# Paraffin
engine = Cengines()
load_default_prop(engine, 'L_Nitrous_S_HDPE')
assign_engine_parameters(engine, engine_parameters)
set_engine_geometry(engine)

engine.solid_propellant_density = 980

# Magic Paraffin + PE wax combination
# engine.regression_a = 0.00015
# engine.regression_n = 0.65
# engine.regression_m = 0

print(engine.regression_a)

prepare_sim(engine, DT)
print('Simulating paraffin...')
paraffin_res, paraffin_total_impulse, paraffin_thrust = simulate(engine, MAX_ITERATIONS)

# print(f'HDPE I: {hdpe_total_impulse:.2f}Ns')
print(f'Paraffin I: {paraffin_total_impulse:.2f}Ns')

plt.figure(figsize=(18,18))
plt.subplot(3, 3, 1)

plt.title('Ox mass flow rates')
# plt.plot(hdpe_res['time'], hdpe_res['total_inflow'], label='Total inflow')
# plt.plot(hdpe_res['time'], hdpe_res['nozzle_mass_flowrate'], label='HDPE')
plt.plot(paraffin_res['time'], paraffin_res['nozzle_mass_flowrate'], label='Paraffin')
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Mass flow (kg/s)')

plt.subplot(3, 3, 2)

plt.title('Thrust')
# plt.plot(hdpe_res['time'], hdpe_res['thrust'], label='HDPE')
plt.plot(paraffin_res['time'], paraffin_res['thrust'], label='Paraffin')
plt.xlabel('Time (s)')
plt.ylabel('Force (N)')

plt.subplot(3, 3, 3)

plt.title('Chamber pressure')
# plt.plot(hdpe_res['time'], hdpe_res['chamber_pressure_bar'], label='HDPE')
plt.plot(paraffin_res['time'], paraffin_res['chamber_pressure_bar'], label='Paraffin')

plt.xlabel('Time (s)')
plt.ylabel('Pressure (bar)')

plt.subplot(3, 3, 4)

plt.title('Nozzile exit pressure')
# plt.plot(hdpe_res['time'], hdpe_res['nozzle_exit_pressure']/1e5, label='HDPE')
plt.plot(paraffin_res['time'], paraffin_res['nozzle_exit_pressure']/1e5, label='Paraffin')
plt.xlabel('Time (s)')
plt.ylabel('Pressure (bar)')

plt.subplot(3, 3, 5)

plt.title('Fuel grain hole size')
# plt.plot(hdpe_res['time'], hdpe_res['centre_port_radius'], label='HDPE')
plt.plot(paraffin_res['time'], paraffin_res['centre_port_radius'], label='Paraffin')
plt.xlabel('Time (s)')
plt.ylabel('Radius (m)')

plt.subplot(3, 3, 6)

plt.title('Oxygen remaining mass')
# plt.plot(hdpe_res['time'], hdpe_res['ox_tank_contents_mass'], label='HDPE')
plt.plot(paraffin_res['time'], paraffin_res['ox_tank_contents_mass'], label='Paraffin')
plt.xlabel('Time (s)')
plt.ylabel('Ox mass (kg)')

plt.subplot(3, 3, 7)

plt.title('Oxydizer to fuel ratio')
# plt.plot(hdpe_res['time'], 1/hdpe_res['fuel_to_ox_ratio'], label='HDPE')
plt.plot(paraffin_res['time'], 1/paraffin_res['fuel_to_ox_ratio'], label='Paraffin')
plt.xlabel('Time (s)')
plt.ylabel('O/F ratio')

plt.subplot(3, 3, 8)

plt.title('Specific impulse')
# plt.plot(hdpe_res['time'], hdpe_res['specific_impulse'], label='HDPE')
plt.plot(paraffin_res['time'], paraffin_res['specific_impulse'], label='Paraffin')
plt.xlabel('Time (s)')
plt.ylabel('Specific impulse (s)')

plt.savefig('./output/r2s_2026/hdpe.png', bbox_inches='tight')