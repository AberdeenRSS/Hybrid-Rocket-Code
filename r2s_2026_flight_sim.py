
from dataclasses import dataclass
import math
import os
from typing import Callable
import numpy as np
import matplotlib.pyplot as plt
from common.basic_rocket_sim import RocketSim
from common.cira_atmosphere_model import CiraAtmosphereModel
from common.mach_corrected_drag import mjollnir_rocket_drag

OUT = 'output/r2s_2026'
T_FIRE_MAX_ = 60
T_MAX = 200
DT = 0.001

os.makedirs(f'./{OUT}', exist_ok=True)

cira_model = CiraAtmosphereModel()
cira_model.import_data('./data/atmosphere/cira_nhant.txt', 14)

LAT = 67 # (Aberdeen)

# Air density interpolated using cira at Aberdeen latitude
air_density_model = lambda h: cira_model.get_density_interpolated(h, LAT) 
air_temp_model = lambda h: cira_model.get_temp_interpolated(h, LAT)

drag_model = lambda M: mjollnir_rocket_drag(M)*1.2

def make_dynamic_thrust_model(max_throttle, throttle_percentage, throttle_height):
    def dynamic_thrust_model(v: tuple[float, float, float, float, float]):

        if v[1] < 6000:
            # Throttle down approaching mach 1
            return max_throttle*math.exp(-v[4])
        
        return max_throttle
    
    return dynamic_thrust_model

rocket_radius = 0.08

rocket_cross_section = math.pi*rocket_radius**2
    
rocket_no_throttle = RocketSim(20, 22, 213, 3500, rocket_cross_section, drag_model, air_temp_model, air_density_model)
no_throttle_result = rocket_no_throttle.simulate_to_impact(0.01)

# rocket_throttle = RocketSim(20, 25, 220, make_dynamic_thrust_model(2000, 0.6, 10000), rocket_cross_section, drag_model, air_temp_model, air_density_model)
# throttle_result = rocket_throttle.simulate_to_impact(0.01)

print(f'Max altitude: {np.max(np.array(no_throttle_result[:, 1]))}')

plt.figure(figsize=(12, 8))

ax = plt.subplot(2, 2, 1)
plt.plot(no_throttle_result[:, 0],no_throttle_result[:, 1]/1000, label='No throttle')
# plt.plot(throttle_result[:, 0],throttle_result[:, 1]/1000, label='Throttle')
plt.xlabel('Time (s)')
plt.ylabel('Altitude (km)')
plt.xlim(0, T_MAX)
# plt.legend()

ax = plt.subplot(2, 2, 2)
plt.plot(no_throttle_result[:, 0], no_throttle_result[:, 2])
# plt.plot(throttle_result[:, 0], throttle_result[:, 2])
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.xlim(0, T_MAX)

ax = plt.subplot(2, 2, 3)
plt.plot(no_throttle_result[:, 0], no_throttle_result[:, 3])
# plt.plot(throttle_result[:, 0], throttle_result[:, 3])
plt.xlabel('Time (s)')
plt.ylabel('Mass (kg)')
plt.xlim(0, T_FIRE_MAX_)


ax = plt.subplot(2, 2, 4)
plt.plot(no_throttle_result[:, 0], no_throttle_result[:, 4])
# plt.plot(throttle_result[:, 0], throttle_result[:, 4])
# plt.ylim((0, np.max(throttle_result[:, 4])*1.2))
plt.xlabel('Time (s)')
plt.ylabel('Thrust (N)')
plt.xlim(0, T_FIRE_MAX_)


plt.savefig(f'./{OUT}/r2s_paraffin.png', dpi=300)

# h = np.linspace(0, 100, 300)
# density = cira_model.get_pressure_interpolated(h)

# plt.plot(h, density)
# plt.show()

# thrust_values = np.linspace(700, 6000, 15)
# altitudes = np.zeros(15)
# altitudes_throttled = np.zeros(15)
# i = 0

# for thrust in thrust_values:

#     rocket_no_throttle = RocketSim(10, 15, 200, thrust, 2*math.pi*0.1**2, 0.7, air_density_model)
#     no_throttle_result = rocket_no_throttle.simulate_to_impact(0.01)
#     max_alt = np.max(no_throttle_result[:, 1])
#     altitudes[i] = max_alt

#     rocket_throttle = RocketSim(10, 15, 200, make_dynamic_thrust_model(thrust, 0.6, 10000), 2*math.pi*0.1**2, 0.7, air_density_model)
#     throttle_result = rocket_throttle.simulate_to_impact(0.01)
#     max_alt = np.max(throttle_result[:, 1])
#     altitudes_throttled[i] = max_alt

#     i = i+1

# plt.plot(thrust_values/1000, altitudes/1000, label="No throttling")
# plt.plot(thrust_values/1000, altitudes_throttled/1000, label="Throttling")

# plt.xlabel('Thrust (kN)')
# plt.ylabel('Apogee (km)')

# plt.show()

