import math
import numpy as np
from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer
from rocketcea.cea_obj_w_units import CEA_Obj


## Input parameters
# System Properties
o_fRatio = 7 # Ratio of fuel to oxidiser (1:x) in terms of mass
runTankPressure = 50 # Pressure of the run tank in Bar
injPressureDrop = 0.3 # Pressure drop accross injector as a percentage of total pressure
portRatio = 2 # Ratio of inital and final port Diamiters (Df/Di)
desiredThrust = 50 # Desired thrust in Newtons
oxVol = 0.2 # Amount of oxidiser in L
expRatio = 40 # Nozzle Expansion Area Ratio

oxSystemEfficency = 1 # Efficency of oxidiser feed system
combustionEfficency = 0.9 # Combustion Efficency
nozEfficency = 1 # Nozzle efficency
coeffDis = 1 # Coefficent of discharge

# Fuel Properties
rhoFuel = 924 # Density of fuel in kg/m^3
a = 0.000155 # a_o value for propellent - oxidiser combo
n = 0.5 # n value for propellent - oxidiser combo

# Oxidiser Properties
rhoOx = 800 # Density of oxidiser in kg/m^3


## Calculate derived values
# Calculate mass of Oxidiser
oxMass = (oxVol/1000) * rhoOx
print("Oxidiser Mass(Kg) =", oxMass)


# Calculate mass of fuel
fuelMass = oxMass/o_fRatio
print("Fuel Mass(Kg) =", fuelMass)

# Calculate chamber pressure
cmbrPressure = runTankPressure * ((1-injPressureDrop)-(1-oxSystemEfficency))


## CEA Analasys
'''
-- OLD values --
print("Perform CEA analasys of Nitrous and paraffin with O/F = 1:",o_fRatio, " and pressure =", cmbrPressure)
print("Input results at Throat (Default values for Nitrous - Paraffin at 40bar and O/F of 7)")
throatPressure = float(input("Pressure at throat (P,BAR) = ").strip() or 22.914) * 100000 # Converts to SI unit (Pascal)
throatTemprature = float(input("Temperature at throat (T, K) = ").strip() or 3139.88)
molMass = float(input("Molar Mass (M,(1/n)) = ").strip() or 26.58)
throatGamma = float(input("Gamma at Throat = ").strip() or 1.1573)
CSTAR = float(input("CSTAR = ").strip() or 1608.2)
CF = float(input("CF = ").strip() or 0.6630)
ISP = float(input("ISP = ").strip() or 1066.2)
'''

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

isp = cea_obj.get_Isp(Pc=cmbrPressure, MR=7, eps=40)

#throatPressure = cea_obj.get_PcOvPe(Pc=cmbrPressure, MR=o_fRatio, eps=expRatio, frozen=0, frozenAtThroat=1) # Converts to SI unit (Pascal)
throatTemprature = cea_obj.get_IvacCstrTc_ChmMwGam(Pc=cmbrPressure, MR=o_fRatio, eps=expRatio)[2]
molMass = cea_obj.get_IvacCstrTc_ChmMwGam(Pc=cmbrPressure, MR=o_fRatio, eps=expRatio)[3]
throatGamma = cea_obj.get_IvacCstrTc_ChmMwGam(Pc=cmbrPressure, MR=o_fRatio, eps=expRatio)[4]
CSTAR = cea_obj.get_IvacCstrTc_ChmMwGam(Pc=cmbrPressure, MR=o_fRatio, eps=expRatio)[1]
CF = cea_obj.get_PambCf(Pamb=1.013, Pc=cmbrPressure, MR=o_fRatio, eps=expRatio)[0]
ISP = cea_obj.estimate_Ambient_Isp(Pc=cmbrPressure, MR=o_fRatio, eps=expRatio, Pamb=1.013, frozen=0, frozenAtThroat=1)

print("Inputted data:  P =",cmbrPressure, " T =", throatTemprature, "  Moler Mass =", molMass, "  Gamma =", throatGamma, "  C* =", CSTAR, "  CF =",CF)

## Calculate engine parameters
# Calculate throat Area
throatArea = desiredThrust / (CF * cmbrPressure * 10000 * nozEfficency * coeffDis) # Eq 7.14
throatDiamater = math.sqrt(throatArea/np.pi) * 2
print("Throat Diamater (M) =", throatDiamater)

# Calculate propellent mass flow rate
propellentMassFlow = (cmbrPressure * 10000 * coeffDis * throatArea) / (combustionEfficency * CSTAR) #eq 7.15
print("Total Mass Flow Rate (Kg/s) =", propellentMassFlow)

# Oxidiser mass flow rate
oxMassFlow = propellentMassFlow * (o_fRatio/(1+o_fRatio)) # Eq 7.12
print("Oxidiser Mass Flow Rate (Kg/s) =", oxMassFlow)

# Calculate Burn Time
burnTime = oxMass/oxMassFlow # Eq 7.18
print("Burn Time (s) =", burnTime)

# Calculate Fuel Dimensions
j = 2*n + 1

diaFinalFuel = math.pow((((math.pow(j*2,j)*a)/(math.pow(np.pi,n)))*((math.pow(oxMassFlow,n) * burnTime)/(1-math.pow(1/portRatio,j)))),(1/j)) #Eq 7.26
print("Fuel Outside Diamiter(M) =", diaFinalFuel)

diaInitFuel = diaFinalFuel/portRatio
print("Fuel inside Diamiter(M) =", diaInitFuel) # Eq 7.27

lenFuel = (4*fuelMass)/(np.pi*rhoFuel*(math.pow(diaFinalFuel,2)-math.pow(diaInitFuel,2))) # eq 7.29
print("Fuel Grain Length (M) =", lenFuel)

