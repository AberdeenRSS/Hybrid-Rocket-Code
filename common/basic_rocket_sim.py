
from dataclasses import dataclass
import math
from typing import Callable
import numpy as np

R = 8.314472
M_air = 0.0289647 #kg/mol
R_air = R/M_air
gamma_air = 1.4

@dataclass
class RocketSim():

    dry_mass: float

    fuel_mass: float

    isp: float

    thrust: float | Callable[[tuple], float]

    rocket_cross_section: float

    coefficient_of_drag: float | Callable[[float], float]
    '''
    Drag coefficient. Expects constant value or function returning cd for
    at a specific mach number M
    '''

    air_temperature: float | Callable[[float], float]
    '''
    Air temperature. Expects constant value or function returning cd for
    at an altitude h
    '''

    air_density: Callable[[float], float]


    def simulate_step(self, dt, t, pos_old, v_old, m_old, mach_number):

        fuel_left = m_old > self.dry_mass

        thrust = self.thrust((t, pos_old, v_old, m_old, mach_number)) if callable(self.thrust) else self.thrust

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

        temp = self.air_temperature(pos_old) if callable(self.air_temperature) else self.air_temperature

        speed_of_sound = math.sqrt(gamma_air*R_air*temp)

        mach_number = v_old/speed_of_sound

        cd = self.coefficient_of_drag(mach_number) if callable(self.coefficient_of_drag) else self.coefficient_of_drag 

        # Apply air resistance
        drag = 1/2 * air_density * v_old * v_old * cd * self.rocket_cross_section

        acceleration += -drag/m_old if v_old > 0 else drag/m_old

        v = v_old + acceleration*dt
        pos = pos_old + v*dt
        m = m_old-m_dot*dt
        t = t + dt

        return t, pos, v, m, thrust, mach_number
    
    def simulate_to_impact(self, dt = 0.001):

        times = list()
        positions = list()
        velocities = list()
        masses = list()
        thrusts = list()
        mach_numbers = list()


        t = 0
        pos = 0.0001
        v = 0
        m = self.dry_mass + self.fuel_mass
        mach_number = 0

        while pos > 0:
            times.append(t)
            positions.append(pos)
            velocities.append(v)
            masses.append(m)
            t, pos, v, m, thrust, mach_number = self.simulate_step(dt, t, pos, v, m, mach_number)
            thrusts.append(thrust)

        return np.column_stack([np.array(times), np.array(positions), np.array(velocities),np.array( masses), np.array(thrusts)])
