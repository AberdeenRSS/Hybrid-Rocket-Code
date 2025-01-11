import rocketcea
from rocketcea.cea_obj import CEA_Obj

fuel_name = 'C32H66'
oxidizer_name = 'O2'

cea_obj = CEA_Obj(propName='', oxName=oxidizer_name, fuelName=fuel_name)

isp = cea_obj.get_Isp(Pc=1000, MR=2.5, eps=40)
print(f'Specific Impulse (Isp): {isp} seconds')
