import math
import nitrous_engine_sim
from nitrous_engine_sim import assign_engine_parameters, load_default_prop, Cengines
from nitrous_engine_sim.engine_file_reader import read_engine_file
from nitrous_engine_sim.result_helper import get_running_results
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

MAX_ITERATIONS = 200000
DT = 0.001

engine_parameters = read_engine_file('data/aberdeen_r2s.engine')

def set_engine_geometry(engine):
    engine.ox_initial_tank_pressure_bar = 62.5
    engine.ox_tank_volume = 30/1000
    engine.ox_initial_temp_C = 20
    engine.ox_orifice_number = 30
    engine.ox_orifice_diameter = 0.0007*2

    engine.ox_feed_model = 1;

    engine.fuel_orifice_number = 0

    engine.charge_length = 0.28
    engine.charge_radius = 0.13665/2
    # engine.charge_radius = 0.0993/2

    engine.centre_port_radius = 0.02
    engine.port_max_radius = engine.charge_radius

    engine.pre_comb_chamber_length = 0.25
    engine.post_comb_chamber_length = 0.15

    engine.nozzle_efficiency = 1
    engine.nozzle_throat_rdot = 0
    engine.nozzle_area_ratio = 6
    engine.nozzle_throat_diameter = 0.011*2

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

    return df, total_impulse, total_thrust

charge_len = np.linspace(0.15, 0.5, 40)
isp_shani = list()
isp_stanford = list()
isp_stanford_c = list()


for l in charge_len:

    # Pure Paraffin 
    # Shani Sisi et. al. 
    engine = Cengines()
    engine.load_prop('./data/L_Nitrous_S_Paraffin.propep', 'L_CUSTOM_S_CUSTOM')
    assign_engine_parameters(engine, engine_parameters)
    set_engine_geometry(engine)

    engine.solid_propellant_density = 900
    engine.regression_a = 0.000104 
    engine.regression_n = 0.67
    engine.regression_m = 0

    engine.charge_length = l
    engine.pre_comb_chamber_length = 0.6 - l

    prepare_sim(engine, DT)
    res, impulse, thrust = simulate(engine, MAX_ITERATIONS)

    isp_shani.append(engine.average_ISP)


    # --------

    engine2 = Cengines()
    engine2.load_prop('./data/L_Nitrous_S_Paraffin.propep', 'L_CUSTOM_S_CUSTOM')
    assign_engine_parameters(engine2, engine_parameters)
    set_engine_geometry(engine2)

    engine2.solid_propellant_density = 900
    engine2.regression_a = 0.000155
    engine2.regression_n = 0.5
    engine2.regression_m = 0

    engine2.charge_length = l
    engine2.pre_comb_chamber_length = 0.6 - l

    prepare_sim(engine2, DT)
    res, impulse, thrust = simulate(engine2, MAX_ITERATIONS)

    isp_stanford.append(engine2.average_ISP)

    # --------

    engine3 = Cengines()
    engine3.load_prop('./data/L_Nitrous_S_Paraffin.propep', 'L_CUSTOM_S_CUSTOM')
    assign_engine_parameters(engine3, engine_parameters)
    set_engine_geometry(engine3)

    engine3.solid_propellant_density = 900
    engine3.regression_a = 0.00021
    engine3.regression_n = 0.5
    engine3.regression_m = 0

    engine3.charge_length = l
    engine3.pre_comb_chamber_length = 0.6 - l

    prepare_sim(engine3, DT)
    res, impulse, thrust = simulate(engine3, MAX_ITERATIONS)

    isp_stanford_c.append(engine3.average_ISP)

plt.plot(charge_len*1000, isp_shani, label='Shani Sisi & Alon Gany (a=0.104mm/s n=0.67)')
plt.plot(charge_len*1000, isp_stanford, label='Anthony McCormick et. al. (a=0.155mm/s n=0.5)')
plt.plot(charge_len*1000, isp_stanford_c, label='Shani Sisi & Alon Gany (a=0.210mm/s n=0.5)')

plt.xlabel('Fuel grain length (mm)')
plt.ylabel('Isp (s)')
plt.legend()

plt.savefig('./output/r2s_2026/shani_length_opt', bbox_inches='tight')
