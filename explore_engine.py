import math
import nitrous_engine_sim
from nitrous_engine_sim import assign_engine_parameters, read_engine_file
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nitrous_engine_sim.result_helper import get_running_results

def add_colorbar(z_values, cmap, label):
    ax = plt.gca()
    ax.inset_axes([0.95, 0.1, 0.05, 0.8])
    ax.cla()

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min(v for v in z_values if not math.isnan(v)), vmax=max(v for v in z_values if not math.isnan(v))))
    clbr = plt.colorbar(sm, ax=ax)

    clbr.ax.set_ylabel(label)

engine_parameters = read_engine_file('data/aberdeen_r2s.engine')
res = 100
orifice_radii = np.linspace(0.0002, 0.0025, res)
nozzle_radii = np.linspace(.002, .009, res)

thrust = np.zeros(res*res)
isp = np.zeros(res*res)
impulse = np.zeros(res*res)
ox_usage = np.zeros(res*res)


j = 0

for orifice_r in orifice_radii:
    for nozzle_r in nozzle_radii:

        # Load a default engine to start with
        engine = nitrous_engine_sim.Cengines()
        nitrous_engine_sim.load_default_prop(engine, 'L_Nitrous_S_HDPE')
        assign_engine_parameters(engine, engine_parameters)

        # 4 ox orifices
        engine.ox_orifice_diameter = orifice_r*2
        engine.nozzle_throat_diameter = nozzle_r*2

        # Prepare sim
        engine.delta_time = 0.01
        engine.burn_status = 0
        engine.initialize_engine()
        engine.burn_status = 1
        engine.ignition = True
        engine.surpress_mixture_out_of_range = True


        MAX_ITERATIONS = 200000
        i = 0
        last_fault = 0
        total_impulse = 0
        total_thrust = 0
        ox_initial = engine.ox_tank_contents_mass

        while engine.burn_status == 1 and i < MAX_ITERATIONS:

            engine.simulate_engine()

            total_impulse += engine.thrust*engine.delta_time

            # if engine._fault != last_fault:
            #     if engine._fault > 0:
            #         print(f'New engine fault at {engine.burn_time:.3f}s: {nitrous_engine_sim.get_error_msg(engine._fault)}')
            #     else:
            #         print(f'All faults cleared at {engine.burn_time:.3f}s')
            #     last_fault = engine._fault

            total_thrust += engine.thrust
            i += 1

            if math.isnan(total_thrust):
                break

        avg_thrust = total_thrust/i

        if math.isnan(total_thrust):
            thrust[j] = float('nan') 
            impulse[j] = float('nan') 
            isp[j] = float('nan') 
            ox_usage[j] = float('nan') 
        else:
            thrust[j] = avg_thrust 
            impulse[j] = total_impulse
            isp[j] = engine.average_ISP
            ox_usage[j] = ox_initial - engine.ox_tank_contents_mass

        j += 1


thrust_reshape = thrust.reshape(res, res)
isp_reshape = isp.reshape(res, res)
impulse_reshape = impulse.reshape(res, res)
ox_usage_reshape = ox_usage.reshape(res, res)


plt.figure(figsize=(18,18))

plt.subplot(2, 2, 1)
add_colorbar(thrust, 'plasma', 'Thrust (N)')
plt.contourf(orifice_radii*1000, nozzle_radii*1000, thrust_reshape, 100, cmap='plasma')
plt.xlabel('Ox Orifice radius (mm)')
plt.ylabel('Nozzle Throat radius (mm)')

plt.subplot(2, 2, 2)
add_colorbar(isp, 'cool', 'Isp (s)')
plt.contourf(orifice_radii*1000, nozzle_radii*1000, isp_reshape, 100, cmap='cool')
plt.xlabel('Ox Orifice radius (mm)')
plt.ylabel('Nozzle Throat radius (mm)')

plt.subplot(2, 2, 3)
add_colorbar(impulse, 'Wistia', 'Total impulse (Ns)')
plt.contourf(orifice_radii*1000, nozzle_radii*1000, impulse_reshape, 100, cmap='Wistia')
plt.xlabel('Ox Orifice radius (mm)')
plt.ylabel('Nozzle Throat radius (mm)')

plt.subplot(2, 2, 4)
add_colorbar(ox_usage, 'summer', 'Ox usage (kg)')
plt.contourf(orifice_radii*1000, nozzle_radii*1000, ox_usage_reshape, 100, cmap='summer')
plt.xlabel('Ox Orifice radius (mm)')
plt.ylabel('Nozzle Throat radius (mm)')

plt.show()

