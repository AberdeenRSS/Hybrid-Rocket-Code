
from dataclasses import dataclass
import math
from typing import Callable
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class RocketSim():

    dry_mass: float

    fuel_mass: float

    isp: float

    thrust: float | Callable[[tuple], float]

    rocket_cross_section: float

    coefficient_of_drag: float

    air_density: Callable[[float], float]

    def simulate_step(self, dt, t, pos_old, v_old, m_old):

        fuel_left = m_old > self.dry_mass

        thrust = self.thrust((t, pos_old, v_old, m_old)) if callable(self.thrust) else self.thrust

        if not fuel_left:
            thrust = 0

        # calculate change in mass from isp and current thrust
        m_dot = thrust / (self.isp * 10) 

        # Subtract g
        acceleration = -9.8 

        # Apply acceleration from thrust
        # if there is fuel left
        if fuel_left:
            acceleration += thrust / m_old

        air_density = self.air_density(pos_old)

        # Apply air resistance
        drag = 1/2 * air_density * v_old * v_old * self.coefficient_of_drag * self.rocket_cross_section

        acceleration += -drag/m_old if v_old > 0 else drag/m_old

        v = v_old + acceleration*dt
        pos = pos_old + v*dt
        m = m_old-m_dot*dt
        t = t + dt

        return t, pos, v, m, thrust
    
    def simulate_to_impact(self, dt = 0.001):

        times = list()
        positions = list()
        velocities = list()
        masses = list()
        thrusts = list()

        t = 0
        pos = 0.0001
        v = 0
        m = self.dry_mass + self.fuel_mass

        while pos > 0:
            times.append(t)
            positions.append(pos)
            velocities.append(v)
            masses.append(m)
            t, pos, v, m, thrust = self.simulate_step(dt, t, pos, v, m)
            thrusts.append(thrust)

        return np.column_stack([np.array(times), np.array(positions), np.array(velocities),np.array( masses), np.array(thrusts)])

class CiraAtmosphereModel():
    '''
    Assumes cira data from https://data.ceda.ac.uk/badc/cira/data/
    '''

    def import_data(self, file_location: str, line: int, max_rows=None):

        self.data = np.loadtxt(file_location, skiprows=line, ndmin=2, max_rows=max_rows)

    def get_pressure_interpolated(self, h):

        if self.data is None:
            raise Exception("Data not imported yet")
        
        return np.interp(h/1000, np.flip(self.data[:, 2]), np.flip(self.data[:, 1]))
    
    def get_temp_interpolated(self, h, lat):

        if self.data is None:
            raise Exception("Data not imported yet")
        
        lat_i = math.floor(lat/5)

        if lat_i > 18:
            lat_i = 18
        
        return np.interp(h/1000, np.flip(self.data[:, 2]), np.flip(self.data[:, 3 + lat_i]))
    
    def get_density_interpolated(self, h, lat):

        if self.data is None:
            raise Exception("Data not imported yet")
        
        M_Air = 0.0289647 #kg/mol
        R = 8.314
        
        p = self.get_pressure_interpolated(h)
        T = self.get_temp_interpolated(h, lat)

        return p * M_Air/ (R * T)

cira_model = CiraAtmosphereModel()
cira_model.import_data('./data/atmosphere/cira_nhant.txt', 14)

# Air density interpolated using cira at Aberdeen latitude
air_density_model = lambda h: cira_model.get_density_interpolated(h, 67) 

def make_dynamic_thrust_model(max_throttle, throttle_percentage, throttle_height):
    def dynamic_thrust_model(v: tuple[float, float, float, float]):

        if v[1] < 500:
            return max_throttle
        
        if v[1] < throttle_height:
            return max_throttle*throttle_percentage
        
        return max_throttle
    
    return dynamic_thrust_model
    
rocket_no_throttle = RocketSim(15, 20, 200, 1500, 2*math.pi*0.1**2, 0.7, air_density_model)
no_throttle_result = rocket_no_throttle.simulate_to_impact(0.01)

rocket_throttle = RocketSim(15, 20, 200, make_dynamic_thrust_model(1500, 0.6, 10000), 2*math.pi*0.1**2, 0.7, air_density_model)
throttle_result = rocket_throttle.simulate_to_impact(0.01)

print(f'Max altitude: {np.max(np.array(no_throttle_result[:, 1]))}')

plt.figure(figsize=(12, 8))

ax = plt.subplot(2, 2, 1)
plt.plot(no_throttle_result[:, 0],no_throttle_result[:, 1]/1000, label='No throttle')
plt.plot(throttle_result[:, 0],throttle_result[:, 1]/1000, label='Throttle')

plt.xlabel('Time (s)')
plt.ylabel('Altitude (km)')
plt.legend()

ax = plt.subplot(2, 2, 2)
plt.plot(no_throttle_result[:, 0], no_throttle_result[:, 2])
plt.plot(throttle_result[:, 0], throttle_result[:, 2])
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')

ax = plt.subplot(2, 2, 3)
plt.plot(no_throttle_result[:, 0], no_throttle_result[:, 3])
plt.plot(throttle_result[:, 0], throttle_result[:, 3])
plt.xlabel('Time (s)')
plt.ylabel('Mass (kg)')

ax = plt.subplot(2, 2, 4)
plt.plot(no_throttle_result[:, 0], no_throttle_result[:, 4])
plt.plot(throttle_result[:, 0], throttle_result[:, 4])
plt.ylim((0, np.max(throttle_result[:, 4])*1.2))
plt.xlabel('Time (s)')
plt.ylabel('Thrust (N)')

plt.savefig('./throttle_comparison.png', dpi=300)

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

