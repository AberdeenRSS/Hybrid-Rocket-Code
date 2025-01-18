
import rocketcea
from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer
from rocketcea.cea_obj_w_units import CEA_Obj

card_str = """
fuel paraffin   C 32 H 66   wt%=100
h,cal=-224200     t(k)=298.15   rho=.924
"""
add_new_fuel( 'paraffin', card_str )

card_str = """
oxid N20   N 2 O 1   wt%=100
h,cal=15500     t(k)=298.15    rho=1.226
"""
add_new_oxidizer( 'N20', card_str )

fuel_name = 'paraffin'
oxidizer_name = 'N20'

cea_obj = CEA_Obj(propName='', oxName=oxidizer_name, fuelName=fuel_name, pressure_units='Bar', cstar_units='m/s',
                  temperature_units='K', sonic_velocity_units='m/s', enthalpy_units='J/kg', density_units='kg/m^3',
                  specific_heat_units='J/kg-K', viscosity_units='poise', thermal_cond_units='W/cm-degC')

isp = cea_obj.get_Isp(Pc=1000, MR=7, eps=40)
print(f'Specific Impulse (Isp): {isp} seconds')
