import math

import matplotlib.pyplot as plt

import numpy as np
from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer
from rocketcea.cea_obj_w_units import CEA_Obj
from scipy.cluster.hierarchy import average

## Input parameters
# System Properties
pressureRunTank = 50 # Pressure of the run tank in Bar
pressureDropInj = 0.3 # Pressure drop across injector as a percentage of total pressure
pressureAtmosphere = 101325 # Atmospheric pressure in Pa
thrustDesired = 500 # Desired thrust in Newtons
volOx = 3 # Amount of oxidiser in L
expRatio = 40 # Nozzle Expansion Area Ratio
radiusInitPort = 0.01 # Initial port Radius in M
volPre = 0.001 # Volume of pre combustion chamber in m^3
volPost = 0.001 # Volume of post combustion chamber in m^3
radiusThroat = 0.008 # radius of the nozzle throat in M

efficencyFeed= 1 # Efficency of oxidiser feed system
efficencyComb = 0.9 # Combustion Efficency
efficencyNoz = 1 # Nozzle efficency
coeffDis = 1 # Coefficent of discharge

R_u = 8.3145 # Universal gas constant

# Fuel Properties
rhoFuel = 924 # Density of fuel in kg/m^3
a_0 = 0.000155 # a_o value for propellant - oxidiser combo !!! be careful of a_o and a in given parameters, they are not the same
n = 0.5 # n value for propellant - oxidiser combo
lenFuel = 0.2 # Length of fuel grain in M

# Oxidiser Properties
rhoOx = 800 # Density of oxidiser in kg/m^3

# Create fuels and oxidisers for CEA
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

# Make CEA into useful units
cea_obj = CEA_Obj(propName='', oxName=oxidizer_name, fuelName=fuel_name, pressure_units='Bar', cstar_units='m/s',
                  temperature_units='K', sonic_velocity_units='m/s', enthalpy_units='J/kg', density_units='kg/m^3',
                  specific_heat_units='J/kg-K', viscosity_units='poise', thermal_cond_units='W/cm-degC')

## Design Calculations
mFuelDot = 0 # Sets inital mass flow rate of the fuel
timeStep = 0.001 # Sets the size of the time step used in the solution
radiusPort = radiusInitPort # Sets the inital port radius
presChamb = pressureAtmosphere # Sets the inital pressure
areaThroat = np.pi*radiusThroat**2
mOx = rhoOx*(volOx * 0.001)
moxInit = mOx
time = 0
i = 0
forcePlot = []
pressurePlot = []
oxPlot = []
ofPlot = []
portPlot = []
timePlot = []


## Looped Solution
while mOx > 0 :
    # Oxidiser Mass flow rate (can be a product of time)
    mOxDot = 0.3 # Oxidiser mass flow rate in Kg/s

    # Propellant Mass flow rate
    mPropDot = mOxDot + mFuelDot # Mass flow rate of the propellant (fuel and oxidiser)

    # calculate a value from a_0, not needed if given a directly
    a=a_0/math.pow((1+(mFuelDot/mOxDot)),n) # Eq 3.50

    # Regression Rate
    rDot = a*math.pow((mPropDot/(np.pi*(radiusPort*radiusPort))),n) # Eq 3.51, assuming m=0

    # Burning Area
    areaBurn = 2*np.pi*radiusPort*lenFuel

    # Calculate Fuel Mass Flow Rate
    mFuelDot = rhoFuel*areaBurn*rDot

    # Oxidiser fuel Ratio
    ratioO_F = mOxDot/mFuelDot # For simplicity, the O/f of the propellant being added to the combustion chamber at each time step is used.
    ofPlot.append(ratioO_F)

    # Chamber Volume
    volChamber = np.pi*(radiusPort**2)*lenFuel + volPre + volPost # Eq 3.78

    #CEA analasys
    outputCEA = cea_obj.get_IvacCstrTc_ChmMwGam(Pc=presChamb/100000, MR=ratioO_F, eps=expRatio)
    CF = outputCEA[0]
    CStar = outputCEA[1]
    tempChamb = outputCEA[2]
    massMol = outputCEA[3]
    gammaChamb = outputCEA[4]

    # Specific gas constant
    Cp = cea_obj.get_Chamber_Cp(Pc=presChamb/100000, MR=ratioO_F, eps=expRatio, frozen=0)
    Cv = Cp/gammaChamb
    R = Cp-Cv

    # Calculate mass leaving the chamber
    mOutDot = (((gammaChamb*coeffDis*areaThroat*presChamb)/(efficencyComb*math.sqrt(gammaChamb*R*tempChamb)))
                    *math.pow((2/(gammaChamb+1)),(gammaChamb+1)/(2*(gammaChamb-1)))) # Ee 3.73

    # Chamber Pressure Change
    dPresChambdt = ((R*tempChamb)/volChamber)*((areaBurn*rDot*(rhoFuel-(presChamb/(R*tempChamb)))) + mOxDot - mOutDot) # Eq 3.76

    # Calculate Thrust
    force = mOutDot*CStar*efficencyComb*coeffDis*efficencyNoz
    forcePlot.append(force)

    # Calculate new port radius
    radiusPort = radiusPort + rDot* timeStep
    portPlot.append(radiusPort)

    # Calculate new chamber pressure
    presChamb = presChamb + dPresChambdt*timeStep
    pressurePlot.append(presChamb/100000)

    # Calculate remaining oxidiser
    mOx = mOx - mOxDot * timeStep
    print("Oxidiser Mass remaining",mOx)
    oxPlot.append(mOx)

    time = time + timeStep
    timePlot.append(time)
    i = i + 1

plt.figure(figsize=(18,12))
plt.subplot(231)
plt.title('Pressure')
plt.plot(timePlot, pressurePlot)

plt.subplot(232)
plt.title('force')
plt.plot(timePlot, forcePlot)

plt.subplot(233)
plt.title('Oxidiser Mass')
plt.plot(timePlot, oxPlot)

plt.subplot(234)
plt.title('O/F ratio')
plt.plot(timePlot, ofPlot)

plt.subplot(235)
plt.title('Port Radius')
plt.plot(timePlot, portPlot)

#plt.show()


print("Maximum Pressure:", max(pressurePlot), "Bar")
print("Inital Port Diamater:", radiusInitPort*2*1000, "mm" )
print("Final Port Diamater:", radiusPort*2*1000, "mm")
print("Mass of Fuel Burned:", (np.pi*(radiusPort**2)-np.pi*(radiusInitPort**2)) * lenFuel * rhoFuel, "kg")
print("Mass of Oxidiser Burned:", moxInit, "kg")
print("Average O/F ratio:", sum(ofPlot)/len(ofPlot))
print("Burn Time", time, "Seconds")
