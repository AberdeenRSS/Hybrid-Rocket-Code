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

    print(f'    Iterations: {i}')
    print(f'    Result data points {len(res)}')
    print(f'    Engine burn time: {engine.burn_time:.2f} s')
    print(f'    Total impulse: {total_impulse:.2f} Ns')
    print(f'    Engine specific impulse: {engine.average_ISP:.2f} s')
    print(f'    Oxidizer spent: {(engine.ox_initial_liquid_mass - engine.ox_tank_liquid_mass):.2f} kg')
    print(f'    Fuel spent {fuel_mass_spent:.2f} kg')

    return df, total_impulse, total_thrust

def add_ox_flux(df: pd.DataFrame):
    df['ox_flux'] = df['total_inflow']/(math.pi*df['centre_port_radius']**2) # kg/(s*m^2)


# Lin-lin liu et. al. own fit
# engine.regression_a = 0.00005480
# engine.regression_n = 0.47692
# engine.regression_m = 0

# # F3 sample: 90% Paraffin + 10% PE wax
# engine.regression_a = 0.0003526
# engine.regression_n = 0.537
# engine.regression_m = 0

# F5 sample: 80% Paraffin + 20% PE wax
# engine.regression_a = 0.000299
# engine.regression_n = 0.551
# engine.regression_m = 0

# B70 beeswax
# engine.regression_a = 0.000096
# engine.regression_n = 0.54
# engine.regression_m = 0

# Magic Paraffin + PE wax combination
# engine.regression_a = 0.00015
# engine.regression_n = 0.65
# engine.regression_m = 0

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
prepare_sim(engine, DT)
print('Simulating paraffin...')
weinstein_res, weinstein_total_impulse, weinstein_thrust = simulate(engine, MAX_ITERATIONS)
print(f'Paraffin I: {weinstein_total_impulse:.2f}Ns')
add_ox_flux(weinstein_res)

# Stanford/NASA Ames (claimed)
engine2 = Cengines()
engine2.load_prop('./data/L_Nitrous_S_Paraffin.propep', 'L_CUSTOM_S_CUSTOM')
assign_engine_parameters(engine2, engine_parameters)
set_engine_geometry(engine2)
engine2.solid_propellant_density = 900
engine2.regression_a = 0.000155
engine2.regression_n = 0.5
engine2.regression_m = 0
# engine2.charge_length = 0.4
# engine2.pre_comb_chamber_length = 0.13
prepare_sim(engine2, DT)
print('Simulating stanford claimed...')
stanford_res, stanford_total_impulse, stanford_thrust = simulate(engine2, MAX_ITERATIONS)
print(f'Paraffin I: {stanford_total_impulse:.2f}Ns')
add_ox_flux(stanford_res)

# stanford_c/NASA Ames (fitted)
engine3 = Cengines()
engine3.load_prop('./data/L_Nitrous_S_Paraffin.propep', 'L_CUSTOM_S_CUSTOM')
assign_engine_parameters(engine3, engine_parameters)
set_engine_geometry(engine3)
engine3.solid_propellant_density = 900
engine3.regression_a = 0.00021
engine3.regression_n = 0.5
engine3.regression_m = 0
# engine3.charge_length = 0.3
# engine3.pre_comb_chamber_length = 0.13
prepare_sim(engine3, DT)
print('Simulating stanford_c calculated...')
stanford_c_res, stanford_c_total_impulse, stanford_c_thrust = simulate(engine3, MAX_ITERATIONS)
print(f'Paraffin I: {stanford_c_total_impulse:.2f}Ns')
add_ox_flux(stanford_c_res)


def plot_series(df: pd.DataFrame, series_name: str, label: str, multiplier: float = 1, invert: bool = False):
    values = 1/(df[series_name]*multiplier) if invert else df[series_name]*multiplier
    plt.plot(df['time'], values, label=label)

series = [
    (weinstein_res, 'Shani Sisi et. al. '),
    (stanford_res, 'Anthony McCormick et. al.'),
    (stanford_c_res, 'Eric Dorian et. al. a=0.210mm/s n=0.5'),
]

plt.figure(figsize=(18,18))
plt.subplot(3, 3, 1)

plt.title('Ox mass flow rates')
for s, l in series:
    plot_series(s, 'nozzle_mass_flowrate', l)
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Mass flow (kg/s)')

plt.subplot(3, 3, 2)

plt.title('Thrust')
for s, l in series:
    plot_series(s, 'thrust', l)
plt.xlabel('Time (s)')
plt.ylabel('Force (N)')

plt.subplot(3, 3, 3)

plt.title('Chamber pressure')
for s, l in series:
    plot_series(s, 'chamber_pressure_bar', l)
plt.xlabel('Time (s)')
plt.ylabel('Pressure (bar)')

plt.subplot(3, 3, 4)

plt.title('Nozzile exit pressure')
for s, l in series:
    plot_series(s, 'nozzle_exit_pressure', l, 1/1e5)
plt.xlabel('Time (s)')
plt.ylabel('Pressure (bar)')

plt.subplot(3, 3, 5)

plt.title('Fuel grain hole size')
for s, l in series:
    plot_series(s, 'centre_port_radius', l, 1000)
plt.xlabel('Time (s)')
plt.ylabel('Radius (mm)')

plt.subplot(3, 3, 6)

plt.title('Oxygen remaining mass')
for s, l in series:
    plot_series(s, 'ox_tank_contents_mass', l)
plt.xlabel('Time (s)')
plt.ylabel('Ox mass (kg)')

plt.subplot(3, 3, 7)

plt.title('Oxidizer to fuel ratio')
for s, l in series:
    plot_series(s, 'fuel_to_ox_ratio', l, invert=True)
plt.xlabel('Time (s)')
plt.ylabel('O/F ratio')

plt.subplot(3, 3, 8)

plt.title('Specific impulse')
for s, l in series:
    plot_series(s, 'specific_impulse', l)
plt.xlabel('Time (s)')
plt.ylabel('Specific impulse (s)')

plt.subplot(3, 3, 9)

plt.title('Oxygen flux')
for s, l in series:
    plot_series(s, 'ox_flux', l)
plt.xlabel('Time (s)')
plt.ylabel('Flux (kg/(s m^2))')

plt.savefig('./output/r2s_2026/paraffin.png', bbox_inches='tight')